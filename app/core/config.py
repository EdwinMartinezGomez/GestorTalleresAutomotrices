from functools import lru_cache

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Gestor Taller Automotriz API"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str

    REDIS_URL: str = "redis://10.200.2.253:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_DEFAULT_TTL: int = 60

    CORS_ALLOW_ORIGINS: str = "*"

    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_AUDIENCE: str | None = None

    KAFKA_ENABLED: bool = False
    KAFKA_BOOTSTRAP_SERVERS: str = "10.200.2.253:9092"
    KAFKA_CLIENT_ID: str = "gestor-talleres-api"
    KAFKA_TOPIC_PREFIX: str = "talleres"
    KAFKA_METRICS_ENABLED: bool = True
    KAFKA_METRICS_CONSUMER_GROUP: str = "gestor-talleres-metricas"
    KAFKA_AUTO_OFFSET_RESET: str = "latest"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        # In this project, .env must be the source of truth for local configuration.
        return init_settings, dotenv_settings, env_settings, file_secret_settings


@lru_cache
def get_settings() -> Settings:
    return Settings()
