import json
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from app.core.config import get_settings

try:
    from kafka import KafkaProducer
except Exception:
    KafkaProducer = None


settings = get_settings()


def build_topic_name(topic_suffix: str) -> str:
    prefix = settings.KAFKA_TOPIC_PREFIX.strip(".")
    suffix = topic_suffix.strip(".")
    return f"{prefix}.{suffix}" if prefix else suffix


class KafkaEventPublisher:
    def __init__(self) -> None:
        self._lock = Lock()
        self._producer = None
        self._enabled = bool(settings.KAFKA_ENABLED) and KafkaProducer is not None

    def _get_bootstrap_servers(self) -> list[str]:
        return [value.strip() for value in settings.KAFKA_BOOTSTRAP_SERVERS.split(",") if value.strip()]

    def _get_or_create_producer(self):
        if not self._enabled:
            return None

        if self._producer:
            return self._producer

        with self._lock:
            if self._producer:
                return self._producer

            self._producer = KafkaProducer(
                bootstrap_servers=self._get_bootstrap_servers(),
                client_id=settings.KAFKA_CLIENT_ID,
                value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
            )
            return self._producer

    def publish(self, topic: str, event_type: str, payload: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        producer = self._get_or_create_producer()
        if not producer:
            raise RuntimeError("Kafka producer no disponible")

        event = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
            "metadata": metadata or {},
        }

        try:
            future = producer.send(topic, value=event)
            future.get(timeout=10)
            producer.flush()
        except Exception as exc:
            print(f"Error publicando evento en Kafka ({topic}): {exc}")
            raise

    def send_event(self, topic: str, event: dict[str, Any]) -> None:
        producer = self._get_or_create_producer()
        if not producer:
            raise RuntimeError("Kafka producer no disponible")

        event_with_timestamp = {
            **event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            future = producer.send(topic, value=event_with_timestamp)
            future.get(timeout=10)
            producer.flush()
        except Exception as exc:
            print(f"Error enviando evento a Kafka ({topic}): {exc}")
            raise

    def close(self) -> None:
        if self._producer:
            try:
                self._producer.flush()
                self._producer.close()
            except Exception:
                pass
            finally:
                self._producer = None


event_publisher = KafkaEventPublisher()


def publish_domain_event(topic_suffix: str, event_type: str, payload: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
    topic_name = build_topic_name(topic_suffix)
    event_publisher.publish(topic_name, event_type=event_type, payload=payload, metadata=metadata)


def send_event(topic: str, event: dict[str, Any]) -> None:
    event_publisher.send_event(topic, event)
