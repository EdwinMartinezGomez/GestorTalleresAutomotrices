from uuid import UUID

from pydantic import BaseModel


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str | None = None
    color: str | None = None


class VehiculoCreate(VehiculoBase):
    cliente_id: UUID


class VehiculoUpdate(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    color: str | None = None
    cliente_id: UUID | None = None


class VehiculoResponse(VehiculoBase):
    cliente_id: UUID

    model_config = {"from_attributes": True}


class VehiculoFrontendCreate(BaseModel):
    marca: str
    modelo: str
    ano: int
    color: str
    placa: str
    tipo: str
    vin: str
    km: int
    clienteId: str


class VehiculoFrontendUpdate(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    ano: int | None = None
    color: str | None = None
    placa: str | None = None
    tipo: str | None = None
    vin: str | None = None
    km: int | None = None
    clienteId: str | None = None


class VehiculoFrontendResponse(BaseModel):
    id: str
    marca: str
    modelo: str | None = None
    ano: int | None = None
    color: str | None = None
    placa: str
    tipo: str | None = None
    vin: str | None = None
    km: int | None = None
    cliente: str | None = None
    clienteId: str | None = None
