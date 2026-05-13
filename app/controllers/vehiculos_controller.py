from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.core.security import require_roles
from app.entities.models import Cliente, Vehiculo
from app.repositories.vehiculos_repository import VehiculosRepository
from app.schemas.vehiculos import (
    VehiculoFrontendCreate,
    VehiculoFrontendResponse,
    VehiculoFrontendUpdate,
)
from app.services.vehiculos_service import VehiculosService

router = APIRouter()


def _build_front_vehiculo(db: Session, vehiculo: Vehiculo) -> VehiculoFrontendResponse:
    cliente = db.get(Cliente, vehiculo.cliente_id)
    return VehiculoFrontendResponse(
        id=vehiculo.placa,
        marca=vehiculo.marca,
        modelo=vehiculo.modelo,
        ano=vehiculo.ano,
        color=vehiculo.color,
        placa=vehiculo.placa,
        tipo=vehiculo.tipo,
        vin=vehiculo.vin,
        km=vehiculo.km,
        cliente=cliente.nombre if cliente else None,
        clienteId=str(vehiculo.cliente_id),
    )


def _parse_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="clienteId invalido") from exc


@router.get("", response_model=list[VehiculoFrontendResponse], dependencies=[Depends(require_roles("admin", "recepcionista"))])
def list_vehiculos(db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    vehiculos = service.list()
    return [_build_front_vehiculo(db, vehiculo) for vehiculo in vehiculos]


@router.get("/{placa}", response_model=VehiculoFrontendResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def get_vehiculo(placa: str, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    vehiculo = service.get(placa)
    return _build_front_vehiculo(db, vehiculo)


@router.post("", response_model=VehiculoFrontendResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def create_vehiculo(payload: VehiculoFrontendCreate, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    cliente_id = _parse_uuid(payload.clienteId)
    vehiculo = service.create(
        {
            "placa": payload.placa,
            "marca": payload.marca,
            "modelo": payload.modelo,
            "color": payload.color,
            "ano": payload.ano,
            "tipo": payload.tipo,
            "vin": payload.vin,
            "km": payload.km,
            "cliente_id": cliente_id,
        }
    )
    return _build_front_vehiculo(db, vehiculo)


@router.put("/{placa}", response_model=VehiculoFrontendResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def update_vehiculo(placa: str, payload: VehiculoFrontendUpdate, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    updates: dict[str, object] = {}
    if payload.marca is not None:
        updates["marca"] = payload.marca
    if payload.modelo is not None:
        updates["modelo"] = payload.modelo
    if payload.color is not None:
        updates["color"] = payload.color
    if payload.ano is not None:
        updates["ano"] = payload.ano
    if payload.tipo is not None:
        updates["tipo"] = payload.tipo
    if payload.vin is not None:
        updates["vin"] = payload.vin
    if payload.km is not None:
        updates["km"] = payload.km
    if payload.clienteId is not None:
        updates["cliente_id"] = _parse_uuid(payload.clienteId)
    vehiculo = service.update(placa, updates)
    return _build_front_vehiculo(db, vehiculo)


@router.delete("/{placa}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_vehiculo(placa: str, db: DbSession):
    service = VehiculosService(VehiculosRepository(db))
    service.delete(placa)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
