"""Define Denon/Marantz A/V Receiver Zones."""
from pyavreceiver.denon import const as denon_const
from pyavreceiver.zone import MainZone, Zone


class DenonAuxZone(Zone):
    """Implement a Denon A/V Receiver auxiliary zone."""

    @property
    def source_list(self):
        """Return a list of available input sources."""
        sources = [k for k, v in self.avr.sources.items() if v is not None]
        sources.append(denon_const.SOURCE_FOLLOW)
        return sources


class DenonMainZone(MainZone):
    """Implement a Denon A/V Receiver zone."""

    @property
    def audyssey_dynamic_eq(self) -> str:
        """The state of Audyssey dynamic EQ."""
        return self.get(denon_const.ATTR_DYNAMIC_EQ)

    def set_audyssey_dynamic_eq(self, val: bool) -> bool:
        """Request the receiver set Audyssey dynamic EQ to val."""
        return self.set(denon_const.ATTR_DYNAMIC_EQ, val)

    @property
    def source_list(self):
        """Return a list of available input sources."""
        return [k for k, v in self.avr.sources.items() if v is not None]
