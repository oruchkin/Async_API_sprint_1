from core.settings import ElasticsearchSettings
from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = None


def get_elastic() -> AsyncElasticsearch:
    global es
    if es is None:
        settings = ElasticsearchSettings()
        es = AsyncElasticsearch(settings.url)

    return es
