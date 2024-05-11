import uuid
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from .utils import construct_es_documents

genres_data = [
    {
        "id": str(uuid.uuid4()),
        "name": f"genre-{ix}",
        "description": f"Description for genre-{ix}"
    }
    for ix in range(5)
]

films_data = [
    {
        "id": str(uuid.uuid4()),
        "imdb_rating": ix / 10,
        "genres": [genres_data[ix % len(genres_data)]["name"]],
        "title": "The Star",
        "description": "New World",
        "directors_names": ["Stan"],
        "actors_names": ["Ann", "Bob"],
        "writers_names": ["Ben", "Howard"],
        "actors": [
            {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
            {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
        ],
        "writers": [
            {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
            {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "Howard"},
        ],
        "directors": [{"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Stan"}],
    }
    for ix in range(20)
]


@pytest.mark.asyncio(scope="function")
async def test_list_films_by_genre(make_get_request, es_write_data, redis_client: Redis):
    # arrange
    es_films = construct_es_documents("movies", films_data)
    es_genres = construct_es_documents("genres", genres_data)
    await es_write_data(es_films, "movies")
    await es_write_data(es_genres, "genres")

    target_genre = genres_data[0]

    # act
    keys_before = await redis_client.keys()
    query_data = {"page_size": 3, "genre": target_genre["id"], "sort": "-imdb_rating"}
    (status, body) = await make_get_request("/api/v1/films", query_data)
    keys_after = await redis_client.keys()

    # assert
    assert len(keys_after) > len(keys_before), "Cache key must be set"
    assert status == HTTPStatus.OK
    assert len(body) == 3
    assert body[0]["imdb_rating"] > body[-1]["imdb_rating"]


@pytest.mark.asyncio(scope="function")
async def test_list_films_fail_on_wrong_page_size(make_get_request, es_write_data):
    # arrange
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_films, "movies")

    # act
    query_data = {"page_size": 0}
    (status, body) = await make_get_request("/api/v1/films", query_data)

    # assert
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "page_size" in body["detail"][0]["loc"]


@pytest.mark.asyncio(scope="function")
async def test_list_films_fail_on_wrong_page(make_get_request, es_write_data):
    # arrange
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_films, "movies")

    # act
    query_data = {"page_number": 0}
    (status, body) = await make_get_request("/api/v1/films", query_data)

    # assert
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "page_number" in body["detail"][0]["loc"]


@pytest.mark.asyncio(scope="function")
async def test_list_films_page_number(make_get_request, es_write_data):
    # arrange
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_films, "movies")

    # act
    query_data = {"page_number": 100}
    (status, body) = await make_get_request("/api/v1/films", query_data)

    # assert
    assert status == HTTPStatus.OK
    assert len(body) == 0


@pytest.mark.asyncio(scope="function")
async def test_list_films(make_get_request, es_write_data, redis_client: Redis):
    # arrange
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_films, "movies")

    # act
    keys_before = await redis_client.keys()
    query_data = {
        "page_number": 2,
        "page_size": 5,
        "sort": "imdb_rating",
    }
    (status, body) = await make_get_request("/api/v1/films", query_data)
    keys_after = await redis_client.keys()

    # assert
    assert len(keys_after) > len(keys_before), "Cache key must be set"
    assert status == HTTPStatus.OK
    assert len(body) == 5
    assert body[0]["imdb_rating"] > 0, "For the second page imdb_rating must be > 0"
    assert body[0]["imdb_rating"] < body[-1]["imdb_rating"]


@pytest.mark.asyncio(scope="function")
async def test_get_film(make_get_request, es_write_data, redis_client: Redis):
    # arrange
    es_films = construct_es_documents("movies", films_data)
    await es_write_data(es_films, "movies")

    target_film = films_data[3]

    # act
    keys_before = await redis_client.keys()
    (status, body) = await make_get_request(f"/api/v1/films/{target_film['id']}")
    keys_after = await redis_client.keys()

    # assert
    assert len(keys_after) == len(keys_before), "Cache should not be set"
    assert status == HTTPStatus.OK
    assert body["id"] == target_film["id"]


@pytest.mark.asyncio(scope="function")
async def test_get_film_not_found(make_get_request):
    # arrange
    target_film = films_data[0]

    # act
    (status, _) = await make_get_request(f"/api/v1/films/{target_film['id']}")

    # assert
    # TODO (agrebennikov): it should not return 404!
    assert status == HTTPStatus.NOT_FOUND
