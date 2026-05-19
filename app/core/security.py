from collections.abc import Callable
import asyncio
from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx
from fastapi import HTTPException, Request, status
from keycloak import KeycloakOpenID
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings

settings = get_settings()


def _normalize_keycloak_server_url(raw_url: str) -> str:
    parsed = urlparse(raw_url.rstrip("/"))
    path = parsed.path.rstrip("/")
    if not path:
        path = "/auth"
    return urlunparse(parsed._replace(path=path)).rstrip("/")


class KeycloakOIDC:
    def __init__(self) -> None:
        server_url = _normalize_keycloak_server_url(settings.KEYCLOAK_SERVER_URL)
        self.client = KeycloakOpenID(
            server_url=server_url.rstrip("/") + "/",
            client_id=settings.KEYCLOAK_CLIENT_ID,
            realm_name=settings.KEYCLOAK_REALM,
            client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
        )
        self.issuer: str | None = None
        self.token_endpoint: str | None = None

    async def discover(self) -> None:
        server_url = _normalize_keycloak_server_url(settings.KEYCLOAK_SERVER_URL)
        url = f"{server_url.rstrip('/')}" \
              f"/realms/{settings.KEYCLOAK_REALM}/.well-known/openid-configuration"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        self.issuer = data["issuer"]
        self.token_endpoint = data["token_endpoint"]

    def _decode_token_sync(self, token: str) -> dict[str, Any]:
        payload = self.client.decode_token(token)

        expected_aud = settings.KEYCLOAK_AUDIENCE
        if expected_aud:
            token_aud = payload.get("aud")
            if isinstance(token_aud, str):
                token_aud_values = {token_aud}
            elif isinstance(token_aud, list):
                token_aud_values = set(token_aud)
            else:
                token_aud_values = set()

            if expected_aud not in token_aud_values:
                raise ValueError("Token audience invalida")

        return payload

    async def verify_token(self, token: str) -> dict[str, Any]:
        if not self.issuer:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Servicio de autenticacion no disponible")

        try:
            return await asyncio.to_thread(self._decode_token_sync, token)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido o expirado") from exc

    def _token_sync(self, username: str, password: str) -> dict[str, Any]:
        return self.client.token(username, password)

    async def login(self, username: str, password: str) -> dict[str, Any]:
        if not self.token_endpoint:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Servicio de autenticacion no disponible")

        try:
            token_data = await asyncio.to_thread(self._token_sync, username, password)
            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in"),
                "token_type": token_data.get("token_type"),
            }
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas o Keycloak no disponible") from exc


keycloak_oidc = KeycloakOIDC()


def extract_roles(payload: dict[str, Any]) -> set[str]:
    realm_roles = {str(role).lower() for role in payload.get("realm_access", {}).get("roles", [])}
    client_roles = {
        str(role).lower()
        for role in payload.get("resource_access", {}).get(settings.KEYCLOAK_CLIENT_ID, {}).get("roles", [])
    }
    return realm_roles.union(client_roles)


def has_client_role(token_info: dict[str, Any], client_id: str, required_role: str) -> bool:
    try:
        roles = token_info["resource_access"][client_id]["roles"]
        return required_role in roles
    except KeyError:
        return False


class KeycloakAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: set[str] | None = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or set()

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Token requerido"})

        try:
            token = auth_header.split(" ", maxsplit=1)[1]
            payload = await keycloak_oidc.verify_token(token)
            request.state.user = payload
            request.state.roles = extract_roles(payload)
            return await call_next(request)
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def require_roles(*required_roles: str) -> Callable:
    def checker(request: Request) -> None:
        user_roles = getattr(request.state, "roles", set())
        normalized_required = {str(role).lower() for role in required_roles}
        if normalized_required and not normalized_required.intersection(user_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para este recurso")

    return checker
