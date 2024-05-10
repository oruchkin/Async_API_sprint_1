from uuid import UUID

from models.uitls import BaseOrjsonModel


class Person(BaseOrjsonModel):
    id: UUID
    full_name: str
    gender: str | None = None
