from app.core.security import keycloak_oidc


class AuthService:
    async def login(self, username: str, password: str) -> dict:
        return await keycloak_oidc.login(username, password)
