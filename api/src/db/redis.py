from core.settings import RedisSettings
from redis.asyncio import Redis

redis: Redis | None = None


def get_redis() -> Redis:
    global redis
    if redis is None:
        settings = RedisSettings()
        redis = Redis(host=settings.host, port=settings.port, decode_responses=True)

    return redis
