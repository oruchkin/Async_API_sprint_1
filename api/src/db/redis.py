from typing import Optional

from redis.asyncio import Redis
from core.settings import RedisSettings

redis: Optional[Redis] = None


def get_redis() -> Redis:
    global redis
    if redis is None:
        settings = RedisSettings()
        redis = Redis(host=settings.host, port=settings.port, decode_responses=True)

    return redis
