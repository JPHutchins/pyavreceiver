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
        dispatcher: Dispatcher = Dispatcher(),
        heart_beat: Optional[float] = denon_const.DEFAULT_HEART_BEAT,
        http_api=None,
        telnet: bool = True,
        timeout: float = denon_const.DEFAULT_TIMEOUT,
        zone_aux_class: Zone = DenonAuxZone,
        zone_main_class: DenonMainZone = DenonMainZone,
    ):
        super().__init__(
            host,
            dispatcher=dispatcher,
            heart_beat=heart_beat,
            http_api=http_api,
            telnet=telnet,
            timeout=timeout,
            zone_aux_class=zone_aux_class,
            zone_main_class=zone_main_class,
        )
        self._connection = DenonTelnetConnection(
            self,
            host,
            timeout=timeout,
            heart_beat=heart_beat,
        )
