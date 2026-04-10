from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Gestor Taller Automotriz API"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str

    KEYCLOAK_SERVER_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_AUDIENCE: str | None = None

    KAFKA_ENABLED: bool = False
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CLIENT_ID: str = "gestor-talleres-api"
    KAFKA_TOPIC_PREFIX: str = "talleres"
    KAFKA_METRICS_ENABLED: bool = True
    KAFKA_METRICS_CONSUMER_GROUP: str = "gestor-talleres-metricas"
    KAFKA_AUTO_OFFSET_RESET: str = "latest"


@lru_cache
def get_settings() -> Settings:
    return Settings()
