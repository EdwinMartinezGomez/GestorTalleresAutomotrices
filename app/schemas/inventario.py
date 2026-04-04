from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class InventarioBase(BaseModel):
    nombre_repuesto: str
    stock_actual: int = 0
    stock_minimo: int = 5
    precio_venta: Decimal
    proveedor: str | None = None


class InventarioCreate(InventarioBase):
    pass


class InventarioUpdate(BaseModel):
    nombre_repuesto: str | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None
    precio_venta: Decimal | None = None
    proveedor: str | None = None


class InventarioResponse(InventarioBase):
    id: int

    model_config = {"from_attributes": True}


class MovimientoCreate(BaseModel):
    repuesto_id: int
    tipo_movimiento: str
    cantidad: int


class MovimientoResponse(BaseModel):
    id: int
    repuesto_id: int
    tipo_movimiento: str
    cantidad: int
    fecha: datetime

    model_config = {"from_attributes": True}
