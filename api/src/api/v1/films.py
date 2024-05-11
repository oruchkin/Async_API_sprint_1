from http import HTTPStatus
from typing import Literal
from uuid import UUID

from api.v1.schemas.film import Film
from api.v1.schemas.pagination import PaginatedParams
from db.redis import get_cache
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import TypeAdapter
from services.cache.storage import ICache
from services.film import FilmService, get_film_service

router = APIRouter()


SORT_OPTION = Literal["imdb_rating", "-imdb_rating"]


@router.get("/", response_model=list[Film],
            summary="Список всех фильмов",
            description="Возвращает полный список фильмов")
async def list_films(
    response: Response,
    pagination: PaginatedParams = Depends(),
    sort: SORT_OPTION = Query("imdb_rating", description="Sorting options"),
    genre: UUID | None = Query(None, description="Films by genre"),
    film_service: FilmService = Depends(get_film_service),
    cache: ICache = Depends(get_cache),
) -> list[Film]:
    key = f"films:{pagination.page_number}:{pagination.page_size}:{genre}:{sort}"
    adapter = TypeAdapter(list[Film])
    if cached := await cache.get(key):
        return adapter.validate_json(cached)

    sort_object: dict[str, int] | None = None
    if sort:
        sort_object = {}
        # Maybe sort will be an array in future
        for item in [sort]:
            if item[0] == "-":
                sort_object[item[1:]] = -1
            else:
                sort_object[item] = 1
    films = await film_service.get_all_films(pagination.page_number, pagination.page_size, genre, sort_object)
    mapped = [Film.model_validate(film) for film in films]
    cached = adapter.dump_json(mapped)
    await cache.set(key, cached, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return mapped


@router.get("/search",
            response_model=list[Film],
            summary="Поиск по фильмам",
            description="Возвращает список фильмов по поисковому запросу")
async def search_films(
    response: Response,
    query: str = Query(min_length=3, description="Search query string"),
    pagination: PaginatedParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
    cache: ICache = Depends(get_cache),
) -> list[Film]:
    key = f"films:{query}:{pagination.page_number}:{pagination.page_size}"
    adapter = TypeAdapter(list[Film])
    if cached := await cache.get(key):
        return adapter.validate_json(cached)

    films = await film_service.search_films(query, pagination.page_number, pagination.page_size)
    mapped = [Film.model_validate(film) for film in films]
    cached = adapter.dump_json(mapped)
    await cache.set(key, cached, 60 * 5)
    response.headers["Cache-Control"] = f"max-age={60 * 5}"
    return mapped


@router.get("/{film_id}",
            response_model=Film,
            summary="Данные по конкретному фильму",
            description="Возвращает подробную информацию о фильме.")
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> Film:
    if film := await film_service.get_by_id(film_id):
        return Film.model_validate(film)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
