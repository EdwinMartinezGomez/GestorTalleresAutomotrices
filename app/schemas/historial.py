from datetime import datetime

from pydantic import BaseModel


class HistorialCreate(BaseModel):
    placa_vehiculo: str
    orden_id: int
    kilometraje_actual: int | None = None
    servicio_realizado: str
    observaciones_tecnicas: str | None = None


class HistorialResponse(BaseModel):
    id: int
    placa_vehiculo: str
    orden_id: int
    kilometraje_actual: int | None = None
    servicio_realizado: str
    observaciones_tecnicas: str | None = None
    fecha_servicio: datetime

    model_config = {"from_attributes": True}
