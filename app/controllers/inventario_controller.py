from typing import Any

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import DbSession
from app.core.security import require_roles
from app.repositories.inventario_repository import InventarioRepository
from app.schemas.inventario import (
    InventarioCreate,
    InventarioResponse,
    InventarioUpdate,
    MovimientoCreate,
    MovimientoResponse,
)
from app.services.inventario_service import InventarioService

router = APIRouter()


@router.get("", response_model=list[InventarioResponse])
def list_inventario(db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.list()


@router.get("/movimientos", response_model=list[MovimientoResponse])
def list_movimientos(db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.list_movements()


@router.get("/alertas", response_model=list[dict[str, Any]])
def alertas_stock(db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.list_alertas_stock()


@router.post("", response_model=InventarioResponse, dependencies=[Depends(require_roles("admin", "almacen"))])
def create_inventario(payload: InventarioCreate, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.create(payload.model_dump())


@router.put("/{repuesto_id}", response_model=InventarioResponse, dependencies=[Depends(require_roles("admin", "almacen"))])
def update_inventario(repuesto_id: int, payload: InventarioUpdate, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    updates = payload.model_dump(exclude_none=True)
    return service.update(repuesto_id, updates)


@router.post("/movimientos", response_model=MovimientoResponse, dependencies=[Depends(require_roles("admin", "almacen"))])
def create_movimiento(payload: MovimientoCreate, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.create_movement(payload.model_dump())


@router.delete("/{repuesto_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_inventario(repuesto_id: int, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    service.delete(repuesto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
