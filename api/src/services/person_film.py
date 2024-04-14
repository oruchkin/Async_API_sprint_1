import asyncio
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from models.film import Film
from models.person import Person
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service


class PersonFilmService:
    def __init__(
        self,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service),
    ):
        self._film_service = film_service
        self._person_service = person_service

    async def search(self, query: str, page_number: int = 1, page_size: int = 50) -> list[tuple[Person, list[Film]]]:
        persons = await self._person_service.search(query, page_number, page_size)
        person_films = await self._film_service.find_by_all_persons([p.id for p in persons])
        return [(person, person_films.get(person.id, [])) for person in persons]

    async def get_person_with_films(self, person_id: UUID) -> tuple[Person | None, list[Film]]:
        filmsTask = self._film_service.find_by_person(person_id)
        personTask = self._person_service.get_by_id(person_id)
        return await asyncio.gather(personTask, filmsTask)


@lru_cache()
def get_person_film_service(
    person: PersonService = Depends(get_person_service),
    film: FilmService = Depends(get_film_service),
) -> PersonFilmService:
    return PersonFilmService(person, film)
