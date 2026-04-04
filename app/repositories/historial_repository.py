from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.entities.models import HistorialMantenimiento


class HistorialRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[HistorialMantenimiento]:
        return self.db.query(HistorialMantenimiento).order_by(HistorialMantenimiento.fecha_servicio.desc()).all()

    def create(self, payload: dict[str, Any]) -> HistorialMantenimiento:
        instance = HistorialMantenimiento(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def list_historial_completo(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            text(
                "SELECT placa, modelo, fecha_servicio, servicio_realizado, kilometraje_actual, mecanico_asignado "
                "FROM vista_historial_completo ORDER BY fecha_servicio DESC"
            )
        ).mappings().all()
        return [dict(row) for row in rows]
