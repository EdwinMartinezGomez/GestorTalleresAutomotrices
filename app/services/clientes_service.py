from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.kafka_events import publish_domain_event
from app.repositories.clientes_repository import ClientesRepository


class ClientesService:
    def __init__(self, repository: ClientesRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def get(self, cliente_id: UUID):
        cliente = self.repository.get(cliente_id)
        if not cliente:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
        return cliente

    def create(self, payload: dict):
        try:
            cliente = self.repository.create(payload)
        except IntegrityError as exc:
            self.repository.db.rollback()
            self._raise_conflict_if_duplicate_documento(exc)
            raise
        publish_domain_event(
            topic_suffix="clientes",
            event_type="cliente_creado",
            payload={
                "cliente_id": str(cliente.id),
                "documento": cliente.documento,
            },
        )
        return cliente

    def update(self, cliente_id: UUID, payload: dict):
        cliente = self.get(cliente_id)
        try:
            updated = self.repository.update(cliente, payload)
        except IntegrityError as exc:
            self.repository.db.rollback()
            self._raise_conflict_if_duplicate_documento(exc)
            raise
        publish_domain_event(
            topic_suffix="clientes",
            event_type="cliente_actualizado",
            payload={
                "cliente_id": str(updated.id),
                "campos_actualizados": list(payload.keys()),
            },
        )
        return updated

    def delete(self, cliente_id: UUID):
        cliente = self.get(cliente_id)
        self.repository.delete(cliente)
        publish_domain_event(
            topic_suffix="clientes",
            event_type="cliente_eliminado",
            payload={
                "cliente_id": str(cliente_id),
            },
        )

    def _raise_conflict_if_duplicate_documento(self, exc: IntegrityError) -> None:
        message = str(getattr(exc, "orig", exc)).lower()
        if "clientes_documento_key" in message or "duplicate key value" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un cliente con ese documento",
            ) from exc
