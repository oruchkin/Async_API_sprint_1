import logging
import logging.config
from contextlib import asynccontextmanager

import uvicorn
from api.v1 import films, genres, persons
from core.logger import LOGGING
from db import elastic, redis
from dotenv import load_dotenv
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    elasticSettings = elastic.ElasticsearchSettings()
    elastic.es = AsyncElasticsearch(hosts=[elasticSettings.url])
    redisSettings = redis.RedisSettings()
    redis.redis = Redis(host=redisSettings.host, port=redisSettings.port, decode_responses=True)
    yield
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
