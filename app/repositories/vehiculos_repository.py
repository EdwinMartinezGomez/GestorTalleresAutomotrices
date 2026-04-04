from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.entities.models import Vehiculo


class VehiculosRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Vehiculo]:
        return self.db.query(Vehiculo).order_by(Vehiculo.placa.asc()).all()

    def get(self, placa: str) -> Vehiculo | None:
        return self.db.get(Vehiculo, placa)

    def create(self, payload: dict[str, Any]) -> Vehiculo:
        instance = Vehiculo(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: Vehiculo, payload: dict[str, Any]) -> Vehiculo:
        for key, value in payload.items():
            setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: Vehiculo) -> None:
        self.db.delete(instance)
        self.db.commit()
