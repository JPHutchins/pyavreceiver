"""Define Denon/Marantz A/V Receiver Zones."""
from pyavreceiver.denon import const as denon_const
from pyavreceiver.zone import Zone


class DenonZone(Zone):
    """Implement a Denon A/V Receiver zone."""

    @property
    def audyssey_dynamic_eq(self) -> str:
        """The state of Audyssey dynamic EQ."""
        return self.get(denon_const.ATTR_DYNAMIC_EQ)

    def set_audyssey_dynamic_eq(self, val: bool) -> bool:
        """Request the receiver set Audyssey dynamic EQ to val."""
        return self.set(denon_const.ATTR_DYNAMIC_EQ, val)
