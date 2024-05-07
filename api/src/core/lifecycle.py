import logging.config
from contextlib import asynccontextmanager

from core.settings import ElasticsearchSettings, RedisSettings
from db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def check_elasticsearch_connection(elastic_client) -> None:
    try:
        if await elastic_client.ping():
            logger.warning("Успешное подключение к Elasticsearch.")
    except Exception as e:
        logger.error(f"Ошибка подключения к Elasticsearch: {e}")


async def check_redis_connection(redis_client) -> None:
    try:
        if await redis_client.ping():
            logger.warning("Успешное подключение к Redis.")
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для установления соединения с базами данных.
    Запускается при старте и закрывает соединения при завершении работы приложения.
    """
    elastic_settings = ElasticsearchSettings()
    elastic.es = AsyncElasticsearch(hosts=[elastic_settings.url])
    redis_settings = RedisSettings()
    redis.redis = Redis(host=redis_settings.host, port=redis_settings.port, decode_responses=True)

    await check_elasticsearch_connection(elastic.es)
    await check_redis_connection(redis.redis)

    yield

    logger.info("Закрываем соеденения.")
    await redis.redis.close()
    await elastic.es.close()
