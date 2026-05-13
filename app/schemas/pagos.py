from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PagoCreate(BaseModel):
    orden_id: int
    monto_total: Decimal
    metodo_pago: str | None = None
    referencia: str | None = None


class PagoResponse(BaseModel):
    id: int
    orden_id: int
    monto_total: Decimal
    metodo_pago: str | None = None
    referencia: str | None = None
    fecha_pago: datetime

    model_config = {"from_attributes": True}


class PagoFrontendCreate(BaseModel):
    id: str | None = None
    ordenId: str
    metodo: str
    monto: Decimal
    referencia: str | None = None
    fecha: str | None = None


class PagoFrontendResponse(BaseModel):
    id: str
    ordenId: str
    metodo: str
    monto: Decimal
    referencia: str | None = None
    fecha: str
