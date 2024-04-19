from uuid import UUID

from models.uitls import BaseOrjsonModel


class PersonId(BaseOrjsonModel):
    id: UUID
    name: str


class Film(BaseOrjsonModel):
    id: UUID
    title: str
    description: str | None
    imdb_rating: float | None
    directors: list[PersonId]
    actors: list[PersonId]
    writers: list[PersonId]
