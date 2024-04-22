import json
import os
from typing import Any

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from .settings import ElasticsearchSettings, FastAPISettings


@pytest_asyncio.fixture(name="es_client", scope="session")
async def es_client():
    es_esttings = ElasticsearchSettings()
    es_client = AsyncElasticsearch(hosts=es_esttings.url, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name="http_client")
async def http_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(name="es_write_data")
def es_write_data(es_client):
    async def inner(data: list[dict]):
        if await es_client.indices.exists(index="movies"):
            await es_client.indices.delete(index="movies")
        await es_client.indices.create(index="movies", body=_get_schema("movies"))

        await async_bulk(client=es_client, actions=data)

    return inner


@pytest_asyncio.fixture(name="make_get_request")
def make_get_request(http_client):
    api_settings = FastAPISettings()

    async def inner(path: str, query_data: dict):
        url = api_settings.url + path
        async with http_client.get(url, params=query_data) as response:
            body = await response.json()
            return (response, body)

    return inner


def _get_schema(index: str) -> Any:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/testdata/schemas/{index}.json", "r") as fp:
        return json.load(fp)
