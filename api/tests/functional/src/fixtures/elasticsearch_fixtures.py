import json
import os
from typing import Any

import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from ..settings import ElasticsearchSettings


@pytest_asyncio.fixture(scope="function")
async def es_client():
    es_esttings = ElasticsearchSettings()
    es_client = AsyncElasticsearch(hosts=es_esttings.url, verify_certs=False)
    yield es_client
    await es_client.close()


def _get_schema(index: str) -> Any:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(current_dir)
    with open(f"{parent_dir}/testdata/schemas/{index}.json", "r") as fp:
        return json.load(fp)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_data(es_client: AsyncElasticsearch):
    yield
    indices = await es_client.indices.get_alias(index="*")
    for index in indices:
        await es_client.indices.delete(index=index)


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], index: str):
        indices = await es_client.indices.get_alias(index="*")
        if index not in indices:
            await es_client.indices.create(index=index, body=_get_schema(index))

        await async_bulk(client=es_client, actions=data, refresh="wait_for")

    return inner
