import logging
import time

from redis import Redis

from ..settings import RedisSettings

logger = logging.Logger(__name__)

if __name__ == "__main__":
    r_settings = RedisSettings()
    client = redis = Redis(host=r_settings.host, port=r_settings.port, decode_responses=True)
    while True:
        if client.ping():
            break
        logger.info("Failed to connect to redis, retrying...")
        time.sleep(1)
