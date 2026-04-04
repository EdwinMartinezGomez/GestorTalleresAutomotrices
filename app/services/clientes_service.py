from uuid import UUID

from fastapi import HTTPException, status

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
        return self.repository.create(payload)

    def update(self, cliente_id: UUID, payload: dict):
        cliente = self.get(cliente_id)
        return self.repository.update(cliente, payload)

    def delete(self, cliente_id: UUID):
        cliente = self.get(cliente_id)
        self.repository.delete(cliente)
