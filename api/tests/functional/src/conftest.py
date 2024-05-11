import json
import logging
import os
import urllib.parse
from typing import Any

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from .settings import ElasticsearchSettings, FastAPISettings, RedisSettings

logger = logging.getLogger(__name__)


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


@pytest_asyncio.fixture(scope="function")
async def es_client():
    es_esttings = ElasticsearchSettings()
    es_client = AsyncElasticsearch(hosts=es_esttings.url, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope="function")
async def http_client():
    # timout is required as if something goes wrong script will just hang
    session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
    session = aiohttp.ClientSession(timeout=session_timeout)
    yield session
    await session.close()


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], index: str):
        indices = await es_client.indices.get_alias(index="*")
        if index not in indices:
            await es_client.indices.create(index=index, body=_get_schema(index))

        await async_bulk(client=es_client, actions=data, refresh="wait_for")

    return inner


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_data(es_client: AsyncElasticsearch):
    yield
    indices = await es_client.indices.get_alias(index="*")
    for index in indices:
        await es_client.indices.delete(index=index)


def encode_url(url: str, path: str, query: dict | None = None) -> str:
    if query is None:
        return url + path

    params = urllib.parse.urlencode(query, quote_via=urllib.parse.quote)
    return url + path + f"?{params}"


@pytest_asyncio.fixture()
def make_get_request(http_client: aiohttp.ClientSession):
    api_settings = FastAPISettings()

    async def inner(path: str, query_data: dict | None = None):
        # aiohttp.get encodes query parameters in really silly way
        # thinking that it's form data (application/x-www-form-urlencoded).
        # Specifically it encodes whitespace as + instead of %20.
        # So we have to do it manually
        url = encode_url(api_settings.url, path, query_data)
        async with http_client.get(url) as response:
            body = await response.json()
            if response.status >= 500:
                raise ValueError(body)

            return response.status, body

    return inner


def _get_schema(index: str) -> Any:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/testdata/schemas/{index}.json", "r") as fp:
        return json.load(fp)
