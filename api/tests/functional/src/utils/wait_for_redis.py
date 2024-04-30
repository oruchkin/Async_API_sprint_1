import logging
import time

from redis import Redis

from ..settings import RedisSettings

logging.basicConfig()
logging.root.setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

logger = logging.getLogger("wait_for_redis")
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    r_settings = RedisSettings()
    client = redis = Redis(host=r_settings.host, port=r_settings.port, decode_responses=True)
    while True:
        try:
            resp = client.ping()
            logger.info("Redis connected")
            break
        except Exception as ex:
            logger.info("Failed to connect to redis, retrying... %s" % ex)
            time.sleep(1)
