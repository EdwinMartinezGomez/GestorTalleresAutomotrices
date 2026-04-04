from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrdenBase(BaseModel):
    placa_vehiculo: str
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    estado: str = "Diagnostico"
    mecanico_asignado: UUID | None = None
    fecha_entrega: datetime | None = None


class OrdenCreate(OrdenBase):
    pass


class OrdenUpdate(BaseModel):
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    estado: str | None = None
    mecanico_asignado: UUID | None = None
    fecha_entrega: datetime | None = None


class OrdenResponse(OrdenBase):
    id: int
    fecha_ingreso: datetime

    model_config = {"from_attributes": True}


class OrdenRepuestoCreate(BaseModel):
    orden_id: int
    repuesto_id: int
    cantidad: int = 1


class OrdenRepuestoResponse(BaseModel):
    id: int
    orden_id: int
    repuesto_id: int
    cantidad: int

    model_config = {"from_attributes": True}
