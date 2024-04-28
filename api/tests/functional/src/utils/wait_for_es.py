import logging
import time

from elasticsearch import Elasticsearch

from ..settings import ElasticsearchSettings

logging.basicConfig()
logging.root.setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

logger = logging.getLogger("wait_for_es")
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    es_settings = ElasticsearchSettings()
    es_client = Elasticsearch(hosts=es_settings.url, validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            logger.info("Elasticsearch connected")
            break
        logger.info("Failed to connect to elasticsearch, retrying...")
        time.sleep(1)
