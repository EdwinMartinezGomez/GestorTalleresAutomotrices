from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.api.deps import DbSession
from app.core.security import require_roles
from app.repositories.clientes_repository import ClientesRepository
from app.schemas.clientes import ClienteCreate, ClienteResponse, ClienteUpdate
from app.services.clientes_service import ClientesService

router = APIRouter()


@router.get("", response_model=list[ClienteResponse])
def list_clientes(db: DbSession):
    service = ClientesService(ClientesRepository(db))
    return service.list()


@router.get("/{cliente_id}", response_model=ClienteResponse)
def get_cliente(cliente_id: UUID, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    return service.get(cliente_id)


@router.post("", response_model=ClienteResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def create_cliente(payload: ClienteCreate, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    return service.create(payload.model_dump())


@router.put("/{cliente_id}", response_model=ClienteResponse, dependencies=[Depends(require_roles("admin", "recepcionista"))])
def update_cliente(cliente_id: UUID, payload: ClienteUpdate, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    updates = payload.model_dump(exclude_none=True)
    return service.update(cliente_id, updates)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_roles("admin"))])
def delete_cliente(cliente_id: UUID, db: DbSession):
    service = ClientesService(ClientesRepository(db))
    service.delete(cliente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
