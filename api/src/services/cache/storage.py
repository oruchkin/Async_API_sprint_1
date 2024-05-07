import abc
from typing import Any


class ICache(abc.ABC):
    @abc.abstractmethod
    async def set(self, key: str, value: Any, timeout_sec: int) -> None: ...

    @abc.abstractmethod
    async def get(self, key: str) -> Any: ...
