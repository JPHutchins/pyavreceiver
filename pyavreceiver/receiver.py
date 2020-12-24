"""Define an audio/video receiver."""
from collections import defaultdict
from typing import Optional

from pyavreceiver import const
from pyavreceiver.dispatch import Dispatcher
from pyavreceiver.telnet_connection import TelnetConnection
from pyavreceiver.zone import Zone


class AVReceiver:
    """Representation of an audio/video receiver."""

    def __init__(
        self,
        host: str,
        *,
        telnet: bool = True,
        http: bool = True,
        upnp: bool = True,
        timeout: float = const.DEFAULT_TIMEOUT,
        heart_beat: Optional[float] = const.DEFAULT_HEART_BEAT,
        dispatcher: Dispatcher = Dispatcher(),
        zone: Zone = Zone
    ):
        """Init the device."""
        self._host = host
        self._connection = None  # type: TelnetConnection
        self._dispatcher = dispatcher
        self._telnet = telnet
        self._http = http
        self._upnp = upnp
        self._connections = []
        self._state = defaultdict()
        self._main_zone = None  # type: Zone
        self._zone = zone

    async def init(
        self,
        *,
        auto_reconnect=False,
        reconnect_delay: float = const.DEFAULT_RECONNECT_DELAY
    ):
        """Await the initialization of the device."""
        await self._connection.init(
            auto_reconnect=auto_reconnect, reconnect_delay=reconnect_delay
        )
        self._main_zone = self._zone(self)

    async def connect(
        self,
        *,
        auto_reconnect=False,
        reconnect_delay: float = const.DEFAULT_RECONNECT_DELAY
    ):
        """Connect to the audio/video receiver."""
        if self._telnet:
            await self._connection.connect_telnet(
                auto_reconnect=auto_reconnect, reconnect_delay=reconnect_delay
            )
            self._connections.append(self._connection.disconnect_telnet)

    async def disconnect(self):
        """Disconnect from the audio/video receiver."""
        while self._connections:
            disconnect = self._connections.pop()
            await disconnect()

    def update_state(self, state_update: dict) -> bool:
        """Handle a state update."""
        update = False
        for attr, val in state_update.items():
            if attr not in self._state or self._state[attr] != val:
                self._state[attr] = val
                update = True
        return update

    @property
    def dispatcher(self) -> Dispatcher:
        """Get the dispatcher instance."""
        return self._dispatcher

    @property
    def connection_state(self) -> str:
        """Get the state of the connection."""
        return self._connection.state

    @property
    def host(self) -> str:
        """Get the host."""
        return self._host

    @property
    def main(self) -> Zone:
        """Get the main zone object."""
        return self._main_zone

    @property
    def state(self) -> defaultdict:
        """Get the current state."""
        return self._state

    @property
    def power(self) -> str:
        """The state of power."""
        return self.state.get(const.ATTR_POWER)

    def set_power(self, val: bool) -> bool:
        """Request the receiver set power to val."""
        # pylint: disable=protected-access
        command = self._connection._command_lookup[const.ATTR_POWER].set_val(val)
        self._connection.send_command(command)
        return True
