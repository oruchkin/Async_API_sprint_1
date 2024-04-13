from abc import ABC
from typing import Any, Literal, cast
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

INDICES = Literal["movies", "persons", "genres"]


class ServiceABC(ABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def _get_from_elastic(self, index: INDICES, id: UUID) -> dict | None:
        try:
            data = await self.elastic.get(index=index, id=id)
            return cast(dict, data)["_source"]
        except NotFoundError:
            return None

    async def _query_from_elastic(self, index: INDICES, query: dict, size: int = 1000, skip: int = 0) -> list[Any]:
        data = await self.elastic.search(index=index, body={"query": query, "size": size, "from": skip})
        docs = cast(dict, data)["hits"]["hits"]
        return [doc["_source"] for doc in docs]
