from pydantic import BaseModel


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str | None = None
    color: str | None = None


class VehiculoCreate(VehiculoBase):
    cliente_documento: str


class VehiculoUpdate(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    color: str | None = None
    cliente_documento: str | None = None


class VehiculoResponse(VehiculoBase):
    cliente_documento: str

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
    clienteDocumento: str


class VehiculoFrontendUpdate(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    ano: int | None = None
    color: str | None = None
    placa: str | None = None
    tipo: str | None = None
    vin: str | None = None
    km: int | None = None
    clienteDocumento: str | None = None


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
    clienteDocumento: str | None = None
