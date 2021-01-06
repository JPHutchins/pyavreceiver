"""Define the interface of an A/V Receiver Zone."""
import asyncio
from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, Coroutine, Dict, Sequence, Union

from pyavreceiver import const
from pyavreceiver.command import Command


class Zone(ABC):
    """Define an Audio/Video Receiver zone."""

    def __init__(self, avr, zone: str = "main"):
        """Init the zone."""
        self._avr = avr
        self._zone_prefix = const.ZONE_PREFIX[zone.lower()]
        self._filter_func = define_filter(zone)
        self._commands = dict(filter(self._filter_func, avr.commands.items()))

    def get(self, name: str) -> str:
        """Get the current state of the attribute name."""
        return self.state.get(self._zone_prefix + name)

    def set(self, name: str, val=None, qos=0) -> Union[Coroutine, bool]:
        """Request the receiver set the name to val."""
        if qos == 0:
            command = self.commands[f"{self._zone_prefix}{name}"].set_val(val)
            self.telnet_connection.send_command(command)
            return True
        command = self.commands[f"{self._zone_prefix}{name}"].set_val(val, qos=qos)
        return self.telnet_connection.async_send_command(command)

    def update(self, name: str) -> Coroutine:
        """Request the receiver to send update of the value of name."""
        command = self.commands[name].set_query(qos=1)
        return self.telnet_connection.async_send_command(command)

    async def update_all(self):
        """Update all known attributes in commands."""
        tasks = []
        for name in self.commands:
            tasks.append(self.update(name))
        await asyncio.gather(*tasks)

    @property
    def avr(self):
        """Return the AVReceiver instance."""
        return self._avr

    @property
    def commands(self) -> Dict[str, Command]:
        """Get the commands for this zone."""
        return self._commands

    @property
    def state(self) -> dict:
        """Get the state of this zone."""
        return dict(filter(self._filter_func, self._avr.state.items()))

    @property
    def telnet_connection(self):
        """Return the TelnetConnection instance."""
        return self.avr.telnet_connection

    @property
    def available(self):
        """Return True if the device is available."""
        return self.avr.connection_state == const.STATE_CONNECTED

    @property
    @abstractmethod
    def source_list(self) -> Sequence[str]:
        """Return a list of available input sources."""

    @property
    def bass(self) -> int:
        """The state of bass."""
        return self.get(const.ATTR_BASS)

    def set_bass(self, val: float) -> Coroutine:
        """Request the receiver set the bass to val."""
        return self.set(const.ATTR_BASS, val, 1)

    @property
    def max_volume(self) -> int:
        """The max volume."""
        return self.get(const.ATTR_MAX_VOLUME)

    @property
    def mute(self) -> str:
        """The state of mute."""
        return self.get(const.ATTR_MUTE)

    def set_mute(self, val: bool) -> Coroutine:
        """Request the receiver set mute to val."""
        return self.set(const.ATTR_MUTE, val, 3)

    @property
    def power(self) -> str:
        """The state of zone power."""
        return self.get(const.ATTR_POWER)

    def set_power(self, val: bool) -> Coroutine:
        """Request the receiver set zone power to val."""
        return self.set(const.ATTR_POWER, val, 3)

    @property
    def source(self) -> str:
        """The state of source."""
        mapper = {v: k for k, v in self.avr.sources.items()}
        return mapper.get(self.get(const.ATTR_SOURCE))

    def set_source(self, val: str) -> Coroutine:
        """Request the receiver set the source to val."""
        return self.set(const.ATTR_SOURCE, val, 2)

    @property
    def treble(self) -> int:
        """The state of treble."""
        return self.get(const.ATTR_TREBLE)

    def set_treble(self, val: float) -> Coroutine:
        """Request the receiver set the treble to val."""
        return self.set(const.ATTR_TREBLE, val, 1)

    @property
    def volume(self) -> str:
        """The state of volume."""
        return self.get(const.ATTR_VOLUME)

    def set_volume(self, val: float) -> Coroutine:
        """Request the receiver set volume to val."""
        return self.set(const.ATTR_VOLUME, val, 2)

    def set_volume_down(self) -> bool:
        """Request the receiver turn the volume down."""
        return self.set(const.ATTR_VOLUME_DOWN)

    def set_volume_up(self) -> bool:
        """Request the receiver turn the volume up."""
        return self.set(const.ATTR_VOLUME_UP)


