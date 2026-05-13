from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.core.security import require_roles
from app.entities.models import Inventario
from app.repositories.inventario_repository import InventarioRepository
from app.schemas.inventario import (
    RepuestoFrontendCreate,
    RepuestoFrontendResponse,
    RepuestoFrontendUpdate,
    MovimientoCreate,
    MovimientoResponse,
)
from app.services.inventario_service import InventarioService

router = APIRouter()


def _build_front_repuesto(_: Session, item: Inventario) -> RepuestoFrontendResponse:
    return RepuestoFrontendResponse(
        id=item.id,
        nombre=item.nombre_repuesto,
        sku=item.sku,
        categoria=item.categoria,
        proveedor=item.proveedor,
        ubicacion=item.ubicacion,
        stock=item.stock_actual,
        stockMin=item.stock_minimo,
        stockMax=item.stock_maximo,
        precioCompra=item.precio_compra,
        precioVenta=item.precio_venta,
    )


@router.get("", response_model=list[RepuestoFrontendResponse], dependencies=[Depends(require_roles("admin", "almacen"))])
def list_inventario(db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return [_build_front_repuesto(db, item) for item in service.list()]


@router.get("/movimientos", response_model=list[MovimientoResponse], dependencies=[Depends(require_roles("admin", "almacen"))])
def list_movimientos(db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.list_movements()


@router.get("/alertas", response_model=list[RepuestoFrontendResponse], dependencies=[Depends(require_roles("admin", "almacen"))])
def alertas_stock(db: DbSession):
    items = db.query(Inventario).filter(Inventario.stock_actual < Inventario.stock_minimo).all()
    return [_build_front_repuesto(db, item) for item in items]


@router.post("", response_model=RepuestoFrontendResponse, dependencies=[Depends(require_roles("admin", "almacen"))])
def create_inventario(payload: RepuestoFrontendCreate, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    item = service.create(
        {
            "nombre_repuesto": payload.nombre,
            "sku": payload.sku,
            "categoria": payload.categoria,
            "proveedor": payload.proveedor,
            "ubicacion": payload.ubicacion,
            "stock_actual": payload.stock,
            "stock_minimo": payload.stockMin,
            "stock_maximo": payload.stockMax,
            "precio_compra": payload.precioCompra,
            "precio_venta": payload.precioVenta,
        }
    )
    return _build_front_repuesto(db, item)


@router.put("/{repuesto_id}", response_model=RepuestoFrontendResponse, dependencies=[Depends(require_roles("admin", "almacen"))])
def update_inventario(repuesto_id: int, payload: RepuestoFrontendUpdate, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    updates: dict[str, Any] = {}
    if payload.nombre is not None:
        updates["nombre_repuesto"] = payload.nombre
    if payload.sku is not None:
        updates["sku"] = payload.sku
    if payload.categoria is not None:
        updates["categoria"] = payload.categoria
    if payload.proveedor is not None:
        updates["proveedor"] = payload.proveedor
    if payload.ubicacion is not None:
        updates["ubicacion"] = payload.ubicacion
    if payload.stock is not None:
        updates["stock_actual"] = payload.stock
    if payload.stockMin is not None:
        updates["stock_minimo"] = payload.stockMin
    if payload.stockMax is not None:
        updates["stock_maximo"] = payload.stockMax
    if payload.precioCompra is not None:
        updates["precio_compra"] = payload.precioCompra
    if payload.precioVenta is not None:
        updates["precio_venta"] = payload.precioVenta
    item = service.update(repuesto_id, updates)
    return _build_front_repuesto(db, item)


@router.post("/movimientos", response_model=MovimientoResponse, dependencies=[Depends(require_roles("admin", "almacen"))])
def create_movimiento(payload: MovimientoCreate, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.create_movement(payload.model_dump())


@router.delete("/{repuesto_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_inventario(repuesto_id: int, db: DbSession):
    service = InventarioService(InventarioRepository(db))
    service.delete(repuesto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
