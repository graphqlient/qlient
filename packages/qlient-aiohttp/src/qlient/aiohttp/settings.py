"""This module contains the aio http settings."""

import json
from collections.abc import Callable
from typing import Any

from qlient.core.settings import Settings


class AIOHTTPSettings(Settings):
    """The AIO http settings."""

    def __init__(
        self, json_loads: Callable[[str], Any] = json.loads, json_dumps: Callable[..., str] = json.dumps, **kwargs
    ):
        super().__init__(**kwargs)
        self.json_loads: Callable[[str], Any] = json_loads
        self.json_dumps: Callable[..., str] = json_dumps
