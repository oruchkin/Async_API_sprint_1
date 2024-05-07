from redis.asyncio import Redis
from services.cache.none_storage import NoneCache
from services.cache.redis_storage import RedisCache
from services.cache.storage import ICache

redis: Redis | None = None


def get_redis() -> Redis:
    global redis
    if not redis:
        raise ValueError("Redis is not setup")

    return redis


def get_cache() -> ICache:
    # In future we can move it to different location
    # but as we don't have any other implementations
    # of the cache provider let's keep it here.
    global redis
    if redis is None:
        return NoneCache()

    return RedisCache(redis)
