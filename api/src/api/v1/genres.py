from http import HTTPStatus
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from models.genre import Genre as Model
from pydantic import BaseModel
from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


def _from_model(model: Model) -> Genre:
    return Genre(id=model.id, name=model.name, description=model.description)


@router.get("/", response_model=list[Genre], summary="Список жанров")
async def list_genres(genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:
    entities = await genre_service.get_all()
    return [_from_model(entity) for entity in entities]


@router.get("/{genre_id}", response_model=Genre, summary="Данные по конкретному жанру")
async def film_details(genre_id: UUID, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    if entity := await genre_service.get_by_id(genre_id):
        return _from_model(entity)

    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")
