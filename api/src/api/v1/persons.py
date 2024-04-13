from http import HTTPStatus
from uuid import UUID

from api.v1.films import Film
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str


@router.get("/search", response_model=list[Person], summary="Поиск по персонам")
async def search_persons(person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    return []


@router.get("/{person_id}", response_model=Person, summary="Данные по персоне")
async def get_person(person_id: UUID, person_service: PersonService = Depends(get_person_service)) -> Person:
    if entity := await person_service.get_by_id(person_id):
        return Person(id=entity.id, full_name=entity.full_name)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")


@router.get("/{person_id}/films", response_model=list[Film], summary="Фильмы по персоне")
async def list_person_films(person_id: UUID, film_service: FilmService = Depends(get_film_service)) -> list[Film]:
    entities = await film_service.find_by_person(person_id)
    return [Film(**film.model_dump()) for film in entities]
