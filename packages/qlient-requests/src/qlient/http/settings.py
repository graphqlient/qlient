"""This file contains the settings that can be overwritten in the qlient Client."""

import json
from typing import Any
from collections.abc import Callable

from qlient.core import Settings


class HTTPSettings(Settings):
    """Class that represents the settings that can be adjusted to your liking."""

    def __init__(
        self, json_loads: Callable[[str], Any] = json.loads, json_dumps: Callable[..., str] = json.dumps, **kwargs
    ):
        super().__init__(**kwargs)
        self.json_loads: Callable[[str], Any] = json_loads
        self.json_dumps: Callable[..., str] = json_dumps
