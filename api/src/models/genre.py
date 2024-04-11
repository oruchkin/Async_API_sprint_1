import orjson
from models.uitls import orjson_dumps
from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str
    description: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
