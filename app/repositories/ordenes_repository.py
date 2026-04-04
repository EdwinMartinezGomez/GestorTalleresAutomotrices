from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.entities.models import Orden, OrdenRepuesto


class OrdenesRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Orden]:
        return self.db.query(Orden).order_by(Orden.fecha_ingreso.desc()).all()

    def get(self, orden_id: int) -> Orden | None:
        return self.db.get(Orden, orden_id)

    def create(self, payload: dict[str, Any]) -> Orden:
        instance = Orden(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: Orden, payload: dict[str, Any]) -> Orden:
        for key, value in payload.items():
            setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: Orden) -> None:
        self.db.delete(instance)
        self.db.commit()

    def add_repuesto(self, payload: dict[str, Any]) -> OrdenRepuesto:
        instance = OrdenRepuesto(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def list_resumen(self) -> list[dict[str, Any]]:
        rows = self.db.execute(text("SELECT estado, total FROM vista_resumen_ordenes")).mappings().all()
        return [dict(row) for row in rows]
