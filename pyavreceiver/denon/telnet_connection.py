"""Define the Denon/Marantz telnet connection."""
import logging
from datetime import datetime
from importlib import resources
from typing import Optional

import yaml

from pyavreceiver.denon import const as denon_const
from pyavreceiver.denon.commands import get_command_lookup
from pyavreceiver.denon.response import DenonMessage
from pyavreceiver.telnet_connection import TelnetConnection

_LOGGER = logging.getLogger(__name__)


class DenonTelnetConnection(TelnetConnection):
    """Define the simplest Denon telnet connection."""

    def __init__(
        self,
        avr,
        host,
        *,
        port: int = denon_const.CLI_PORT,
        timeout: float = denon_const.DEFAULT_TIMEOUT,
        heart_beat: Optional[float] = denon_const.DEFAULT_HEART_BEAT,
    ):
        """Init the connection."""
        super().__init__(avr, host, port=port, timeout=timeout, heart_beat=heart_beat)
        self._message_interval_limit = denon_const.MESSAGE_INTERVAL_LIMIT

    def _load_command_dict(self, path=None):
        with resources.open_text("pyavreceiver.denon", "commands.yaml") as file:
            self._command_dict = yaml.safe_load(file.read())

    def _get_command_lookup(self, command_dict):
        return get_command_lookup(command_dict)

    async def _response_handler(self):
        while True:
            msg = None  # temporary for error detection
            try:
                msg = await self._reader.readuntil(
                    separator=denon_const.TELNET_SEPARATOR.encode()
                )
                message = msg.decode()[:-1]
                self._last_activity = datetime.utcnow()
                resp = DenonMessage(message, command_dict=self._command_dict)
                self._handle_event(resp)

                # Check if this is a response to a previous command
                if exp_response_item := self._expected_responses.popmatch(resp.command):
                    _, expected_response = exp_response_item
                    expected_response.set(resp.message)
            # pylint: disable=broad-except, fixme
            except Exception as err:
                # TODO: error handling
                _LOGGER.critical(err)
                _LOGGER.critical(msg)
                raise err
