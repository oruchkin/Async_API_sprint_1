from uuid import UUID

from models.uitls import BaseOrjsonModel


class Genre(BaseOrjsonModel):
    id: UUID
    name: str
    description: str | None = None
