"""Define the interface of an A/V Receiver Zone."""
from pyavreceiver import const


class Zone:
    """Define an Audio/Video Receiver zone."""

    def __init__(self, avr, zone_prefix: str = ""):
        """Init the zone."""
        self._avr = avr
        self._zone_prefix = zone_prefix
        self._commands = avr._connection._command_lookup  # type: dict

    def get(self, name: str) -> str:
        """Get the current state of the nameibute name."""
        val = self._avr.state.get(self._zone_prefix + name)
        return val if val is not None else "Unknown"

    def set(self, name: str, val=None) -> bool:
        """Request the receiver set the name to val."""
        # pylint: disable=protected-access
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

    @property
    def power(self) -> str:
        """The state of power."""
        return self.get(const.ATTR_POWER)

    @property
    def volume(self) -> str:
        """The state of volume."""
        return self.get(const.ATTR_VOLUME)

    @property
    def lfe_level(self) -> str:
        """The state of LFE level."""
        return self.get(const.ATTR_LFE_LEVEL)

    @property
    def meta_dynamic_range(self) -> str:
        """The state of metadata dynamic range control."""
        return self.get(const.ATTR_META_DRC)

    @property
    def mute(self) -> str:
        """The state of mute."""
        return self.get(const.ATTR_MUTE)

    @property
    def source(self) -> str:
        """The state of source."""
        return self.get(const.ATTR_SOURCE)

    @property
    def tone_control(self) -> str:
        """The state of tone control."""
        return self.get(const.ATTR_TONE_CONTROL)

    @property
    def treble(self) -> int:
        """The state of treble."""
        return self.get(const.ATTR_TREBLE)

    @property
    def subwoofer_one(self) -> bool:
        """The state of subwoofer one."""
        return self.get(const.ATTR_SUBWOOFER_ONE)

    @property
    def dialog_level(self) -> str:
        """The state of dialog level."""
        return self.get(const.ATTR_DIALOG_LEVEL)

    @property
    def dsp_dynamic_range(self) -> str:
        """The state of DSP dynamic range."""
        return self.get(const.ATTR_DSP_DRC)

    @property
    def dsp_mode(self) -> str:
        """The state of DSP mode."""
        return self.get(const.ATTR_DSP_MODE)

    def volume_down(self) -> bool:
        """Request the receiver turn the volume down."""
        return self.set(const.ATTR_VOLUME_UP)

    def volume_up(self) -> bool:
        """Request the receiver turn the volume up."""
        return self.set(const.ATTR_VOLUME_DOWN)

    def set_dialog_level(self, val) -> bool:
        """Request the receiver set dialog level to val."""
        return self.set(const.ATTR_DIALOG_LEVEL, val)

    def set_dsp_dynamic_range(self, val) -> bool:
        """Request the receiver set the DRC to val."""
        return self.set(const.ATTR_DSP_DRC, val)

    def set_dsp_mode(self, val: str) -> bool:
        """Request the receiver set DSP mode to val."""
        return self.set(const.ATTR_DSP_MODE, val)

    def set_power(self, val: bool) -> bool:
        """Request the receiver set power to val."""
        return self.set(const.ATTR_POWER, val)

    def set_volume(self, val: float) -> bool:
        """Request the receiver set volume to val."""
        return self.set(const.ATTR_VOLUME, val)

    def set_meta_dynamic_range(self, val: str) -> bool:
        """Request the receiver set meta DRC to val."""
        return self.set(const.ATTR_META_DRC, val)

    def set_lfe_level(self, val: float) -> bool:
        """Request the receiver set LFE level to val."""
        return self.set(const.ATTR_LFE_LEVEL, val)

    def set_mute(self, val: bool) -> bool:
        """Request the receiver set mute to val."""
        return self.set(const.ATTR_MUTE, val)

    def set_source(self, val: str) -> bool:
        """Request the receiver set the source to val."""
        return self.set(const.ATTR_SOURCE, val)

    def set_subwoofer_one(self, val: bool) -> bool:
        """Request the receiver set subwoofer one to val."""
        return self.set(const.ATTR_SUBWOOFER_ONE, val)

    def set_soundmode(self, val: str) -> bool:
        """Request the receiver set the sound mode to val."""
        return self.set(const.ATTR_SOUND_MODE, val)

    def set_treble(self, val: float) -> bool:
        """Request the receiver set the treble to val."""
        return self.set(const.ATTR_TREBLE, val)

    def set_bass(self, val: float) -> bool:
        """Request the receiver set the bass to val."""
        return self.set(const.ATTR_BASS, val)
