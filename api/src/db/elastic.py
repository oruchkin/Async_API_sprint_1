from typing import Optional

from elasticsearch import AsyncElasticsearch
from pydantic_settings import BaseSettings, SettingsConfigDict


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ES_")
    url: str = ""


es: Optional[AsyncElasticsearch] = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    global es
    if es is None:
        settings = ElasticsearchSettings()
        es = AsyncElasticsearch(settings.url)

    return es
