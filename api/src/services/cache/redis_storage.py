from typing import Any

from redis.asyncio import Redis

from .storage import ICache


class RedisCache(ICache):
    def __init__(self, client: Redis):
        self._client = client

    async def set(self, key: str, value: Any, timeout_sec: int) -> None:
        await self._client.set(key, value, timeout_sec)

    async def get(self, key: str) -> Any:
        return await self._client.get(key)
