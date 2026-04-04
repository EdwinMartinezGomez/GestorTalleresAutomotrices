from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class PagoCreate(BaseModel):
    orden_id: int
    monto_total: Decimal
    metodo_pago: str | None = None


class PagoResponse(BaseModel):
    id: int
    orden_id: int
    monto_total: Decimal
    metodo_pago: str | None = None
    fecha_pago: datetime

    model_config = {"from_attributes": True}
