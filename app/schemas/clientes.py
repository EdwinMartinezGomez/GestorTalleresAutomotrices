from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ClienteBase(BaseModel):
    documento: str
    nombre: str
    telefono: str | None = None
    correo: EmailStr | None = None
    direccion: str | None = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    documento: str | None = None
    nombre: str | None = None
    telefono: str | None = None
    correo: EmailStr | None = None
    direccion: str | None = None


class ClienteResponse(ClienteBase):
    id: UUID
    fecha_registro: datetime

    model_config = {"from_attributes": True}


class ClienteFrontendCreate(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str
    rut: str
    direccion: str
    comuna: str
    ciudad: str


class ClienteFrontendUpdate(BaseModel):
    nombre: str | None = None
    email: EmailStr | None = None
    telefono: str | None = None
    rut: str | None = None
    direccion: str | None = None
    comuna: str | None = None
    ciudad: str | None = None


class ClienteFrontendResponse(BaseModel):
    id: str
    nombre: str
    email: EmailStr | None = None
    telefono: str
    rut: str
    direccion: str | None = None
    comuna: str | None = None
    ciudad: str | None = None
    vehiculos: int = 0
    ultimaVisita: str | None = None
    estadoOrden: str | None = None
