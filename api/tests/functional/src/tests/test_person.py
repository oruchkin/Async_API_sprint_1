from http import HTTPStatus
from uuid import uuid4

import pytest
from redis.asyncio import Redis

from .utils import construct_es_documents

person_id = uuid4()
persons_data = [
    {
        "id": str(person_id),
        "full_name": "John Doe",
        "gender": None
    }
]

films_data = [
    {
        "id": str(uuid4()),
        "title": "The Star",
        "description": "A film about a star.",
        "imdb_rating": 8.5,
        "directors": [{"id": str(person_id), "name": "John Doe"}],
        "actors": [],
        "writers": []
    },
    {
        "id": str(uuid4()),
        "title": "The Moon",
        "description": "A film about the moon.",
        "imdb_rating": 7.0,
        "directors": [],
        "actors": [{"id": str(person_id), "name": "John Doe"}],
        "writers": []
    },
    {
        "id": str(uuid4()),
        "title": "Another Movie Without Description",
        "description": None,
        "imdb_rating": 0.0,
        "directors": [],
        "actors": [],
        "writers": [{"id": str(person_id), "name": "John Doe"}]
    }
]


@pytest.mark.asyncio
async def test_get_person(make_get_request, es_write_data):
    es_persons = construct_es_documents("persons", persons_data)
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_persons, "persons")
    await es_write_data(es_films, "movies")

    (status, body) = await make_get_request(f"/api/v1/persons/{person_id}")

    assert status == HTTPStatus.OK
    assert body["id"] == str(person_id)
    assert body["full_name"] == "John Doe"
    assert "gender" not in body or body["gender"] is None


@pytest.mark.asyncio
async def test_get_person_not_found(make_get_request, es_write_data):
    es_persons = construct_es_documents("persons", persons_data)
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_persons, "persons")
    await es_write_data(es_films, "movies")
    non_existent_id = uuid4()
    (status, _) = await make_get_request(f"/api/v1/persons/{non_existent_id}")

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("query_data, expected_status", [
    ({"query": "Jo", "page_size": 20}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({"query": "John", "page_size": 101}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({"query": "John", "page_size": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ({"query": "John", "page_size": 20, "page_number": -5}, HTTPStatus.UNPROCESSABLE_ENTITY),
])
@pytest.mark.asyncio
async def test_search_persons_validation(make_get_request, query_data, expected_status, es_write_data):
    es_persons = construct_es_documents("persons", persons_data)
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_persons, "persons")
    await es_write_data(es_films, "movies")
    (status, _) = await make_get_request("/api/v1/persons/search", query_data)
    assert status == expected_status


@pytest.mark.asyncio
async def test_search_person(make_get_request, es_write_data):
    es_persons = construct_es_documents("persons", persons_data)
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_persons, "persons")
    await es_write_data(es_films, "movies")

    query_data = {"query": "John Doe", "page_size": 10}
    (status, body) = await make_get_request("/api/v1/persons/search", query_data)

    assert status == HTTPStatus.OK
    assert len(body) == 1
    assert body[0]["full_name"] == "John Doe"


@pytest.mark.asyncio
async def test_list_all_persons(make_get_request, es_write_data):
    es_persons = construct_es_documents("persons", persons_data)
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_persons, "persons")
    await es_write_data(es_films, "movies")

    query_data = {"query": "John Doe", "page_size": 50}
    (status, body) = await make_get_request("/api/v1/persons/search", query_data)

    assert status == HTTPStatus.OK
    assert len(body) == 1
    assert body[0]["full_name"] == "John Doe"


@pytest.mark.asyncio
async def test_person_search_cache(make_get_request, es_write_data, redis_client: Redis):
    es_persons = construct_es_documents("persons", persons_data)
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_persons, "persons")
    await es_write_data(es_films, "movies")

    query_data = {"query": "John Doe", "page_size": 50}

    await make_get_request("/api/v1/persons/search", query_data)
    keys_before = await redis_client.keys()

    await make_get_request("/api/v1/persons/search", query_data)
    keys_after = await redis_client.keys()

    assert len(keys_after) == len(keys_before)


@pytest.mark.asyncio
async def test_list_person_films(make_get_request, es_write_data):
    es_persons = construct_es_documents("persons", persons_data)
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_persons, "persons")
    await es_write_data(es_films, "movies")

    (status, body) = await make_get_request(f"/api/v1/persons/{person_id}/films")

    assert status == HTTPStatus.OK
    assert len(body) == 3
    assert any(film["title"] == "The Star" for film in body)
    assert any(film["title"] == "The Moon" for film in body)
    assert any(film["title"] != "Inception" for film in body)
