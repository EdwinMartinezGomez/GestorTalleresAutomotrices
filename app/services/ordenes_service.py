from fastapi import HTTPException, status

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
        return self.repository.create(payload)

    def update(self, orden_id: int, payload: dict):
        orden = self.get(orden_id)
        return self.repository.update(orden, payload)

    def delete(self, orden_id: int):
        orden = self.get(orden_id)
        self.repository.delete(orden)

    def add_repuesto(self, payload: dict):
        self.get(payload["orden_id"])
        return self.repository.add_repuesto(payload)

    def list_resumen(self):
        return self.repository.list_resumen()
