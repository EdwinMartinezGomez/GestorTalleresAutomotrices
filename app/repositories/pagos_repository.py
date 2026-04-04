from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.entities.models import Pago


class PagosRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Pago]:
        return self.db.query(Pago).order_by(Pago.fecha_pago.desc()).all()

    def get(self, pago_id: int) -> Pago | None:
        return self.db.get(Pago, pago_id)

    def create(self, payload: dict[str, Any]) -> Pago:
        instance = Pago(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: Pago) -> None:
        self.db.delete(instance)
        self.db.commit()

    def list_ingresos_por_dia(self) -> list[dict[str, Any]]:
        rows = self.db.execute(text("SELECT fecha, total_dia, cantidad_pagos FROM vista_reporte_ingresos ORDER BY fecha DESC")).mappings().all()
        return [dict(row) for row in rows]
