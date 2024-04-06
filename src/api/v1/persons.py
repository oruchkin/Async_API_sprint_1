from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.v1.films import Film
from services.person import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str


@router.get('/search', response_model=list[Person], summary="Поиск по персонам")
async def search_persons(person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    return []


@router.get(
        '/{person_id}',
        response_model=Person,
        summary="Данные по персоне")
async def get_person(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')


@router.get('/{person_id}/films', response_model=list[Film], summary="Фильмы по персоне")
async def list_person_films(person_service: PersonService = Depends(get_person_service)) -> list[Film]:
    return []

