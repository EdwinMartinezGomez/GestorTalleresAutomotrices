from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.core.security import require_roles
from app.repositories.pagos_repository import PagosRepository
from app.schemas.pagos import PagoCreate, PagoResponse
from app.services.pagos_service import PagosService

router = APIRouter()


@router.get("", response_model=list[PagoResponse], dependencies=[Depends(require_roles("admin", "cajero"))])
def list_pagos(db: DbSession):
    service = PagosService(PagosRepository(db))
    return service.list()


@router.post("", response_model=PagoResponse, dependencies=[Depends(require_roles("admin", "cajero"))])
def create_pago(payload: PagoCreate, db: DbSession):
    service = PagosService(PagosRepository(db))
    return service.create(payload.model_dump())
