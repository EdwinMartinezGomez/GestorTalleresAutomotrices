from pydantic import BaseModel


class VehiculoBase(BaseModel):
    placa: str
    marca: str
    modelo: str | None = None
    color: str | None = None


class VehiculoCreate(VehiculoBase):
    cliente_id: str


class VehiculoUpdate(BaseModel):
    marca: str | None = None
    modelo: str | None = None
    color: str | None = None
    cliente_id: str | None = None


class VehiculoResponse(VehiculoBase):
    cliente_id: str

    model_config = {"from_attributes": True}
