from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


@router.get("/", response_model=list[Film])
async def list_films(film_service: FilmService = Depends(get_film_service)) -> list[Film]:
    return []


@router.get("/search", response_model=list[Film])
async def search_films(film_service: FilmService = Depends(get_film_service)) -> list[Film]:
    return []


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film, summary="Полная информация по фильму")
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> Film:
    if film := await film_service.get_by_id(film_id):
        return Film(id=film.id, title=film.title, imdb_rating=film.imdb_rating)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
