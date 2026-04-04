from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.security import KeycloakAuthMiddleware, keycloak_oidc

settings = get_settings()

app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
async def startup_event() -> None:
    try:
        await keycloak_oidc.discover()
    except Exception as exc:
        print(f"No se pudo inicializar Keycloak al iniciar: {exc}")


app.add_middleware(
    KeycloakAuthMiddleware,
    exclude_paths={"/health", "/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json", "/auth/login"},
)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse(content={"status": "ok"})


app.include_router(api_router)
