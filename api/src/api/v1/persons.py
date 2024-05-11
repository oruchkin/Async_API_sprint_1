import logging
from http import HTTPStatus
from typing import Annotated, get_args
from uuid import UUID

from api.v1.films import Film
from api.v1.schemas.person import Person, PersonFilm
from api.v1.schemas.pagination import PaginatedParams
from db.redis import get_cache
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from models.film import Film as FilmModel
from models.person import Person as PersonModel
from pydantic import TypeAdapter
from services.cache.storage import ICache
from services.film import PERSON_ROLE, FilmService, get_film_service
from services.person_film import PersonFilmService, get_person_film_service

router = APIRouter()


logger = logging.getLogger(__name__)


@router.get("/search",
            response_model=list[Person],
            summary="Поиск по персонам",
            description="Возвращает список персон по поисковому запросу")
async def search_persons(
    response: Response,
    query: str = Query(..., min_length=3, description="Search string"),
    pagination: PaginatedParams = Depends(),
    person_film_service: PersonFilmService = Depends(get_person_film_service),
    cache: ICache = Depends(get_cache),
) -> list[Person]:
    key = f"persons:{query}:{pagination.page_number}:{pagination.page_size}"
    adapter = TypeAdapter(list[Person])
    if cached := await cache.get(key):
        return adapter.validate_json(cached)

    logger.debug("Persons search cache missed")
    entities = await person_film_service.search(query, pagination.page_number or 1, pagination.page_size or 50)
    persons = [_construct_person_films(person, films) for (person, films) in entities]
    cached = adapter.dump_json(persons)
    await cache.set(key, cached, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return persons


@router.get("/{person_id}",
            response_model=Person,
            summary="Данные по персоне",
            description="Возвращает подробную информацию о персоне")
async def get_person(
    person_id: UUID, person_film_service: PersonFilmService = Depends(get_person_film_service)
) -> Person:
    (person, films) = await person_film_service.get_person_with_films(person_id)
    if person:
        return _construct_person_films(person, films)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")


@router.get("/{person_id}/films",
            response_model=list[Film],
            summary="Фильмы по персоне",
            description="Возвращает список фильмов, в которых участвовала персона")
async def list_person_films(
    response: Response,
    person_id: UUID,
    film_service: FilmService = Depends(get_film_service),
    cache: ICache = Depends(get_cache),
) -> list[Film]:
    key = f"persons:{person_id}:films"
    adapter = TypeAdapter(list[Film])
    if cached := await cache.get(key):
        return adapter.validate_json(cached)

    logger.debug(f"Person films cache missed {person_id}")
    entities = await film_service.find_by_person(person_id)
    films_list = [Film(**film.model_dump()) for film in entities]
    cached = adapter.dump_json(films_list)
    await cache.set(key, cached, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return films_list


def _construct_person_films(person: PersonModel, films: list[FilmModel]) -> Person:
    """Construct Person model with films"""
    model = Person.model_validate(person)
    model.films = [_extract_film_details(film, person.id) for film in films]
    return model


def _extract_film_details(film: FilmModel, person_id: UUID) -> PersonFilm:
    all_roles = get_args(PERSON_ROLE)
    roles = [role for role in all_roles if any(r.id == person_id for r in getattr(film, role))]
    return PersonFilm(uuid=film.id, roles=roles)
