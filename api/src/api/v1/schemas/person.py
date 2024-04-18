from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PersonFilm(BaseModel):
    uuid: UUID
    roles: list[str]


class Person(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    films: list[PersonFilm] | None = None
