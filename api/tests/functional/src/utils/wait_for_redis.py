import logging
import time

from redis import Redis

from ..settings import RedisSettings

logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)

logger = logging.getLogger(__name__)

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
