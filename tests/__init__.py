"""Tests for the pyavreceiver library."""
from datetime import datetime
from importlib import resources

import yaml

from pyavreceiver import const
from pyavreceiver.denon.commands import get_command_lookup
from pyavreceiver.telnet_connection import TelnetConnection


class GenericTelnetConnection(TelnetConnection):
    """Define the simplest Denon telnet connection."""

    def __init__(
        self,
        avr,
        host,
        *,
        port=4000,
        timeout=const.DEFAULT_TIMEOUT,
        heart_beat=const.DEFAULT_HEART_BEAT,
    ):
        """Init the connection."""
        super().__init__(avr, host, port=port, timeout=timeout, heart_beat=heart_beat)
        self._message_interval_limit = const.MESSAGE_INTERVAL_LIMIT

    def _load_command_dict(self, path=None):
        with resources.open_text("pyavreceiver.denon", "commands.yaml") as file:
            self._command_dict = yaml.safe_load(file.read())

    def _get_command_lookup(self, command_dict):
        return get_command_lookup(command_dict)

    async def _response_handler(self):
        while True:
            msg = await self._reader.readuntil(separator=b"\r")
            message = msg.decode()[:-1]
            self._last_activity = datetime.utcnow()
            resp = message
            # self._handle_event(resp)

            # Check if this is a response to a previous command
            if commands := self._expected_responses.get(resp):
                try:
                    _, response = commands.popitem(last=False)
                    response.set("OK!")
                    if not commands:
                        del commands
                # pylint: disable=broad-except
                except Exception as err:
                    print("handler exception")
                    print(err)
