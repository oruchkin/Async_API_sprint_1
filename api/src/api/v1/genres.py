from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str
    description: str


@router.get("/", response_model=list[Genre], summary="Список жанров")
async def list_genres(genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:
    return []


@router.get("/{genre_id}", response_model=Genre, summary="Данные по конкретному жанру")
async def film_details(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    if entity := await genre_service.get_by_id(genre_id):
        return Genre(id=entity.id, name=entity.name, description=entity.description)
    
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
