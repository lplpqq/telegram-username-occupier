from __future__ import annotations
import abc
import asyncio
from contextlib import asynccontextmanager
from types import TracebackType
from typing import AsyncIterator, Optional, Type, Any

from aiohttp import ClientSession, ClientResponse

DEFAULT_TIMEOUT = 60.0


class BaseSession(abc.ABC):
    def __init__(
        self,
        base_api_url: str,
        session: ClientSession,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._base_api_url = base_api_url
        self._session = session
        self._timeout = timeout

    async def create_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession()

        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

            # Wait 250 ms for the underlying SSL connections to close
            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    @asynccontextmanager
    async def _request(
        self, method: str, relative_endpoint: str, **kwargs
    ) -> AsyncIterator[ClientResponse]:
        full_url = self._base_api_url + relative_endpoint

        async with self._session.request(method, full_url, **kwargs) as response:
            response.raise_for_status()
            yield response

    async def _get(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> tuple[str, ClientResponse]:
        async with self._request("GET", endpoint, **kwargs) as response:
            text_response = await response.text()
            return text_response, response

    async def __aenter__(self) -> BaseSession:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()
