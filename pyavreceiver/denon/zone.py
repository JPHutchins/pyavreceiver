"""Define Denon/Marantz A/V Receiver Zones."""
from typing import Coroutine

from pyavreceiver.denon import const as denon_const
from pyavreceiver.zone import MainZone, Zone


class DenonAuxZone(Zone):
    """Implement a Denon A/V Receiver auxiliary zone."""

    @property
    def min_volume(self) -> int:
        """The min volume."""
        return denon_const.DEVICE_MIN_VOLUME

    @property
    def source_list(self):
        """Return a list of available input sources."""
        sources = [k for k, v in self.avr.sources.items() if v is not None]
        sources.append(denon_const.SOURCE_FOLLOW)
        return sources


class DenonMainZone(MainZone):
    """Implement a Denon A/V Receiver main zone."""

    @property
    def cinema_eq(self) -> bool:
        """The state of Audyssey cinema EQ."""
        return self.get(denon_const.ATTR_CINEMA_EQ)

    def set_cinema_eq(self, val: bool) -> Coroutine:
        """Request the receiver set Audyssey cinema EQ to val."""
        return self.set(denon_const.ATTR_CINEMA_EQ, val, 2)

    @property
    def dsx(self) -> bool:
        """The state of Audyssey DSX."""
        return self.get(denon_const.ATTR_DSX)

    def set_dsx(self, val: bool) -> Coroutine:
        """Request the receiver set Audyssey DSX to val."""
        return self.set(denon_const.ATTR_DSX, val, 2)

    @property
    def dynamic_eq(self) -> bool:
        """The state of Audyssey dynamic EQ."""
        return self.get(denon_const.ATTR_DYNAMIC_EQ)

    def set_dynamic_eq(self, val: bool) -> Coroutine:
        """Request the receiver set Audyssey dynamic EQ to val."""
        return self.set(denon_const.ATTR_DYNAMIC_EQ, val, 2)

    @property
    def multi_eq(self) -> str:
        """The state of Audyssey multi EQ."""
        return self.get(denon_const.ATTR_MULTI_EQ)

    def set_multi_eq(self, val: str) -> Coroutine:
        """Request the receiver set Audyssey multi EQ to val."""
        return self.set(denon_const.ATTR_MULTI_EQ, val, 2)

    @property
    def reference_level_offset(self) -> str:
        """The state of Audyssey reference level offset."""
        return self.get(denon_const.ATTR_REFLEV_OFFSET)

    def set_reference_level_offset(self, val: str) -> Coroutine:
        """Request the receiver set Audyssey reference level offset to val."""
        return self.set(denon_const.ATTR_REFLEV_OFFSET, val, 2)

    @property
    def min_volume(self) -> int:
        """The min volume."""
        return denon_const.DEVICE_MIN_VOLUME
