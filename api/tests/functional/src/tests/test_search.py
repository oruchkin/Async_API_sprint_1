import uuid

import pytest
from redis.asyncio import Redis


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        ({"query": "The Star", "page_size": 60}, {"status": 200, "length": 60}),
        ({"query": "Mashed potato", "page_size": 60}, {"status": 200, "length": 0}),
    ],
)
@pytest.mark.asyncio(scope="function")
async def test_search(make_get_request, es_write_data, redis_client: Redis, query_data: dict, expected_answer: dict):

    # arrange
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "imdb_rating": 8.5,
            "genres": ["Action", "Sci-Fi"],
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
        for _ in range(60)
    ]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {"_index": "movies", "_id": row["id"]}
        data.update({"_source": row})
        bulk_query.append(data)

    try:
        await es_write_data(bulk_query)

        # act
        keys_before = await redis_client.keys()
        (status, body) = await make_get_request("/api/v1/films/search", query_data)
        keys_after = await redis_client.keys()

        # assert
        assert len(keys_after) > len(keys_before), "Cache key must be set"
        assert status == expected_answer["status"]
        assert len(body) == expected_answer["length"]

    except AssertionError as err:
        # do not catch AssertionErrors
        raise err
    except Exception as err:
        assert False, err
