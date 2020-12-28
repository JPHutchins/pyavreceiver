"""Define the interface of an A/V Receiver Zone."""
from pyavreceiver import const


class Zone:
    """Define an Audio/Video Receiver zone."""

    def __init__(self, avr, zone: str = "main"):
        """Init the zone."""
        self._avr = avr
        self._zone_prefix = const.ZONE_PREFIX[zone.lower()]
        self._commands = avr._connection._command_lookup  # type: dict

    def get(self, name: str) -> str:
        """Get the current state of the nameibute name."""
        return self._avr.state.get(self._zone_prefix + name)

    def set(self, name: str, val=None) -> bool:
        """Request the receiver set the name to val."""
        # pylint: disable=protected-access
        if not self._avr.power:
            return False
        command = self._avr._connection._command_lookup[
            f"{self._zone_prefix}{name}"
        ].set_val(val)
        self._avr._connection.send_command(command)
        return True

    def update(self, name: str):
        """Request the receiver to send update of the value of name."""
        # pylint: disable=protected-access
        command = self._avr._connection._command_lookup[name].set_query()
        self._avr._connection.send_command(command)

    def update_all(self):
        """Update all known attributes in commands."""
        for name in self.commands:
            self.update(name)

    @property
    def commands(self) -> dict:
        """The dictionary of available commands."""
        return self._commands

    @property
    def bass(self) -> int:
        """The state of bass."""
        return self.get(const.ATTR_BASS)

    def set_bass(self, val: float) -> bool:
        """Request the receiver set the bass to val."""
        return self.set(const.ATTR_BASS, val)

    @property
    def mute(self) -> str:
        """The state of mute."""
        return self.get(const.ATTR_MUTE)

    def set_mute(self, val: bool) -> bool:
        """Request the receiver set mute to val."""
        return self.set(const.ATTR_MUTE, val)

    @property
    def power(self) -> str:
        """The state of zone power."""
        return self.get(const.ATTR_ZONE1_POWER)

    def set_power(self, val: bool) -> bool:
        """Request the receiver set zone power to val."""
        return self.set(const.ATTR_ZONE1_POWER, val)

    @property
    def source(self) -> str:
        """The state of source."""
        return self.get(const.ATTR_SOURCE)

    def set_source(self, val: str) -> bool:
        """Request the receiver set the source to val."""
        return self.set(const.ATTR_SOURCE, val)

    @property
    def treble(self) -> int:
        """The state of treble."""
        return self.get(const.ATTR_TREBLE)

    def set_treble(self, val: float) -> bool:
        """Request the receiver set the treble to val."""
        return self.set(const.ATTR_TREBLE, val)

    @property
    def volume(self) -> str:
        """The state of volume."""
        return self.get(const.ATTR_VOLUME)

    def set_volume(self, val: float) -> bool:
        """Request the receiver set volume to val."""
        return self.set(const.ATTR_VOLUME, val)

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
    def soundmode(self) -> str:
        """The state of soundmode."""
        return self.get(const.ATTR_SOUND_MODE)

    def set_soundmode(self, val: str) -> bool:
        """Request the receiver set the sound mode to val."""
        return self.set(const.ATTR_SOUND_MODE, val)

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
