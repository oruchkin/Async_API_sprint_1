import logging

import backoff
from elasticsearch import Elasticsearch

from ..settings import ElasticsearchSettings

logging.basicConfig()
logging.root.setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)
logging.getLogger("elasticsearch").setLevel(logging.ERROR)

logger = logging.getLogger("wait_for_es")
logger.setLevel(logging.INFO)


@backoff.on_exception(backoff.expo, Exception, max_time=300)
def connect(client: Elasticsearch) -> None:
    if not client.ping():
        raise ValueError("Failed to connect")

    logger.info("Elasticsearch connected")


if __name__ == "__main__":
    es_settings = ElasticsearchSettings()
    es_client = Elasticsearch(hosts=es_settings.url, validate_cert=False, use_ssl=False)
    connect(es_client)
