from fastapi import APIRouter, Depends, Response, status

from app.api.deps import DbSession
from app.core.security import require_roles
from app.repositories.vehiculos_repository import VehiculosRepository
from app.schemas.vehiculos import VehiculoCreate, VehiculoResponse, VehiculoUpdate
from app.services.vehiculos_service import VehiculosService

router = APIRouter()


@router.get("", response_model=list[VehiculoResponse], dependencies=[Depends(require_roles("admin", "recepcionista"))])
def list_vehiculos(db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    return service.list()


@router.get("/{placa}", response_model=VehiculoResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def get_vehiculo(placa: str, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    return service.get(placa)


@router.post("", response_model=VehiculoResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def create_vehiculo(payload: VehiculoCreate, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    return service.create(payload.model_dump())


@router.put("/{placa}", response_model=VehiculoResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def update_vehiculo(placa: str, payload: VehiculoUpdate, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    updates = payload.model_dump(exclude_none=True)
    return service.update(placa, updates)


@router.delete("/{placa}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_vehiculo(placa: str, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    service.delete(placa)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
