from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.core.kafka_metrics import kafka_metrics_consumer
from app.core.security import require_roles
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.ordenes_repository import OrdenesRepository
from app.repositories.pagos_repository import PagosRepository
from app.services.inventario_service import InventarioService
from app.services.ordenes_service import OrdenesService
from app.services.pagos_service import PagosService

router = APIRouter(dependencies=[Depends(require_roles("admin", "gerencia"))])


@router.get("/ingresos", response_model=list[dict[str, Any]])
def reporte_ingresos(db: DbSession):
    service = PagosService(PagosRepository(db))
    return service.list_ingresos_por_dia()


@router.get("/alertas-stock", response_model=list[dict[str, Any]])
def reporte_alertas_stock(db: DbSession):
    service = InventarioService(InventarioRepository(db))
    return service.list_alertas_stock()


@router.get("/ordenes", response_model=list[dict[str, Any]])
def reporte_ordenes(db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.list_resumen()


@router.get("/kafka-metricas", response_model=dict[str, Any])
def reporte_kafka_metricas():
    return kafka_metrics_consumer.snapshot()
