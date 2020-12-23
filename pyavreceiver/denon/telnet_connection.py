"""Define the Denon/Marantz telnet connection."""
import logging
from typing import Optional
from datetime import datetime
import aiofiles
import yaml


from pyavreceiver.denon import const as denon_const
from pyavreceiver.denon.commands import get_command_lookup
from pyavreceiver.denon.response import DenonMessage
from pyavreceiver.telnet_connection import TelnetConnection

_LOGGER = logging.getLogger("denon_telnet_cconnection")


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

    async def _load_command_dict(self, path=None):
        async with aiofiles.open("pyavreceiver/denon/commands.yaml") as file:
            self._command_dict = yaml.safe_load(await file.read())

    def _get_command_lookup(self, command_dict):
        return get_command_lookup(command_dict)

    async def _response_handler(self):
        while True:
            msg = await self._reader.readuntil(
                separator=denon_const.TELNET_SEPARATOR.encode()
            )
            message = msg.decode()[:-1]
            self._last_activity = datetime.utcnow()
            resp = DenonMessage(message, command_dict=self._command_dict)
            self._handle_event(resp)

            # Check if this is a response to a previous command
            if commands := self._expected_responses.get(resp.command):
                commands.popleft()
                if not commands:
                    del commands
