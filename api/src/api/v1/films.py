from http import HTTPStatus
from typing import Literal, Optional
from uuid import UUID

from api.v1.schemas.film import Film
from db.redis import get_redis
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import TypeAdapter
from redis import Redis
from services.film import FilmService, get_film_service

router = APIRouter()


SORT_OPTION = Literal["imdb_rating", "-imdb_rating"]


@router.get("/", response_model=list[Film])
async def list_films(
    response: Response,
    page_number: int = Query(1, description="Page number [1, N]", ge=1),
    page_size: int = Query(10, description="Page size [1, 100]", ge=1, le=100),
    genre: Optional[UUID] = Query(None, description="Films by genre"),
    sort: Optional[SORT_OPTION] = Query(None, description="Sorting options"),
    film_service: FilmService = Depends(get_film_service),
    redis: Redis = Depends(get_redis),
) -> list[Film]:
    key = f"films:{page_number}:{page_size}:{genre}:{sort}"
    adapter = TypeAdapter(list[Film])
    if cache := await redis.get(key):
        return adapter.validate_json(cache)

    sort_object: dict[str, int] | None = None
    if sort:
        sort_object = {}
        for item in [sort]:
            if item[0] == "-":
                sort_object[item[1:]] = -1
            else:
                sort_object[item] = 1
    films = await film_service.get_all_films(page_number, page_size, genre, sort_object)
    mapped = [Film.model_validate(film) for film in films]
    cache = adapter.dump_json(mapped)
    await redis.set(key, cache, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return mapped


@router.get("/search", response_model=list[Film])
async def search_films(
    response: Response,
    query: str = Query(min_length=3, description="Search query string"),
    page_number: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(10, description="Page size", ge=1, le=100),
    film_service: FilmService = Depends(get_film_service),
    redis: Redis = Depends(get_redis),
) -> list[Film]:
    key = f"films:{query}:{page_number}:{page_size}"
    adapter = TypeAdapter(list[Film])
    if cache := await redis.get(key):
        return adapter.validate_json(cache)

    films = await film_service.search_films(query, page_number, page_size)
    mapped = [Film.model_validate(film) for film in films]
    cache = adapter.dump_json(mapped)
    await redis.set(key, cache, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return mapped


# Внедряем FilmService с помощью Depends(get_film_service)
@router.get("/{film_id}", response_model=Film, summary="Полная информация по фильму")
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> Film:
    if film := await film_service.get_by_id(film_id):
        return Film.model_validate(film)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
