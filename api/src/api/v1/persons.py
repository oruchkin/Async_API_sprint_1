import asyncio
from http import HTTPStatus
from typing import get_args
from uuid import UUID

from api.v1.films import Film
from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import Film as FilmModel
from pydantic import BaseModel
from services.film import PERSON_ROLE, FilmService, get_film_service
from services.person import PersonService, get_person_service
from services.person_film import PersonFilmService, get_person_film_service

router = APIRouter()


class PersonFilm(BaseModel):
    uuid: UUID
    roles: list[str]


class Person(BaseModel):
    id: str
    full_name: str
    films: list[PersonFilm]


@router.get("/search", response_model=list[Person], summary="Поиск по персонам")
async def search_persons(
    query: str = Query(..., description="Search string"),
    page_number: int | None = Query(..., description="Page number [1, N], default 1"),
    page_size: int | None = Query(..., description="Page size [1, 100], default 50"),
    person_service: PersonService = Depends(get_person_service),
) -> list[Person]:
    entities = await person_service.find(query, page_number or 1, page_size or 50)
    return [Person(id=person.id, full_name=person.full_name, films=[]) for person in entities]


@router.get("/{person_id}", response_model=Person, summary="Данные по персоне")
async def get_person(
    person_id: UUID,
    person_film_service: PersonFilmService = Depends(get_person_film_service),
) -> Person:
    (person, films) = await person_film_service.get_person_with_films(person_id)
    if person:
        model = Person(id=person.id, full_name=person.full_name, films=[])
        model.films = [_extract_film_details(film, person_id) for film in films]
        return model

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")


@router.get("/{person_id}/films", response_model=list[Film], summary="Фильмы по персоне")
async def list_person_films(person_id: UUID, film_service: FilmService = Depends(get_film_service)) -> list[Film]:
    entities = await film_service.find_by_person(person_id)
    return [Film(**film.model_dump()) for film in entities]


def _extract_film_details(film: FilmModel, person_id: UUID) -> PersonFilm:
    all_roles = get_args(PERSON_ROLE)
    roles = [role for role in all_roles if any(r.id == person_id for r in getattr(film, role))]
    return PersonFilm(uuid=film.id, roles=roles)
