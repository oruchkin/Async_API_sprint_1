from functools import lru_cache
from uuid import UUID

from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.person import Person
from services.base import ServiceABC


class PersonService(ServiceABC):
    def __init__(self, elastic: AsyncElasticsearch):
        super().__init__(elastic)

    async def get_by_id(self, person_id: UUID) -> Person | None:
        if doc := await self._get_from_elastic("persons", person_id):
            return Person(**doc)

    async def search(self, search: str, page_number: int = 1, page_size: int = 50) -> list[Person]:
        query = {"bool": {"must": [{"match": {"full_name": search}}]}}
        entities = await self._query_from_elastic("persons", query, page_size, (page_number - 1) * page_size)
        return [Person(**doc) for doc in entities]


@lru_cache()
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(elastic)
