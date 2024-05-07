import logging

import backoff
from redis import Redis

from ..settings import RedisSettings

logging.basicConfig()
logging.root.setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

logger = logging.getLogger("wait_for_redis")
logger.setLevel(logging.INFO)


@backoff.on_exception(backoff.expo, Exception, max_time=300)
def connect(client: Redis) -> None:
    client.ping()
    logger.info("Redis connected")


if __name__ == "__main__":
    r_settings = RedisSettings()
    redis = Redis(host=r_settings.host, port=r_settings.port, decode_responses=True)
    connect(redis)
