from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Callable, TypeVar

from fastapi.encoders import jsonable_encoder

from app.core.config import get_settings

try:
    import redis
except ImportError:  # pragma: no cover - cache becomes a no-op if the package is absent
    redis = None

T = TypeVar("T")


class RedisCache:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = bool(self.settings.CACHE_ENABLED and redis is not None)
        self.client = None
        if self.enabled:
            try:
                self.client = redis.Redis.from_url(
                    self.settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                )
                self.client.ping()
            except Exception:
                self.enabled = False
                self.client = None

    def get_json(self, key: str) -> Any | None:
        if not self.enabled or self.client is None:
            return None
        cached_value = self.client.get(key)
        if cached_value is None:
            return None
        return json.loads(cached_value)

    def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        if not self.enabled or self.client is None:
            return
        payload = json.dumps(jsonable_encoder(value), ensure_ascii=False)
        ttl = ttl_seconds or self.settings.CACHE_DEFAULT_TTL
        self.client.setex(key, ttl, payload)

    def cached(self, key: str, loader: Callable[[], T], ttl_seconds: int | None = None) -> T:
        cached_value = self.get_json(key)
        if cached_value is not None:
            return cached_value

        value = loader()
        self.set_json(key, value, ttl_seconds)
        return value


@lru_cache
def get_cache() -> RedisCache:
    return RedisCache()


cache_store = get_cache()