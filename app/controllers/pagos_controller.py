from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.core.security import require_roles
from app.repositories.pagos_repository import PagosRepository
from app.schemas.pagos import PagoFrontendCreate, PagoFrontendResponse
from app.services.pagos_service import PagosService

router = APIRouter()


def _parse_orden_id(value: str) -> int:
    digits = "".join(char for char in value if char.isdigit())
    return int(digits) if digits else 0


def _build_front_pago(pago) -> PagoFrontendResponse:
    return PagoFrontendResponse(
        id=f"P-{pago.id}",
        ordenId=f"OT-{pago.orden_id}",
        metodo=(pago.metodo_pago or "efectivo").lower(),
        monto=pago.monto_total,
        referencia=pago.referencia,
        fecha=pago.fecha_pago.date().isoformat(),
    )


@router.get("", response_model=list[PagoFrontendResponse], dependencies=[Depends(require_roles("admin", "cajero"))])
def list_pagos(db: DbSession):
    service = PagosService(PagosRepository(db))
    pagos = service.list()
    return [_build_front_pago(pago) for pago in pagos]


@router.post("", response_model=PagoFrontendResponse, dependencies=[Depends(require_roles("admin", "cajero"))])
def create_pago(payload: PagoFrontendCreate, db: DbSession):
    service = PagosService(PagosRepository(db))
    orden_id = _parse_orden_id(payload.ordenId)
    pago = service.create(
        {
            "orden_id": orden_id,
            "monto_total": payload.monto,
            "metodo_pago": payload.metodo,
            "referencia": payload.referencia,
        }
    )
    return _build_front_pago(pago)
