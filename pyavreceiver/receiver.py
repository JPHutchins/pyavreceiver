"""Define an audio/video receiver."""
from collections import defaultdict
from typing import Dict, Optional

from pyavreceiver import const
from pyavreceiver.command import Command, CommandValues
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
        http_api=None,
        upnp: bool = True,
        timeout: float = const.DEFAULT_TIMEOUT,
        heart_beat: Optional[float] = const.DEFAULT_HEART_BEAT,
        dispatcher: Dispatcher = Dispatcher(),
        main_zone: Zone = None,
        aux_zone: Zone = None,
    ):
        """Init the device."""
        self._host = host
        self._connection = None  # type: TelnetConnection
        self._device_info = {}
        self._dispatcher = dispatcher
        self._telnet = telnet
        self._http = http
        self._http_connection = http_api
        self._upnp = upnp
        self._connections = []
        self._state = defaultdict()
        self._sources = None  # type: dict
        self._main_zone = None  # type: Zone
        self._zone2, self._zone3, self._zone4 = None, None, None
        self._main_zone_class = main_zone
        self._aux_zone_class = aux_zone

    async def init(
        self,
        *,
        auto_reconnect=False,
        reconnect_delay: float = const.DEFAULT_RECONNECT_DELAY,
    ):
        """Await the initialization of the device."""
        disconnect = await self._connection.init(
            auto_reconnect=auto_reconnect, reconnect_delay=reconnect_delay
        )
        self._connections.append(disconnect)
        if self._sources:
            self.commands[const.ATTR_SOURCE].init_values(CommandValues(self._sources))
        if self._http and self._http_connection:
            await self.update_device_info()
        if self.zones >= 1:
            self._main_zone = self._main_zone_class(self)
        if self.zones >= 2:
            self._zone2 = self._aux_zone_class(self, zone="zone2")
        if self.zones >= 3:
            self._zone3 = self._aux_zone_class(self, zone="zone3")
        if self.zones >= 4:
            self._zone4 = self._aux_zone_class(self, zone="zone4")

    async def connect(
        self,
        *,
        auto_reconnect=False,
        reconnect_delay: float = const.DEFAULT_RECONNECT_DELAY,
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

    async def update_device_info(self):
        """Update information about the A/V Receiver."""
        self._device_info = await self._http_connection.get_device_info()
        self._sources = await self._http_connection.get_source_names()

    @property
    def dispatcher(self) -> Dispatcher:
        """Get the dispatcher instance."""
        return self._dispatcher

    @property
    def commands(self) -> Dict[str, Command]:
        """Get the dict of commands."""
        return self._connection.commands

    @property
    def connection_state(self) -> str:
        """Get the state of the connection."""
        return self._connection.state

    @property
    def host(self) -> str:
        """Get the host."""
        return self._host

    @property
    def friendly_name(self) -> str:
        """Get the friendly name."""
        return self._device_info.get(const.INFO_FRIENDLY_NAME)

    @property
    def mac(self) -> str:
        """Get the MAC address."""
        return self._device_info.get(const.INFO_MAC)

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return self._device_info.get(const.INFO_MANUFACTURER)

    @property
    def model(self) -> str:
        """Get the model."""
        return self._device_info.get(const.INFO_MODEL)

    @property
    def main(self) -> Zone:
        """Get the main zone object."""
        return self._main_zone

    @property
    def serial_number(self) -> str:
        """Get the serial number."""
        return self._device_info.get(const.INFO_SERIAL)

    @property
    def sources(self) -> dict:
        """Get the input sources map."""
        return self._sources if self._sources else {}

    @property
    def state(self) -> defaultdict:
        """Get the current state."""
        return self._state

    @property
    def telnet_connection(self) -> TelnetConnection:
        """Get the telnet connection."""
        return self._connection

    @property
    def power(self) -> str:
        """The state of power."""
        return self.state.get(const.ATTR_POWER)

    @property
    def zone2(self) -> Zone:
        """Get the Zone 2 object."""
        return self._zone2

    @property
    def zone3(self) -> Zone:
        """Get the Zone 3 object."""
        return self._zone3

    @property
    def zone4(self) -> Zone:
        """Get the Zone 4 object."""
        return self._zone4

    @property
    def zones(self) -> int:
        """Get the number of zones."""
        return self._device_info.get(const.INFO_ZONES)

    def set_power(self, val: bool) -> bool:
        """Request the receiver set power to val."""
        # pylint: disable=protected-access
        command = self._connection._command_lookup[const.ATTR_POWER].set_val(val)
        self._connection.send_command(command)
        return True
