from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis

redis: Optional[Redis] = None


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    host: str = "127.0.0.1"
    port: int = 6379


def get_redis() -> Redis:
    global redis
    if redis is None:
        settings = RedisSettings()
        redis = Redis(host=settings.host, port=settings.port, decode_responses=True)

    return redis
