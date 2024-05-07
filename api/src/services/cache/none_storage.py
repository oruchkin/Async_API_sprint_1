import logging.config
from typing import Any

from .storage import ICache


class NoneCache(ICache):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    async def set(self, key: str, value: Any, timeout_sec: int) -> None:
        self._logger.info(f"Ignore save {key}")

    async def get(self, key: str) -> Any:
        self._logger.info(f"Ignore load {key}")
