from functools import lru_cache
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.person import Person
from redis.asyncio import Redis
from services.base import ServiceABC

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService(ServiceABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    async def get_by_id(self, person_id: UUID) -> Person | None:
        cache_key = f"persons:{person_id}"
        if person := await self._from_cache(cache_key):
            return person

        if doc := await self._get_from_elastic("persons", person_id):
            person = Person(**doc)
            await self._put_to_cache(cache_key, person)
            return person

    async def search(self, search: str, page_number: int = 1, page_size: int = 50) -> list[Person]:
        query = {"bool": {"must": [{"match": {"full_name": search}}]}}
        entities = await self._query_from_elastic("persons", query, page_size, (page_number - 1) * page_size)
        return [Person(**doc) for doc in entities]

    async def _from_cache(self, key: str) -> Person | None:
        if data := await self.redis.get(key):
            return Person.model_validate_json(data)

    async def _put_to_cache(self, key: str, entity: Person):
        value = entity.model_dump_json()
        await self.redis.set(key, value, CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
