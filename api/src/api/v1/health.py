import logging

from api.v1.schemas.health_status import HealthStatus
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

router = APIRouter()


logger = logging.getLogger(__name__)


@router.get("/", response_model=HealthStatus)
async def get_health(
    es: AsyncElasticsearch = Depends(get_elastic),
    redis: Redis = Depends(get_redis),
) -> HealthStatus:
    is_redis_up = await check_redis_connection(redis)
    is_es_up = await check_elasticsearch_connection(es)
    model = HealthStatus(redis=is_redis_up, elasticsearch=is_es_up)
    return model


async def check_elasticsearch_connection(elastic_client) -> bool:
    try:
        if await elastic_client.ping():
            logger.info("Успешное подключение к Elasticsearch.")
            return True
    except Exception as e:
        logger.error(f"Ошибка подключения к Elasticsearch: {e}")

    return False


async def check_redis_connection(redis_client) -> bool:
    try:
        if await redis_client.ping():
            logger.info("Успешное подключение к Redis.")
            return True
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")

    return False
