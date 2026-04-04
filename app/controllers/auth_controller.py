from fastapi import APIRouter

from app.core.security import keycloak_oidc
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    return await auth_service.login(payload.username, payload.password)


@router.get("/keycloak/status")
async def keycloak_status():
    return {
        "issuer": keycloak_oidc.issuer,
        "token_endpoint": keycloak_oidc.token_endpoint,
        "status": "ok" if keycloak_oidc.issuer else "not_initialized",
    }
