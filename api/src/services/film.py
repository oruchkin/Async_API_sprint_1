from collections import defaultdict
from collections.abc import Collection
from functools import lru_cache
from typing import Literal, get_args
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from redis.asyncio import Redis
from services.base import ServiceABC

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

PERSON_ROLE = Literal["directors", "actors", "writers"]


class FilmService(ServiceABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        super().__init__(elastic)
        self.redis = redis

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

    async def find_by_all_persons(self, person_ids: list[UUID]) -> dict[UUID, list[Film]]:
        subqueries = [FilmService._construct_find_by_all_persons_subquery(person_ids, m) for m in get_args(PERSON_ROLE)]
        data = await self._query_from_elastic("movies", {"bool": {"should": subqueries}})
        films = [Film(**doc) for doc in data]
        return FilmService._group_by_person(films, person_ids)

    async def find_by_person(self, person_id: UUID) -> list[Film]:
        """
        Search for films by person took part in production
        """
        subqueries = [FilmService._construct_find_by_person_subquery(person_id, m) for m in get_args(PERSON_ROLE)]
        data = await self._query_from_elastic("movies", {"bool": {"should": subqueries}})
        return [Film(**doc) for doc in data]

    @staticmethod
    def _construct_find_by_all_persons_subquery(person_ids: Collection[UUID], property: str) -> dict:
        return {
            "nested": {"path": property, "query": {"bool": {"should": [{"terms": {f"{property}.id": person_ids}}]}}}
        }

    @staticmethod
    def _construct_find_by_person_subquery(person_id: UUID, property: str) -> dict:
        return {"nested": {"path": property, "query": {"bool": {"should": [{"match": {f"{property}.id": person_id}}]}}}}

    @staticmethod
    def _group_by_person(films: list[Film], persons: Collection[UUID]) -> dict[UUID, list[Film]]:
        person_films = defaultdict(list)
        for film in films:
            ids = FilmService._extract_persons(film)
            for person in ids.intersection(persons):
                person_films[person].append(film)

        return person_films

    @staticmethod
    def _extract_persons(film: Film) -> set[UUID]:
        person_ids: set[UUID] = set()
        for attr in get_args(PERSON_ROLE):
            role_persons = [p.id for p in getattr(film, attr)]
            person_ids.update(role_persons)

        return person_ids

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
