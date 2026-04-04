from fastapi import HTTPException, status

from app.repositories.vehiculos_repository import VehiculosRepository


class VehiculosService:
    def __init__(self, repository: VehiculosRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def get(self, placa: str):
        vehiculo = self.repository.get(placa)
        if not vehiculo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehiculo no encontrado")
        return vehiculo

    def create(self, payload: dict):
        return self.repository.create(payload)

    def update(self, placa: str, payload: dict):
        vehiculo = self.get(placa)
        return self.repository.update(vehiculo, payload)

    def delete(self, placa: str):
        vehiculo = self.get(placa)
        self.repository.delete(vehiculo)
