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
