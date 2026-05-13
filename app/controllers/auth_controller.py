from fastapi import APIRouter, HTTPException, status

from app.core.security import keycloak_oidc
from app.schemas.auth import ForgotPasswordRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    username = payload.username or payload.email
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debe enviar username o email")
    return await auth_service.login(username, payload.password)


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(_: ForgotPasswordRequest):
    return None


@router.get("/keycloak/status")
async def keycloak_status():
    return {
        "issuer": keycloak_oidc.issuer,
        "token_endpoint": keycloak_oidc.token_endpoint,
        "status": "ok" if keycloak_oidc.issuer else "not_initialized",
    }
