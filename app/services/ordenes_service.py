from fastapi import HTTPException, status

from app.core.kafka_events import publish_domain_event
from app.repositories.ordenes_repository import OrdenesRepository


class OrdenesService:
    def __init__(self, repository: OrdenesRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def get(self, orden_id: int):
        orden = self.repository.get(orden_id)
        if not orden:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden no encontrada")
        return orden

    def create(self, payload: dict):
        orden = self.repository.create(payload)
        publish_domain_event(
            topic_suffix="ordenes",
            event_type="orden_creada",
            payload={
                "orden_id": orden.id,
                "placa_vehiculo": orden.placa_vehiculo,
                "estado": orden.estado,
            },
        )
        return orden

    def update(self, orden_id: int, payload: dict):
        orden = self.get(orden_id)
        updated = self.repository.update(orden, payload)
        publish_domain_event(
            topic_suffix="ordenes",
            event_type="orden_actualizada",
            payload={
                "orden_id": updated.id,
                "estado": updated.estado,
                "campos_actualizados": list(payload.keys()),
            },
        )
        return updated

    def delete(self, orden_id: int):
        orden = self.get(orden_id)
        self.repository.delete(orden)
        publish_domain_event(
            topic_suffix="ordenes",
            event_type="orden_eliminada",
            payload={"orden_id": orden_id},
        )

    def add_repuesto(self, payload: dict):
        self.get(payload["orden_id"])
        orden_repuesto = self.repository.add_repuesto(payload)
        publish_domain_event(
            topic_suffix="ordenes",
            event_type="orden_repuesto_agregado",
            payload={
                "orden_repuesto_id": orden_repuesto.id,
                "orden_id": orden_repuesto.orden_id,
                "repuesto_id": orden_repuesto.repuesto_id,
                "cantidad": orden_repuesto.cantidad,
            },
        )
        return orden_repuesto

    def list_resumen(self):
        return self.repository.list_resumen()
