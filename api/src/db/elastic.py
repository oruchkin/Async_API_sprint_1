from elasticsearch import AsyncElasticsearch
from core.settings import ElasticsearchSettings



es: AsyncElasticsearch | None = None


def get_elastic() -> AsyncElasticsearch:
    global es
    if es is None:
        settings = ElasticsearchSettings()
        es = AsyncElasticsearch(settings.url)

    return es
