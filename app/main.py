import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn

# Permite ejecutar este archivo directamente sin perder el contexto del paquete.
if __package__ is None or __package__ == "":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from app.api.routes import api_router
from app.core.database import engine, sync_legacy_schema
from app.core.config import get_settings
from app.core.kafka_events import event_publisher
from app.core.kafka_metrics import kafka_metrics_consumer
from app.core.security import KeycloakAuthMiddleware, keycloak_oidc
from app.entities.base import Base
from app.entities import models  # noqa: F401

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.APP_ENV.lower() == "development":
        # Crea tablas base si no existen (entornos locales sin script SQL).
        try:
            Base.metadata.create_all(bind=engine)
            sync_legacy_schema()
        except Exception as exc:
            print(f"No se pudo crear/sincronizar esquema al iniciar: {exc}")
    try:
        await keycloak_oidc.discover()
    except Exception as exc:
        print(f"No se pudo inicializar Keycloak al iniciar: {exc}")
    kafka_metrics_consumer.start()
    yield
    kafka_metrics_consumer.stop()
    event_publisher.close()


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


app.add_middleware(
    KeycloakAuthMiddleware,
    exclude_paths={"/health", "/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json", "/auth/login"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=False)
