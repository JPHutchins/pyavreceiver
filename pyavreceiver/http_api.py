"""Define a request/response connection to an AV Receiver."""
from abc import ABC
from collections import defaultdict


class HTTPApi(ABC):
    """Define the HTTP connection interface."""

    def __init__(self, host: str, upnp_data=None):
        """Init the connection."""
        self.host = host
        self._upnp_data = upnp_data
        self.port = None  # type: int
        self._device_info_url = None  # type: str
        self._device_info = defaultdict(None)

    @property
    def device_info(self):
        """Return the device info dict."""
        return self._device_info
