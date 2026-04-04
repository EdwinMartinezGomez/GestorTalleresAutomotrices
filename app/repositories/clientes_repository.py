from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.entities.models import Cliente


class ClientesRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Cliente]:
        return self.db.query(Cliente).order_by(Cliente.fecha_registro.desc()).all()

    def get(self, cliente_id: UUID) -> Cliente | None:
        return self.db.get(Cliente, cliente_id)

    def create(self, payload: dict[str, Any]) -> Cliente:
        instance = Cliente(**payload)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, instance: Cliente, payload: dict[str, Any]) -> Cliente:
        for key, value in payload.items():
            setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, instance: Cliente) -> None:
        self.db.delete(instance)
        self.db.commit()
