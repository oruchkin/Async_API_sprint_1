from functools import lru_cache
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from redis.asyncio import Redis
from services.base import ServiceABC

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService(ServiceABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(redis, elastic)

    async def get_by_id(self, film_id: UUID) -> Film | None:
        """
        get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
        """
        cache_key = f"movies:{film_id}"
        if film := await self._film_from_cache(cache_key):
            return film

        if doc := await self._get_from_elastic("movies", film_id):
            film = Film(**doc)
            await self._put_film_to_cache(cache_key, film)
            return film

    async def _film_from_cache(self, key: str) -> Film | None:
        if data := await self.redis.get(key):
            return Film.model_validate_json(data)

    async def _put_film_to_cache(self, key: str, film: Film):
        value = film.model_dump_json()
        await self.redis.set(key, value, FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
