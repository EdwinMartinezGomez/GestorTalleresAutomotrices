from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.core.security import require_roles
from app.repositories.historial_repository import HistorialRepository
from app.schemas.historial import HistorialCreate, HistorialResponse
from app.services.historial_service import HistorialService

router = APIRouter()


@router.get("", response_model=list[HistorialResponse])
def list_historial(db: DbSession):
    service = HistorialService(HistorialRepository(db))
    return service.list()


@router.post("", response_model=HistorialResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def create_historial(payload: HistorialCreate, db: DbSession):
    service = HistorialService(HistorialRepository(db))
    return service.create(payload.model_dump())


@router.get("/vehiculo-completo", response_model=list[dict[str, Any]])
def historial_completo(db: DbSession):
    service = HistorialService(HistorialRepository(db))
    return service.list_historial_completo()
