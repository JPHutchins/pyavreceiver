"""Implement the AV Receiver interface."""
from typing import Optional

from pyavreceiver.dispatch import Dispatcher
from pyavreceiver.receiver import AVReceiver
from pyavreceiver.zone import MainZone, Zone


class TemplateReceiver(AVReceiver):
    """Representation of an A/V Receiver."""

    def __init__(
        self,
        host,
        *,
        dispatcher: Dispatcher = Dispatcher(),
        heart_beat: Optional[float],
        http_api=None,
        telnet: bool = True,
        timeout: float,
        zone_aux_class: Zone,
        zone_main_class: MainZone,
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
        self._connection = None  # Instance to your telnet, websocket, etc. connection
