import orjson
from models.uitls import orjson_dumps
from pydantic import BaseModel


class Film(BaseModel):
    id: str
    title: str
    description: str
    imdb_rating: float

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
