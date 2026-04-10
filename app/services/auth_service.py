from fastapi import HTTPException

from app.core.kafka_events import publish_domain_event
from app.core.security import keycloak_oidc


class AuthService:
    async def login(self, username: str, password: str) -> dict:
        try:
            token = await keycloak_oidc.login(username, password)
            publish_domain_event(
                topic_suffix="auth",
                event_type="login_exitoso",
                payload={"username": username},
            )
            return token
        except HTTPException as exc:
            publish_domain_event(
                topic_suffix="auth",
                event_type="login_fallido",
                payload={"username": username, "detalle": str(exc.detail)},
            )
            raise
