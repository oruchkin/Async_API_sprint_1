from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    title: str


@router.get('/', response_model=list[Genre], summary="Список жанров")
async def list_genres(genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:
    return []


@router.get(
        '/{genre_id}',
        response_model=Genre,
        summary="Данные по конкретному жанру")
async def film_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
