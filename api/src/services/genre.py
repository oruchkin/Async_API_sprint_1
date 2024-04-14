from functools import lru_cache
from uuid import UUID

from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre
from services.base import ServiceABC

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService(ServiceABC):
    def __init__(self, elastic: AsyncElasticsearch):
        super().__init__(elastic)

    async def get_all(self) -> list[Genre]:
        """
        Get all available genres
        """
        docs = await self._query_from_elastic("genres", {"match_all": {}})
        return [Genre(**doc) for doc in docs]

    async def get_by_id(self, genre_id: UUID) -> Genre | None:
        """
        Get single genre by id
        """
        if doc := await self._get_from_elastic("genres", genre_id):
            return Genre(**doc)


@lru_cache()
def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(elastic)
