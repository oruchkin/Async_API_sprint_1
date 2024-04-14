from uuid import UUID

import orjson
from models.uitls import orjson_dumps
from pydantic import BaseModel


class Person(BaseModel):
    id: UUID
    full_name: str
    gender: str | None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
