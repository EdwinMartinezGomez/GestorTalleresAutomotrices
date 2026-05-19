from collections import defaultdict
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import DbSession
from app.core.kafka_metrics import kafka_metrics_consumer
from app.core.security import require_roles
from app.entities.models import Cliente, Orden, Vehiculo
from app.repositories.inventario_repository import InventarioRepository
from app.repositories.ordenes_repository import OrdenesRepository
from app.repositories.pagos_repository import PagosRepository
from app.services.inventario_service import InventarioService
from app.services.ordenes_service import OrdenesService
from app.services.pagos_service import PagosService

router = APIRouter(dependencies=[Depends(require_roles("admin", "gerencia"))])


class DashboardChartDatum(BaseModel):
    label: str
    value: float
    color: str | None = None


class DashboardRecentOrden(BaseModel):
    numero: str
    cliente: str
    estado: str


class DashboardData(BaseModel):
    ordenesActivas: int
    ingresosMes: float
    vehiculosEnTaller: int
    stockBajo: int
    ingresosPorMes: list[DashboardChartDatum]
    ordenesPorEstado: list[DashboardChartDatum]
    ordenesRecientes: list[DashboardRecentOrden]


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


@router.get("/dashboard", response_model=DashboardData)
def dashboard(db: DbSession):
    orden_service = OrdenesService(OrdenesRepository(db))
    pago_service = PagosService(PagosRepository(db))
    inventario_service = InventarioService(InventarioRepository(db))

    ordenes = orden_service.list()
    pagos = pago_service.list()
    inventario = inventario_service.list()

    activos = {"ABIERTA", "EN_PROGRESO"}
    ordenes_activas = sum(1 for orden in ordenes if (orden.estado or "").upper() in activos)
    vehiculos_en_taller = sum(1 for orden in ordenes if (orden.estado or "").upper() != "CERRADA")
    stock_bajo = sum(1 for item in inventario if item.stock_actual < item.stock_minimo)

    now = datetime.utcnow()
    ingresos_mes = sum(
        float(pago.monto_total)
        for pago in pagos
        if pago.fecha_pago and pago.fecha_pago.year == now.year and pago.fecha_pago.month == now.month
    )

    ingresos_por_mes_map: dict[str, float] = defaultdict(float)
    for pago in pagos:
        if not pago.fecha_pago:
            continue
        label = pago.fecha_pago.strftime("%b")
        ingresos_por_mes_map[label] += float(pago.monto_total)

    ingresos_por_mes = [
        DashboardChartDatum(label=label, value=round(value, 2))
        for label, value in ingresos_por_mes_map.items()
    ]

    estados_map: dict[str, int] = defaultdict(int)
    for orden in ordenes:
        estado = (orden.estado or "").upper()
        estados_map[estado] += 1

    ordenes_por_estado = [
        DashboardChartDatum(label=label.title(), value=value)
        for label, value in estados_map.items()
    ]

    recientes: list[DashboardRecentOrden] = []
    ordenes_sorted = sorted(ordenes, key=lambda item: item.fecha_ingreso or datetime.min, reverse=True)
    for orden in ordenes_sorted[:3]:
        cliente_nombre = ""
        vehiculo = db.get(Vehiculo, orden.placa_vehiculo)
        if vehiculo:
            cliente = db.query(Cliente).filter(Cliente.documento == vehiculo.cliente_documento).first()
            if cliente:
                cliente_nombre = cliente.nombre
        recientes.append(
            DashboardRecentOrden(
                numero=orden.numero or str(orden.id).zfill(4),
                cliente=cliente_nombre,
                estado=orden.estado or "",
            )
        )

    return DashboardData(
        ordenesActivas=ordenes_activas,
        ingresosMes=round(ingresos_mes, 2),
        vehiculosEnTaller=vehiculos_en_taller,
        stockBajo=stock_bajo,
        ingresosPorMes=ingresos_por_mes,
        ordenesPorEstado=ordenes_por_estado,
        ordenesRecientes=recientes,
    )
