from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

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
        try:
            return self.repository.create(payload)
        except IntegrityError as exc:
            self.repository.db.rollback()
            self._raise_conflict_if_duplicate_placa(exc)
            raise

    def update(self, placa: str, payload: dict):
        vehiculo = self.get(placa)
        try:
            return self.repository.update(vehiculo, payload)
        except IntegrityError as exc:
            self.repository.db.rollback()
            self._raise_conflict_if_duplicate_placa(exc)
            raise

    def delete(self, placa: str):
        vehiculo = self.get(placa)
        self.repository.delete(vehiculo)

    def _raise_conflict_if_duplicate_placa(self, exc: IntegrityError) -> None:
        message = str(getattr(exc, "orig", exc)).lower()
        if "vehiculos_pkey" in message or "duplicate" in message or "llave duplicada" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un vehiculo con esa placa",
            ) from exc
