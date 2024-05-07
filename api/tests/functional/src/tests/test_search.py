import random
import uuid

import pytest
from redis.asyncio import Redis


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "The Star", "page_size": 20}, {"status": 200, "length": 15}),
        ({"query": "The Star", "page_size": 20, "page_number": 2}, {"status": 200, "length": 0}),
        ({"query": "The Star", "page_size": 20, "page_number": 0}, {"status": 422}),
        ({"query": "The Star", "page_size": 0}, {"status": 422}),
        ({"query": "Mashed potato", "page_size": 20}, {"status": 200, "length": 5}),
        ({"query": "Th"}, {"status": 422}),
    ],
)
@pytest.mark.asyncio(scope="function")
async def test_search(make_get_request, es_write_data, redis_client: Redis, query_data: dict, expected_answer: dict):

    # arrange
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": random.randint(0, 10),
            "genres": ["Action", "Sci-Fi"],
            "title": "The Star" if ix < 15 else "Mashed potato",
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

    bulk_query = [{"_index": "movies", "_id": row["id"], "_source": row} for row in es_data]
    await es_write_data(bulk_query)

    # act
    keys_before = await redis_client.keys()
    (status, body) = await make_get_request("/api/v1/films/search", query_data)
    keys_after = await redis_client.keys()

    # assert
    assert status == expected_answer["status"]
    if status < 400:
        assert len(keys_after) > len(keys_before), "Cache key must be set"
        assert len(body) == expected_answer["length"]
