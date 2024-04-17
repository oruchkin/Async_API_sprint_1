from uuid import UUID

import orjson
from models.uitls import orjson_dumps
from pydantic import BaseModel


class PersonId(BaseModel):
    id: UUID
    name: str


class Film(BaseModel):
    id: UUID
    title: str
    description: str | None
    imdb_rating: float | None
    directors: list[PersonId]
    actors: list[PersonId]
    writers: list[PersonId]

    class Config:
        json_loads = orjson.loads
        model_validate_json = orjson.loads
        json_dumps = orjson_dumps
        model_dump_json = orjson_dumps
