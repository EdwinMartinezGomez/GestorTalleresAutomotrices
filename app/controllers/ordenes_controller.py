from typing import Any

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import DbSession
from app.core.security import require_roles
from app.repositories.ordenes_repository import OrdenesRepository
from app.schemas.ordenes import OrdenCreate, OrdenRepuestoCreate, OrdenRepuestoResponse, OrdenResponse, OrdenUpdate
from app.services.ordenes_service import OrdenesService

router = APIRouter()


@router.get("", response_model=list[OrdenResponse], dependencies=[Depends(require_roles("admin", "mecanico"))])
def list_ordenes(db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.list()


@router.post("", response_model=OrdenResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def create_orden(payload: OrdenCreate, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.create(payload.model_dump())


@router.put("/{orden_id}", response_model=OrdenResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def update_orden(orden_id: int, payload: OrdenUpdate, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    updates = payload.model_dump(exclude_none=True)
    return service.update(orden_id, updates)


@router.post("/repuestos", response_model=OrdenRepuestoResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def add_repuesto(payload: OrdenRepuestoCreate, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.add_repuesto(payload.model_dump())


@router.get("/resumen/estados", response_model=list[dict[str, Any]], dependencies=[Depends(require_roles("admin", "mecanico", "gerencia"))])
def resumen_estados(db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.list_resumen()


@router.get("/{orden_id}", response_model=OrdenResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def get_orden(orden_id: int, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.get(orden_id)


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_orden(orden_id: int, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    service.delete(orden_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
