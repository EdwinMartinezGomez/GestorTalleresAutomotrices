from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.core.security import require_roles
from app.entities.models import Cliente, Orden, Vehiculo
from app.repositories.ordenes_repository import OrdenesRepository
from app.schemas.ordenes import (
    OrdenFrontendCreate,
    OrdenFrontendResponse,
    OrdenFrontendUpdate,
    OrdenLinea,
    OrdenNota,
    OrdenRepuestoCreate,
    OrdenRepuestoResponse,
)
from app.services.ordenes_service import OrdenesService

router = APIRouter()


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _to_numeric_id(value: str | None) -> int:
    if not value:
        return 0
    digits = "".join(char for char in value if char.isdigit())
    return int(digits) if digits else 0


def _calculate_totals(lineas: list[dict[str, Any]]) -> dict[str, float]:
    subtotal = 0.0
    descuento = 0.0
    for linea in lineas:
        cantidad = float(linea.get("cantidad", 0))
        precio = float(linea.get("precioUnitario", 0))
        descuento_pct = float(linea.get("descuentoPct", 0))
        subtotal += cantidad * precio
        descuento += cantidad * precio * (descuento_pct / 100)
    neto = subtotal - descuento
    iva = neto * 0.19
    total = neto + iva
    return {
        "subtotal": round(subtotal, 2),
        "descuento": round(descuento, 2),
        "iva": round(iva, 2),
        "total": round(total, 2),
    }


