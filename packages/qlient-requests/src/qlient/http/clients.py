"""This file contains the graphql http client."""

import logging

from qlient.core import Client, Backend
from qlient.http.backends import HTTPBackend
from qlient.http.settings import HTTPSettings

logger = logging.getLogger("qlient")


class HTTPClient(Client):
    """This class represents the http client.

    Examples:
        Basic example
        >>> client = HTTPClient("https://...")
        >>> response = client.query.get_books(...)

        With a custom authenticated session
        >>> import requests
        >>> session = requests.Session()
        >>> session.headers["Authorization"] = ...
        >>> client = HTTPClient(HTTPBackend("https://...", session=session))
        >>> response = client.query.get_books(...)
    """

    def __init__(self, backend: str | Backend, settings: HTTPSettings = None, **kwargs):
        if settings is None:
            settings = HTTPSettings()

        if isinstance(backend, str):
            backend = HTTPBackend(backend)

        super().__init__(backend, settings=settings, **kwargs)
