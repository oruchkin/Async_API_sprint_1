from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.film import FilmService, get_film_service
from typing import Annotated
from fastapi import Query

router = APIRouter()


class Film(BaseModel):
    id: UUID
    title: str
    imdb_rating: float


@router.get("/", response_model=list[Film])
async def list_films(
        page_number: int = Query(1, description="Page number [1, N]", ge=1),
        page_size: int = Query(10, description="Page size [1, 100]", ge=1, le=100),
        film_service: FilmService = Depends(get_film_service)
) -> list[Film]:
    films = await film_service.get_all_films(page_number, page_size)
    return films


# @router.get("/search", response_model=list[Film])
# async def search_films(film_service: FilmService = Depends(get_film_service)) -> list[Film]:
#     return []

@router.get("/search", response_model=list[Film])
async def search_films(
        query: str = Query(None, description="Search query string"),
        page_number: int = Query(1, description="Page number", ge=1),
        page_size: int = Query(10, description="Page size", ge=1, le=100),
        film_service: FilmService = Depends(get_film_service)
) -> list[Film]:
    if not query:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Query string is required for search.")
    return await film_service.search_films(query, page_number, page_size)


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film, summary="Полная информация по фильму")
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> Film:
    if film := await film_service.get_by_id(film_id):
        return Film(id=film.id, title=film.title, imdb_rating=film.imdb_rating)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
