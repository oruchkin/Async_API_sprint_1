from functools import lru_cache
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre
from redis.asyncio import Redis
from services.base import ServiceABC

CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService(ServiceABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

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
        cache_key = f"genres:{genre_id}"
        if genre := await self._from_cache(cache_key):
            return genre

        if doc := await self._get_from_elastic("genres", genre_id):
            genre = Genre(**doc)
            await self._put_to_cache(cache_key, genre)
            return genre

    async def _from_cache(self, key: str) -> Genre | None:
        if data := await self.redis.get(key):
            return Genre.model_validate_json(data)

    async def _put_to_cache(self, key: str, entity: Genre):
        value = entity.model_dump_json()
        await self.redis.set(key, value, CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
