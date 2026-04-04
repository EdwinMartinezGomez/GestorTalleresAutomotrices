from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.entities.models import Inventario, MovimientoInventario


class InventarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Inventario]:
        return self.db.query(Inventario).order_by(Inventario.id.asc()).all()

    def get(self, repuesto_id: int) -> Inventario | None:
        return self.db.get(Inventario, repuesto_id)

    def create(self, payload: dict[str, Any]) -> Inventario:
        instance = Inventario(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: Inventario, payload: dict[str, Any]) -> Inventario:
        for key, value in payload.items():
            setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: Inventario) -> None:
        self.db.delete(instance)
        self.db.commit()

    def create_movement(self, payload: dict[str, Any]) -> MovimientoInventario:
        movement = MovimientoInventario(**payload)
        self.db.add(movement)
        self.db.commit()
        self.db.refresh(movement)
        return movement

    def list_movements(self) -> list[MovimientoInventario]:
        return self.db.query(MovimientoInventario).order_by(MovimientoInventario.fecha.desc()).all()

    def get_alertas_stock(self) -> list[dict[str, Any]]:
        rows = self.db.execute(text("SELECT nombre_repuesto, stock_actual, stock_minimo FROM vista_alertas_stock")).mappings().all()
        return [dict(row) for row in rows]
