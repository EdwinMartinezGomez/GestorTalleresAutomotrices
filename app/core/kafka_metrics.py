import json
from collections import defaultdict
from datetime import datetime, timezone
from threading import Event, Lock, Thread
from typing import Any

from app.core.config import get_settings
from app.core.kafka_events import build_topic_name

try:
    from kafka import KafkaConsumer
except Exception:
    KafkaConsumer = None


settings = get_settings()


class KafkaMetricsStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._last_event_at: str | None = None
        self._events_processed = 0
        self._events_by_topic: dict[str, int] = defaultdict(int)
        self._events_by_type: dict[str, int] = defaultdict(int)
        self._errors = 0

    def add_event(self, topic: str, event_type: str) -> None:
        with self._lock:
            self._events_processed += 1
            self._events_by_topic[topic] += 1
            self._events_by_type[event_type] += 1
            self._last_event_at = datetime.now(timezone.utc).isoformat()

    def add_error(self) -> None:
        with self._lock:
            self._errors += 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "started_at": self._started_at,
                "last_event_at": self._last_event_at,
                "events_processed": self._events_processed,
                "events_by_topic": dict(self._events_by_topic),
                "events_by_type": dict(self._events_by_type),
                "errors": self._errors,
            }


class KafkaMetricsConsumer:
    def __init__(self) -> None:
        self._enabled = bool(settings.KAFKA_ENABLED and settings.KAFKA_METRICS_ENABLED and KafkaConsumer is not None)
        self._store = KafkaMetricsStore()
        self._topics = [
            "seguridad.accesos",
            build_topic_name("auth"),
            build_topic_name("clientes"),
            build_topic_name("inventario"),
            build_topic_name("ordenes"),
            build_topic_name("pagos"),
        ]
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._running = False
        self._consumer = None

    def _get_bootstrap_servers(self) -> list[str]:
        return [value.strip() for value in settings.KAFKA_BOOTSTRAP_SERVERS.split(",") if value.strip()]

    def start(self) -> None:
        if not self._enabled or self._running:
            return

        self._stop_event.clear()
        self._thread = Thread(target=self._run, daemon=True, name="kafka-metrics-consumer")
        self._thread.start()
        self._running = True

    def _run(self) -> None:
        try:
            self._consumer = KafkaConsumer(
                *self._topics,
                bootstrap_servers=self._get_bootstrap_servers(),
                group_id=settings.KAFKA_METRICS_CONSUMER_GROUP,
                enable_auto_commit=True,
                auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                value_deserializer=lambda value: json.loads(value.decode("utf-8")),
                consumer_timeout_ms=1000,
            )

            while not self._stop_event.is_set():
                messages = self._consumer.poll(timeout_ms=1000, max_records=200)
                for records in messages.values():
                    for message in records:
                        try:
                            body = message.value if isinstance(message.value, dict) else {}
                            event_type = str(body.get("event_type") or body.get("tipo") or "desconocido")
                            self._store.add_event(message.topic, event_type)
                        except Exception:
                            self._store.add_error()
        except Exception as exc:
            self._store.add_error()
            print(f"No se pudo iniciar consumidor de metricas Kafka: {exc}")
        finally:
            if self._consumer:
                try:
                    self._consumer.close()
                except Exception:
                    pass
            self._running = False

    def stop(self) -> None:
        if not self._running:
            return

        self._stop_event.set()

        if self._consumer:
            try:
                self._consumer.close()
            except Exception:
                pass

        if self._thread:
            self._thread.join(timeout=2)

        self._running = False

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "running": self._running,
            "topics": self._topics,
            "metrics": self._store.snapshot(),
        }


kafka_metrics_consumer = KafkaMetricsConsumer()
