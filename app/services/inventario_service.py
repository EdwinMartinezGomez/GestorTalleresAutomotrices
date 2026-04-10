from fastapi import HTTPException, status

from app.core.kafka_events import publish_domain_event
from app.repositories.inventario_repository import InventarioRepository


class InventarioService:
    def __init__(self, repository: InventarioRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def get(self, repuesto_id: int):
        item = self.repository.get(repuesto_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repuesto no encontrado")
        return item

    def create(self, payload: dict):
        item = self.repository.create(payload)
        publish_domain_event(
            topic_suffix="inventario",
            event_type="repuesto_creado",
            payload={
                "repuesto_id": item.id,
                "nombre_repuesto": item.nombre_repuesto,
                "stock_actual": item.stock_actual,
            },
        )
        return item

    def update(self, repuesto_id: int, payload: dict):
        item = self.get(repuesto_id)
        updated = self.repository.update(item, payload)
        publish_domain_event(
            topic_suffix="inventario",
            event_type="repuesto_actualizado",
            payload={
                "repuesto_id": updated.id,
                "campos_actualizados": list(payload.keys()),
            },
        )
        return updated

    def delete(self, repuesto_id: int):
        item = self.get(repuesto_id)
        self.repository.delete(item)
        publish_domain_event(
            topic_suffix="inventario",
            event_type="repuesto_eliminado",
            payload={"repuesto_id": repuesto_id},
        )

    def create_movement(self, payload: dict):
        item = self.get(payload["repuesto_id"])
        movement_type = payload["tipo_movimiento"].upper()
        quantity = payload["cantidad"]

        if quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor a cero")

        if movement_type == "ENTRADA":
            item.stock_actual += quantity
        elif movement_type == "SALIDA":
            if item.stock_actual < quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Stock insuficiente")
            item.stock_actual -= quantity
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de movimiento invalido")

        self.repository.update(item, {"stock_actual": item.stock_actual})
        payload["tipo_movimiento"] = movement_type
        movement = self.repository.create_movement(payload)
        publish_domain_event(
            topic_suffix="inventario",
            event_type="movimiento_inventario_creado",
            payload={
                "movimiento_id": movement.id,
                "repuesto_id": movement.repuesto_id,
                "tipo_movimiento": movement.tipo_movimiento,
                "cantidad": movement.cantidad,
                "stock_actual": item.stock_actual,
            },
        )
        return movement

    def list_movements(self):
        return self.repository.list_movements()

    def list_alertas_stock(self):
        return self.repository.get_alertas_stock()
