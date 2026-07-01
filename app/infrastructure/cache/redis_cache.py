import json
from typing import Any

import redis.asyncio as redis

from app.domain.repositories.cache_client import CacheClient


class RedisCacheClient(CacheClient):
    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        payload = value if isinstance(value, str) else json.dumps(value)
        await self._redis.set(key, payload, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def close(self) -> None:
        await self._redis.close()
