from collections import defaultdict
from collections.abc import Collection
from functools import lru_cache
from typing import Literal, get_args
from uuid import UUID

from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from services.base import ServiceABC

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

PERSON_ROLE = Literal["directors", "actors", "writers"]


class FilmService(ServiceABC):
    def __init__(self, elastic: AsyncElasticsearch):
        super().__init__(elastic)

    async def search_films(self, query: str, page_number: int = 1, page_size: int = 10) -> list[Film]:
        """Поиск фильмов по текстовому запросу и фильтрам."""
        search_query = {"bool": {"must": [{"match": {"title": {"query": query, "fuzziness": "AUTO"}}}]}}
        from_index = (page_number - 1) * page_size
        films_data = await self._query_from_elastic("movies", search_query, size=page_size, skip=from_index)
        return [Film(**film) for film in films_data]

    async def get_all_films(
        self, page_number: int, page_size: int, genre: UUID | None = None, sort: dict[str, int] | None = None
    ) -> list[Film]:
        """Возвращает все фильмы из базы."""

        from_index = (page_number - 1) * page_size
        query = {"match_all": {}}

        if genre:
            if genre_record := await self._get_from_elastic("genres", genre):
                query = {"bool": {"filter": [{"term": {"genres": genre_record["name"]}}]}}

        films_data = await self._query_from_elastic("movies", query, size=page_size, skip=from_index, sort=sort)

        prepared_films = []
        for film in films_data:
            if film.get("imdb_rating") is None:
                film["imdb_rating"] = 0
            prepared_films.append(Film(**film))
        return prepared_films

    async def get_by_id(self, film_id: UUID) -> Film | None:
        """
        get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
        """
        if doc := await self._get_from_elastic("movies", film_id):
            return Film(**doc)

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


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
