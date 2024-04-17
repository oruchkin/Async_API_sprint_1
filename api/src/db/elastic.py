from typing import Optional

from elasticsearch import AsyncElasticsearch
# from pydantic_settings import BaseSettings, SettingsConfigDict
from core.settings import ElasticsearchSettings



es: Optional[AsyncElasticsearch] = None


def get_elastic() -> AsyncElasticsearch:
    global es
    if es is None:
        settings = ElasticsearchSettings()
        es = AsyncElasticsearch(settings.url)

    return es
