import uuid
from typing import Any
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.entities.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    documento: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(15))
    correo: Mapped[str | None] = mapped_column(String(100))
    direccion: Mapped[str | None] = mapped_column(Text)
    comuna: Mapped[str | None] = mapped_column(String(100))
    ciudad: Mapped[str | None] = mapped_column(String(100))
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    placa: Mapped[str] = mapped_column(String(10), primary_key=True)
    marca: Mapped[str] = mapped_column(String(50), nullable=False)
    modelo: Mapped[str | None] = mapped_column(String(50))
    color: Mapped[str | None] = mapped_column(String(30))
    ano: Mapped[int | None] = mapped_column(Integer)
    tipo: Mapped[str | None] = mapped_column(String(30))
    vin: Mapped[str | None] = mapped_column(String(50))
    km: Mapped[int | None] = mapped_column(Integer)
    cliente_documento: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("clientes.documento", ondelete="CASCADE"),
        nullable=True,
    )


class Inventario(Base):
    __tablename__ = "inventario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_repuesto: Mapped[str] = mapped_column(String(100), nullable=False)
    sku: Mapped[str | None] = mapped_column(String(50))
    categoria: Mapped[str | None] = mapped_column(String(80))
    ubicacion: Mapped[str | None] = mapped_column(String(50))
    stock_actual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    stock_maximo: Mapped[int | None] = mapped_column(Integer)
    precio_compra: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    proveedor: Mapped[str | None] = mapped_column(String(100))


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repuesto_id: Mapped[int] = mapped_column(ForeignKey("inventario.id"), nullable=False)
    tipo_movimiento: Mapped[str] = mapped_column(String(10), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Orden(Base):
    __tablename__ = "ordenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    placa_vehiculo: Mapped[str] = mapped_column(ForeignKey("vehiculos.placa"), nullable=False)
    diagnostico: Mapped[str | None] = mapped_column(Text)
    trabajo_realizado: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="Diagnostico")
    numero: Mapped[str | None] = mapped_column(String(20))
    tipo_servicio: Mapped[str | None] = mapped_column(String(20))
    descripcion: Mapped[str | None] = mapped_column(Text)
    prioridad: Mapped[str | None] = mapped_column(String(20))
    lineas: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    inventario_vehiculo: Mapped[dict[str, bool]] = mapped_column(JSON, default=dict)
    kilometraje: Mapped[int | None] = mapped_column(Integer)
    nivel_combustible: Mapped[int | None] = mapped_column(Integer)
    estado_vehiculo: Mapped[str | None] = mapped_column(Text)
    notas: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    tareas: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    descuento: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    iva: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    tecnico_asignado: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    mecanico_asignado: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    fecha_ingreso: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime)


class OrdenRepuesto(Base):
    __tablename__ = "orden_repuestos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    repuesto_id: Mapped[int] = mapped_column(ForeignKey("inventario.id"), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    monto_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    metodo_pago: Mapped[str | None] = mapped_column(String(50))
    referencia: Mapped[str | None] = mapped_column(String(50))
    fecha_pago: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class HistorialMantenimiento(Base):
    __tablename__ = "historial_mantenimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    placa_vehiculo: Mapped[str] = mapped_column(ForeignKey("vehiculos.placa", ondelete="CASCADE"), nullable=False)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), nullable=False)
    kilometraje_actual: Mapped[int | None] = mapped_column(Integer)
    servicio_realizado: Mapped[str] = mapped_column(String(255), nullable=False)
    observaciones_tecnicas: Mapped[str | None] = mapped_column(Text)
    fecha_servicio: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
