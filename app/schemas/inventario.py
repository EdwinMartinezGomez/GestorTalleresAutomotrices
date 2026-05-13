from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class InventarioBase(BaseModel):
    nombre_repuesto: str
    sku: str | None = None
    categoria: str | None = None
    ubicacion: str | None = None
    stock_actual: int = 0
    stock_minimo: int = 5
    stock_maximo: int | None = None
    precio_compra: Decimal | None = None
    precio_venta: Decimal
    proveedor: str | None = None


class InventarioCreate(InventarioBase):
    pass


class InventarioUpdate(BaseModel):
    nombre_repuesto: str | None = None
    sku: str | None = None
    categoria: str | None = None
    ubicacion: str | None = None
    stock_actual: int | None = None
    stock_minimo: int | None = None
    stock_maximo: int | None = None
    precio_compra: Decimal | None = None
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


class RepuestoFrontendCreate(BaseModel):
    nombre: str
    sku: str
    categoria: str
    proveedor: str
    ubicacion: str
    stock: int
    stockMin: int
    stockMax: int
    precioCompra: Decimal
    precioVenta: Decimal


class RepuestoFrontendUpdate(BaseModel):
    nombre: str | None = None
    sku: str | None = None
    categoria: str | None = None
    proveedor: str | None = None
    ubicacion: str | None = None
    stock: int | None = None
    stockMin: int | None = None
    stockMax: int | None = None
    precioCompra: Decimal | None = None
    precioVenta: Decimal | None = None


class RepuestoFrontendResponse(BaseModel):
    id: int
    nombre: str
    sku: str | None = None
    categoria: str | None = None
    proveedor: str | None = None
    ubicacion: str | None = None
    stock: int
    stockMin: int
    stockMax: int | None = None
    precioCompra: Decimal | None = None
    precioVenta: Decimal
