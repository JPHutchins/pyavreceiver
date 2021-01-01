"""Define a Denon/Marantz Audio Video Receiver."""
from typing import Optional

from pyavreceiver.denon import const as denon_const
from pyavreceiver.denon.telnet_connection import DenonTelnetConnection
from pyavreceiver.denon.zone import DenonAuxZone, DenonMainZone
from pyavreceiver.dispatch import Dispatcher
from pyavreceiver.receiver import AVReceiver
from pyavreceiver.zone import Zone


class DenonReceiver(AVReceiver):
    """Representation of a Denon or Marantz A/V Receiver."""

    def __init__(
        self,
        host,
        *,
        telnet: bool = True,
        http: bool = True,
        http_api=None,
        upnp: bool = True,
        timeout: float = denon_const.DEFAULT_TIMEOUT,
        heart_beat: Optional[float] = denon_const.DEFAULT_HEART_BEAT,
        dispatcher: Dispatcher = Dispatcher(),
        main_zone: DenonMainZone = DenonMainZone,
        aux_zone: Zone = DenonAuxZone
    ):
        super().__init__(
            host,
            telnet=telnet,
            http=http,
            http_api=http_api,
            upnp=upnp,
            timeout=timeout,
            heart_beat=heart_beat,
            dispatcher=dispatcher,
            main_zone=main_zone,
            aux_zone=aux_zone,
        )
        self._connection = DenonTelnetConnection(
            self,
            host,
            timeout=timeout,
            heart_beat=heart_beat,
        )
