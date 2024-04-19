import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default) -> str:
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    class Config: 
        model_validate_json = orjson.loads
        model_dump_json = orjson_dumps