from typing import Optional

import orjson
from models.uitls import orjson_dumps
from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        json_loads = orjson.loads
        model_validate_json = orjson.loads
        json_dumps = orjson_dumps
        model_dump_json = orjson_dumps