def _normalize_lineas(lineas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for linea in lineas:
        payload = dict(linea)
        if "total" not in payload:
            cantidad = float(payload.get("cantidad", 0))
            precio = float(payload.get("precioUnitario", 0))
            descuento_pct = float(payload.get("descuentoPct", 0))
            total = cantidad * precio * (1 - descuento_pct / 100)
            payload["total"] = round(total, 2)
        normalized.append(payload)
    return normalized


def _build_front_orden(db: Session, orden: Orden) -> OrdenFrontendResponse:
    vehiculo = db.get(Vehiculo, orden.placa_vehiculo)
    cliente = db.query(Cliente).filter(Cliente.documento == vehiculo.cliente_documento).first() if vehiculo else None
    lineas = _normalize_lineas(orden.lineas or [])
    totals = _calculate_totals(lineas)
    return OrdenFrontendResponse(
        id=orden.id,
        numero=orden.numero or str(orden.id).zfill(4),
        estado=orden.estado or "ABIERTA",
        tipoServicio=orden.tipo_servicio or "MANTENCION",
        descripcion=orden.descripcion or "",
        fechaCreacion=orden.fecha_ingreso.isoformat() if orden.fecha_ingreso else "",
        fechaLimite=orden.fecha_entrega.isoformat() if orden.fecha_entrega else (orden.fecha_ingreso.isoformat() if orden.fecha_ingreso else ""),
        cliente={
            "id": _to_numeric_id(str(cliente.id)) if cliente else 0,
            "nombre": cliente.nombre if cliente else "",
            "telefono": cliente.telefono or "" if cliente else "",
        },
        vehiculo={
            "id": _to_numeric_id(vehiculo.placa) if vehiculo else 0,
            "marca": vehiculo.marca if vehiculo else "",
            "modelo": vehiculo.modelo or "" if vehiculo else "",
            "placa": vehiculo.placa if vehiculo else orden.placa_vehiculo,
            "ano": vehiculo.ano or 0 if vehiculo else 0,
            "color": vehiculo.color or "" if vehiculo else "",
        },
        tecnicoAsignado=orden.tecnico_asignado,
        lineas=lineas,
        inventarioVehiculo=orden.inventario_vehiculo or {},
        kilometraje=orden.kilometraje or 0,
        nivelCombustible=orden.nivel_combustible or 0,
        estadoVehiculo=orden.estado_vehiculo or "",
        notas=orden.notas or [],
        diagnostico=orden.diagnostico or "",
        tareas=orden.tareas or [],
        subtotal=float(orden.subtotal) if orden.subtotal is not None else totals["subtotal"],
        descuento=float(orden.descuento) if orden.descuento is not None else totals["descuento"],
        iva=float(orden.iva) if orden.iva is not None else totals["iva"],
        total=float(orden.total) if orden.total is not None else totals["total"],
        prioridad=orden.prioridad,
    )


@router.get("", response_model=list[OrdenFrontendResponse], dependencies=[Depends(require_roles("admin", "mecanico"))])
def list_ordenes(db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    ordenes = service.list()
    return [_build_front_orden(db, orden) for orden in ordenes]


@router.post("", response_model=OrdenFrontendResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def create_orden(payload: OrdenFrontendCreate, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    vehiculo = db.get(Vehiculo, payload.vehiculo.placa)
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vehiculo no encontrado")
    lineas = _normalize_lineas([linea.model_dump() for linea in payload.lineas])
    totals = _calculate_totals(lineas)
    orden = service.create(
        {
            "placa_vehiculo": payload.vehiculo.placa,
            "estado": payload.estado,
            "numero": payload.numero,
            "tipo_servicio": payload.tipoServicio,
            "descripcion": payload.descripcion,
            "prioridad": payload.prioridad,
            "diagnostico": payload.diagnostico,
            "fecha_ingreso": _parse_iso_datetime(payload.fechaCreacion),
            "fecha_entrega": _parse_iso_datetime(payload.fechaLimite),
            "lineas": lineas,
            "inventario_vehiculo": payload.inventarioVehiculo,
            "kilometraje": payload.kilometraje,
            "nivel_combustible": payload.nivelCombustible,
            "estado_vehiculo": payload.estadoVehiculo,
            "notas": [nota.model_dump() for nota in payload.notas],
            "tareas": [tarea.model_dump() for tarea in payload.tareas],
            "subtotal": payload.subtotal if payload.subtotal is not None else totals["subtotal"],
            "descuento": payload.descuento if payload.descuento is not None else totals["descuento"],
            "iva": payload.iva if payload.iva is not None else totals["iva"],
            "total": payload.total if payload.total is not None else totals["total"],
            "tecnico_asignado": payload.tecnicoAsignado.model_dump() if payload.tecnicoAsignado else None,
        }
    )
    return _build_front_orden(db, orden)


@router.put("/{orden_id}", response_model=OrdenFrontendResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def update_orden(orden_id: int, payload: OrdenFrontendUpdate, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    orden = service.get(orden_id)
    updates: dict[str, Any] = {}
    if payload.numero is not None:
        updates["numero"] = payload.numero
    if payload.estado is not None:
        updates["estado"] = payload.estado
    if payload.tipoServicio is not None:
        updates["tipo_servicio"] = payload.tipoServicio
    if payload.descripcion is not None:
        updates["descripcion"] = payload.descripcion
    if payload.fechaCreacion is not None:
        updates["fecha_ingreso"] = _parse_iso_datetime(payload.fechaCreacion)
    if payload.fechaLimite is not None:
        updates["fecha_entrega"] = _parse_iso_datetime(payload.fechaLimite)
    if payload.prioridad is not None:
        updates["prioridad"] = payload.prioridad
    if payload.diagnostico is not None:
        updates["diagnostico"] = payload.diagnostico
    if payload.inventarioVehiculo is not None:
        updates["inventario_vehiculo"] = payload.inventarioVehiculo
    if payload.kilometraje is not None:
        updates["kilometraje"] = payload.kilometraje
    if payload.nivelCombustible is not None:
        updates["nivel_combustible"] = payload.nivelCombustible
    if payload.estadoVehiculo is not None:
        updates["estado_vehiculo"] = payload.estadoVehiculo
    if payload.tecnicoAsignado is not None:
        updates["tecnico_asignado"] = payload.tecnicoAsignado.model_dump()
    if payload.notas is not None:
        updates["notas"] = [nota.model_dump() for nota in payload.notas]
    if payload.tareas is not None:
        updates["tareas"] = [tarea.model_dump() for tarea in payload.tareas]
    if payload.lineas is not None:
        lineas = _normalize_lineas([linea.model_dump() for linea in payload.lineas])
        totals = _calculate_totals(lineas)
        updates["lineas"] = lineas
        updates["subtotal"] = totals["subtotal"]
        updates["descuento"] = totals["descuento"]
        updates["iva"] = totals["iva"]
        updates["total"] = totals["total"]
    if payload.subtotal is not None:
        updates["subtotal"] = payload.subtotal
    if payload.descuento is not None:
        updates["descuento"] = payload.descuento
    if payload.iva is not None:
        updates["iva"] = payload.iva
    if payload.total is not None:
        updates["total"] = payload.total
    updated = service.update(orden.id, updates)
    return _build_front_orden(db, updated)


@router.patch("/{orden_id}", response_model=OrdenFrontendResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def patch_orden(orden_id: int, payload: OrdenFrontendUpdate, db: DbSession):
    return update_orden(orden_id, payload, db)


@router.post("/repuestos", response_model=OrdenRepuestoResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def add_repuesto(payload: OrdenRepuestoCreate, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.add_repuesto(payload.model_dump())


@router.get("/resumen/estados", response_model=list[dict[str, Any]], dependencies=[Depends(require_roles("admin", "mecanico", "gerencia"))])
def resumen_estados(db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    return service.list_resumen()


@router.get("/{orden_id}", response_model=OrdenFrontendResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def get_orden(orden_id: int, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    orden = service.get(orden_id)
    return _build_front_orden(db, orden)


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_orden(orden_id: int, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    service.delete(orden_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{orden_id}/estado", response_model=OrdenFrontendResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def update_estado(orden_id: int, payload: dict[str, str], db: DbSession):
    estado = payload.get("estado")
    if not estado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado requerido")
    service = OrdenesService(OrdenesRepository(db))
    updated = service.update(orden_id, {"estado": estado})
    return _build_front_orden(db, updated)


@router.patch("/{orden_id}/diagnostico", response_model=OrdenFrontendResponse, dependencies=[Depends(require_roles("admin", "mecanico"))])
def update_diagnostico(orden_id: int, payload: dict[str, str], db: DbSession):
    diagnostico = payload.get("diagnostico")
    if diagnostico is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Diagnostico requerido")
    service = OrdenesService(OrdenesRepository(db))
    updated = service.update(orden_id, {"diagnostico": diagnostico})
    return _build_front_orden(db, updated)


@router.post("/{orden_id}/notas", response_model=OrdenNota, dependencies=[Depends(require_roles("admin", "mecanico"))])
def add_nota(orden_id: int, payload: OrdenNota, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    orden = service.get(orden_id)
    notas = list(orden.notas or [])
    notas.insert(0, payload.model_dump())
    service.update(orden_id, {"notas": notas})
    return payload


@router.post("/{orden_id}/lineas", response_model=OrdenLinea, dependencies=[Depends(require_roles("admin", "mecanico"))])
def add_linea(orden_id: int, payload: OrdenLinea, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    orden = service.get(orden_id)
    lineas = list(orden.lineas or [])
    linea = payload.model_dump()
    lineas.append(linea)
    lineas = _normalize_lineas(lineas)
    totals = _calculate_totals(lineas)
    service.update(
        orden_id,
        {
            "lineas": lineas,
            "subtotal": totals["subtotal"],
            "descuento": totals["descuento"],
            "iva": totals["iva"],
            "total": totals["total"],
        },
    )
    return payload


@router.patch("/{orden_id}/lineas/{linea_id}", response_model=OrdenLinea, dependencies=[Depends(require_roles("admin", "mecanico"))])
def update_linea(orden_id: int, linea_id: int, payload: OrdenLinea, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    orden = service.get(orden_id)
    lineas = list(orden.lineas or [])
    updated = None
    for index, linea in enumerate(lineas):
        if int(linea.get("id", 0)) == linea_id:
            updated = payload.model_dump()
            updated["id"] = linea_id
            lineas[index] = updated
            break
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Linea no encontrada")
    lineas = _normalize_lineas(lineas)
    totals = _calculate_totals(lineas)
    service.update(
        orden_id,
        {
            "lineas": lineas,
            "subtotal": totals["subtotal"],
            "descuento": totals["descuento"],
            "iva": totals["iva"],
            "total": totals["total"],
        },
    )
    return OrdenLinea(**updated)


@router.delete("/{orden_id}/lineas/{linea_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin", "mecanico"))])
def delete_linea(orden_id: int, linea_id: int, db: DbSession):
    service = OrdenesService(OrdenesRepository(db))
    orden = service.get(orden_id)
    lineas = [linea for linea in (orden.lineas or []) if int(linea.get("id", 0)) != linea_id]
    lineas = _normalize_lineas(lineas)
    totals = _calculate_totals(lineas)
    service.update(
        orden_id,
        {
            "lineas": lineas,
            "subtotal": totals["subtotal"],
            "descuento": totals["descuento"],
            "iva": totals["iva"],
            "total": totals["total"],
        },
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
