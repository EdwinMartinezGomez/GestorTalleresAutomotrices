from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.core.cache import cache_store
from app.core.security import require_roles
from app.entities.models import Cliente, Orden, Vehiculo
from app.repositories.clientes_repository import ClientesRepository
from app.schemas.clientes import (
    ClienteFrontendCreate,
    ClienteFrontendResponse,
    ClienteFrontendUpdate,
)
from app.services.clientes_service import ClientesService

router = APIRouter()


def _build_front_cliente(db: Session, cliente: Cliente) -> ClienteFrontendResponse:
    vehiculos_count = db.query(Vehiculo).filter(Vehiculo.cliente_documento == cliente.documento).count()
    ultima_orden = (
        db.query(Orden)
        .join(Vehiculo, Vehiculo.placa == Orden.placa_vehiculo)
        .filter(Vehiculo.cliente_documento == cliente.documento)
        .order_by(Orden.fecha_ingreso.desc())
        .first()
    )
    ultima_visita = ultima_orden.fecha_ingreso.isoformat() if ultima_orden else None
    estado_orden = ultima_orden.estado if ultima_orden and ultima_orden.estado else "Sin orden"
    return ClienteFrontendResponse(
        id=str(cliente.id),
        nombre=cliente.nombre,
        email=cliente.correo,
        telefono=cliente.telefono or "",
        rut=cliente.documento,
        direccion=cliente.direccion,
        comuna=cliente.comuna,
        ciudad=cliente.ciudad,
        vehiculos=vehiculos_count,
        ultimaVisita=ultima_visita,
        estadoOrden=estado_orden,
    )


@router.get("", response_model=list[ClienteFrontendResponse], dependencies=[Depends(require_roles("admin", "recepcionista"))])
def list_clientes(db: DbSession):
    service = ClientesService(ClientesRepository(db))
    cache_key = "clientes:list"
    return cache_store.cached(
        cache_key,
        lambda: [_build_front_cliente(db, cliente).model_dump() for cliente in service.list()],
        ttl_seconds=30,
    )


@router.get("/{cliente_id}", response_model=ClienteFrontendResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def get_cliente(cliente_id: UUID, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    cliente = service.get(cliente_id)
    return _build_front_cliente(db, cliente)


@router.post("", response_model=ClienteFrontendResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def create_cliente(payload: ClienteFrontendCreate, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    cliente = service.create(
        {
            "documento": payload.rut,
            "nombre": payload.nombre,
            "telefono": payload.telefono,
            "correo": payload.email,
            "direccion": payload.direccion,
            "comuna": payload.comuna,
            "ciudad": payload.ciudad,
        }
    )
    return _build_front_cliente(db, cliente)


@router.put("/{cliente_id}", response_model=ClienteFrontendResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def update_cliente(cliente_id: UUID, payload: ClienteFrontendUpdate, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    updates: dict[str, object] = {}
    if payload.rut is not None:
        updates["documento"] = payload.rut
    if payload.nombre is not None:
        updates["nombre"] = payload.nombre
    if payload.telefono is not None:
        updates["telefono"] = payload.telefono
    if payload.email is not None:
        updates["correo"] = payload.email
    if payload.direccion is not None:
        updates["direccion"] = payload.direccion
    if payload.comuna is not None:
        updates["comuna"] = payload.comuna
    if payload.ciudad is not None:
        updates["ciudad"] = payload.ciudad
    cliente = service.update(cliente_id, updates)
    return _build_front_cliente(db, cliente)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_cliente(cliente_id: UUID, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    service.delete(cliente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
