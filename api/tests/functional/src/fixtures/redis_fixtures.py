import pytest_asyncio
from redis.asyncio import Redis

from ..settings import RedisSettings


@pytest_asyncio.fixture(scope="function")
async def redis_client():
    redis_settings = RedisSettings()
    redis_client = Redis(host=redis_settings.host, port=redis_settings.port, decode_responses=True)
    yield redis_client
    await redis_client.aclose()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_cache(redis_client: Redis):
    yield
    # never use .keys in prod!
    keys = await redis_client.keys()
    for key in keys:
        await redis_client.delete(key)
