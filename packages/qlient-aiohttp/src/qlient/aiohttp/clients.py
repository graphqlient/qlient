"""The client implementation for aiohttp"""

from qlient.aiohttp.backends import AIOHTTPBackend
from qlient.core import AsyncClient, Backend


class AIOHTTPClient(AsyncClient):
    """The aiohttp implementation for qlient.

    Examples:
        Basic Example
        >>> async with AIOHTTPClient("https://...") as client:
        >>>     result = await client.query.get_books(...)

        With custom client session
        >>> import aiohttp
        >>> async with aiohttp.ClientSession() as session:
        >>>     async with AIOHTTPClient(AIOHTTPBackend("https://...", session=session)) as client:
        >>>         result = await client.query.get_books(...)
    """

    def __init__(self, backend: str | Backend, **kwargs):
        if isinstance(backend, str):
            backend = AIOHTTPBackend(backend)

        super().__init__(backend, **kwargs)