class MainZone(Zone):
    """Define an Audio/Video Receiver main zone.

    Attributes are ordered alphabetically.  Setters are prefixed with set_ and grouped with
    their corresponding property.
    """

    @property
    def dialog_level(self) -> str:
        """The state of dialog level."""
        return self.get(const.ATTR_DIALOG_LEVEL)

    def set_dialog_level(self, val) -> bool:
        """Request the receiver set dialog level to val."""
        return self.set(const.ATTR_DIALOG_LEVEL, val)

    @property
    def dsp_dynamic_range(self) -> str:
        """The state of DSP dynamic range."""
        return self.get(const.ATTR_DSP_DRC)

    def set_dsp_dynamic_range(self, val) -> bool:
        """Request the receiver set the DRC to val."""
        return self.set(const.ATTR_DSP_DRC, val)

    @property
    def dsp_mode(self) -> str:
        """The state of DSP mode."""
        return self.get(const.ATTR_DSP_MODE)

    def set_dsp_mode(self, val: str) -> bool:
        """Request the receiver set DSP mode to val."""
        return self.set(const.ATTR_DSP_MODE, val)

    @property
    def lfe_level(self) -> str:
        """The state of LFE level."""
        return self.get(const.ATTR_LFE_LEVEL)

    def set_lfe_level(self, val: float) -> bool:
        """Request the receiver set LFE level to val."""
        return self.set(const.ATTR_LFE_LEVEL, val)

    @property
    def meta_dynamic_range(self) -> str:
        """The state of metadata dynamic range control."""
        return self.get(const.ATTR_META_DRC)

    def set_meta_dynamic_range(self, val: str) -> bool:
        """Request the receiver set meta DRC to val."""
        return self.set(const.ATTR_META_DRC, val)

    @property
    def power(self) -> str:
        """The state of zone power."""
        return self.get(const.ATTR_ZONE1_POWER)

    def set_power(self, val: bool) -> Coroutine:
        """Request the receiver set zone power to val."""
        return self.set(const.ATTR_ZONE1_POWER, val, 3)

    @property
    def soundmode(self) -> str:
        """The state of soundmode."""
        return self.get(const.ATTR_SOUND_MODE)

    def set_soundmode(self, val: str) -> bool:
        """Request the receiver set the sound mode to val."""
        return self.set(const.ATTR_SOUND_MODE, val.lower())

    @property
    def sound_mode_list(self) -> Sequence[str]:
        """Get the list of available sound modes."""
        return [
            k.capitalize()
            for k, v in self.commands[const.ATTR_SOUND_MODE].values.items()
            if v is not None
        ]

    @property
    def subwoofer_one(self) -> bool:
        """The state of subwoofer one."""
        return self.get(const.ATTR_SUBWOOFER_ONE)

    def set_subwoofer_one(self, val: bool) -> bool:
        """Request the receiver set subwoofer one to val."""
        return self.set(const.ATTR_SUBWOOFER_ONE, val)

    @property
    def tone_control(self) -> str:
        """The state of tone control."""
        return self.get(const.ATTR_TONE_CONTROL)

    def set_tone_control(self, val: bool) -> bool:
        """Request the receiver set the treble to val."""
        return self.set(const.ATTR_TONE_CONTROL, val)


def filter_zones(item, correct_prefixes, wrong_prefixes, zone) -> bool:
    """Return true for item in zone."""
    name, _ = item
    for pre in wrong_prefixes:
        if name.startswith(pre):
            return False
    for pre in correct_prefixes:
        if name.startswith(pre):
            return True
    return zone == "main"  # Main zone default - anything not matched is main


def define_filter(zone) -> Callable:
    """Define the filter function."""
    wrong_prefixes, correct_prefixes = [], []
    for zone_name, prefix_list in const.ZONE_PREFIX_MAP.items():
        if zone_name != zone:
            wrong_prefixes.extend(prefix_list)
        else:
            correct_prefixes = prefix_list
    return partial(
        filter_zones,
        correct_prefixes=correct_prefixes,
        wrong_prefixes=wrong_prefixes,
        zone=zone,
    )
