from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.core.kafka_events import send_event
from app.core.kafka_metrics import kafka_metrics_consumer

router = APIRouter()


@router.get("/test-kafka")
def test_kafka(request: Request) -> dict[str, Any]:
    user = getattr(request.state, "user", {}) or {}
    test_event = {
        "tipo": "cliente_creado",
        "clienteId": "mock-12345",
        "usuario": user.get("preferred_username") or user.get("sub") or "desconocido",
    }

    try:
        send_event("seguridad.accesos", test_event)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"No se pudo enviar el evento a Kafka: {exc}",
        ) from exc

    return {
        "status": "success",
        "message": "Evento cliente_creado enviado a Kafka exitosamente",
        "event": test_event,
    }


@router.get("/metrics")
def kafka_metrics() -> dict[str, Any]:
    snapshot = kafka_metrics_consumer.snapshot()
    metrics = snapshot.get("metrics", {})
    events_processed = metrics.get("events_processed", 0)
    events_by_type = metrics.get("events_by_type", {})

    return {
        "totalEventos": events_processed,
        "descripcion": "Eventos registrados en Kafka para monitoreo de accesos y acciones del sistema",
        "eventosPorTipo": events_by_type,
        "ultimaActualizacion": metrics.get("last_event_at"),
        "enabled": snapshot.get("enabled", False),
        "running": snapshot.get("running", False),
        "topics": snapshot.get("topics", []),
    }
