import urllib.parse

import aiohttp
import pytest_asyncio

from ..settings import FastAPISettings


@pytest_asyncio.fixture(scope="function")
async def http_client():
    # timout is required as if something goes wrong script will just hang
    session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=5, sock_read=5)
    session = aiohttp.ClientSession(timeout=session_timeout)
    yield session
    await session.close()


def encode_url(url: str, path: str, query: dict | None = None) -> str:
    if query is None:
        return url + path

    params = urllib.parse.urlencode(query, quote_via=urllib.parse.quote)
    return url + path + f"?{params}"


@pytest_asyncio.fixture()
def make_get_request(http_client: aiohttp.ClientSession):
    api_settings = FastAPISettings()

    async def inner(path: str, query_data: dict | None = None):
        # aiohttp.get encodes query parameters in really silly way
        # thinking that it's form data (application/x-www-form-urlencoded).
        # Specifically it encodes whitespace as + instead of %20.
        # So we have to do it manually
        url = encode_url(api_settings.url, path, query_data)
        async with http_client.get(url) as response:
            body = await response.json()
            if response.status >= 500:
                raise ValueError(body)

            return response.status, body

    return inner
