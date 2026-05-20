from datetime import datetime

from pydantic import BaseModel


class OrdenBase(BaseModel):
    placa_vehiculo: str
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    estado: str = "Diagnostico"
    mecanico_asignado: int | None = None
    fecha_entrega: datetime | None = None


class OrdenCreate(OrdenBase):
    pass


class OrdenUpdate(BaseModel):
    diagnostico: str | None = None
    trabajo_realizado: str | None = None
    estado: str | None = None
    mecanico_asignado: int | None = None
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


class OrdenClienteRef(BaseModel):
    id: int
    nombre: str
    telefono: str


class OrdenVehiculoRef(BaseModel):
    id: int
    marca: str
    modelo: str
    placa: str
    ano: int
    color: str


class OrdenUsuarioRef(BaseModel):
    id: int
    nombre: str
    rol: str


class OrdenNota(BaseModel):
    id: int
    autor: str
    fecha: str
    texto: str


class OrdenTarea(BaseModel):
    id: int
    descripcion: str
    mecanico: str
    completada: bool


class OrdenLinea(BaseModel):
    id: int
    descripcion: str
    cantidad: int
    precioUnitario: float
    descuentoPct: float
    total: float
    repuestoId: int | None = None


class OrdenFrontendBase(BaseModel):
    numero: str
    estado: str
    tipoServicio: str
    descripcion: str
    fechaCreacion: str
    fechaLimite: str
    cliente: OrdenClienteRef
    vehiculo: OrdenVehiculoRef
    tecnicoAsignado: OrdenUsuarioRef | None = None
    lineas: list[OrdenLinea]
    inventarioVehiculo: dict[str, bool]
    kilometraje: int
    nivelCombustible: int
    estadoVehiculo: str
    notas: list[OrdenNota]
    diagnostico: str
    tareas: list[OrdenTarea]
    subtotal: float
    descuento: float
    iva: float
    total: float
    prioridad: str | None = None


class OrdenFrontendCreate(OrdenFrontendBase):
    pass


class OrdenFrontendUpdate(BaseModel):
    numero: str | None = None
    estado: str | None = None
    tipoServicio: str | None = None
    descripcion: str | None = None
    fechaCreacion: str | None = None
    fechaLimite: str | None = None
    cliente: OrdenClienteRef | None = None
    vehiculo: OrdenVehiculoRef | None = None
    tecnicoAsignado: OrdenUsuarioRef | None = None
    lineas: list[OrdenLinea] | None = None
    inventarioVehiculo: dict[str, bool] | None = None
    kilometraje: int | None = None
    nivelCombustible: int | None = None
    estadoVehiculo: str | None = None
    notas: list[OrdenNota] | None = None
    diagnostico: str | None = None
    tareas: list[OrdenTarea] | None = None
    subtotal: float | None = None
    descuento: float | None = None
    iva: float | None = None
    total: float | None = None
    prioridad: str | None = None


class OrdenFrontendResponse(OrdenFrontendBase):
    id: int
