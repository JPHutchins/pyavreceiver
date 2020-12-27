"""Define a request/response connection to an AV Receiver."""
import logging
from abc import ABC

import aiohttp

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class HTTPConnection(ABC):
    """Define the HTTP connection interface."""

    def __init__(
        self,
        host: str,
        session=None,
    ):
        """Init the connection."""
        self.host = host
        self.port = None  # type: int
        self._session = session or aiohttp.ClientSession()
        self._device_info_url = None  # type: str
