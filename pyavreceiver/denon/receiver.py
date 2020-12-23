"""Define a Denon/Marantz Audio Video Receiver."""
from typing import Optional

from pyavreceiver.receiver import AVReceiver
from pyavreceiver.dispatch import Dispatcher
from pyavreceiver.denon.telnet_connection import DenonTelnetConnection
from pyavreceiver.denon.zone import DenonZone
from pyavreceiver.denon import const as denon_const


class DenonReceiver(AVReceiver):
    """Representation of a Denon or Marantz A/V Receiver."""

    def __init__(
        self,
        host,
        *,
        telnet: bool = True,
        http: bool = True,
        upnp: bool = True,
        timeout: float = denon_const.DEFAULT_TIMEOUT,
        heart_beat: Optional[float] = denon_const.DEFAULT_HEART_BEAT,
        dispatcher: Dispatcher = Dispatcher(),
        zone: DenonZone = DenonZone
    ):
        super().__init__(
            host,
            telnet=telnet,
            http=http,
            upnp=upnp,
            timeout=timeout,
            heart_beat=heart_beat,
            dispatcher=dispatcher,
            zone=zone,
        )
        self._connection = DenonTelnetConnection(
            self,
            host,
            timeout=timeout,
            heart_beat=heart_beat,
        )
