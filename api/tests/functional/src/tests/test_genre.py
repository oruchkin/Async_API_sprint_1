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


@pytest.mark.asyncio
async def test_get_genre(make_get_request, es_write_data):
    es_genres = construct_es_documents("genres", genres_data)
    await es_write_data(es_genres, "genres")

    genre_id = genres_data[0]["id"]
    (status, body) = await make_get_request(f"/api/v1/genres/{genre_id}/")

    assert status == HTTPStatus.OK
    assert body["id"] == genre_id
    assert body["name"] == genres_data[0]["name"]
    assert body["description"] == genres_data[0]["description"]


@pytest.mark.asyncio
async def test_get_genre_not_found(make_get_request, es_write_data):
    es_genres = construct_es_documents("genres", genres_data)
    await es_write_data(es_genres, "genres")

    non_existent_id = uuid.uuid4()
    (status, _) = await make_get_request(f"/api/v1/genres/{non_existent_id}/")

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_genre_invalid_uuid(make_get_request):
    invalid_uuid = "invalid-uuid"
    (status, _) = await make_get_request(f"/api/v1/genres/{invalid_uuid}/")
    assert status == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_all_genres(make_get_request, es_write_data):
    es_genres = construct_es_documents("genres", genres_data)
    await es_write_data(es_genres, "genres")

    (status, body) = await make_get_request("/api/v1/genres/")

    assert status == HTTPStatus.OK
    assert len(body) == len(genres_data)
    for genre in genres_data:
        assert any(item["id"] == genre["id"] for item in body)


@pytest.mark.asyncio
async def test_genre_search_cache(make_get_request, es_write_data, redis_client: Redis):
    es_genres = construct_es_documents("genres", genres_data)
    await es_write_data(es_genres, "genres")

    await make_get_request("/api/v1/genres/")
    keys_before = await redis_client.keys()

    await make_get_request("/api/v1/genres/")
    keys_after = await redis_client.keys()

    assert len(keys_after) == len(keys_before)
