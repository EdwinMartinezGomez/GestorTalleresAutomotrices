from fastapi import APIRouter

from app.controllers.auth_controller import router as auth_router
from app.controllers.clientes_controller import router as clientes_router
from app.controllers.historial_controller import router as historial_router
from app.controllers.inventario_controller import router as inventario_router
from app.controllers.ordenes_controller import router as ordenes_router
from app.controllers.pagos_controller import router as pagos_router
from app.controllers.reportes_controller import router as reportes_router
from app.controllers.vehiculos_controller import router as vehiculos_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(clientes_router, prefix="/clientes", tags=["clientes"])
api_router.include_router(vehiculos_router, prefix="/vehiculos", tags=["vehiculos"])
api_router.include_router(inventario_router, prefix="/inventario", tags=["inventario"])
api_router.include_router(ordenes_router, prefix="/ordenes", tags=["ordenes"])
api_router.include_router(pagos_router, prefix="/pagos", tags=["pagos"])
api_router.include_router(historial_router, prefix="/historial", tags=["historial"])
api_router.include_router(reportes_router, prefix="/reportes", tags=["reportes"])
