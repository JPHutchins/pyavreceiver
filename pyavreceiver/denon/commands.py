"""Define Denon/Marantz commands."""
from pyavreceiver import const
from pyavreceiver.command import TelnetCommand
from pyavreceiver.denon.parse import parse
import pyavreceiver.denon.const as denon_const


class DenonTelnetCommand(TelnetCommand):
    """Representation of a Denon telnet message command."""

    def __init__(
        self,
        name: str,
        command: str,
        values: list,
        val_pfx: str,
        func,
        zero: int,
        val=None,
        message: str = None,
    ):
        self._name = name
        self._command = command
        self._values = values
        self._val_pfx = val_pfx
        self._func = func or identity
        self._zero = zero
        self._val = val

        self._val_translate = {"True": "ON", "False": "OFF"}
        self._message = message

    def set_val(self, val) -> str:
        """Format the command with argument and return."""
        val = self._val_translate.get(str(val)) or val
        try:
            val = val.upper()
        except AttributeError:
            pass
        message = (
            f"{self._command}{self._val_pfx}{self._func(val, zero=self._zero)}"
            f"{denon_const.TELNET_SEPARATOR}"
        )
        return DenonTelnetCommand(
            self._name,
            self._command,
            self._values,
            self._val_pfx,
            self._func,
            self._zero,
            val,
            message,
        )

    def set_query(self) -> str:
        """Format the command with query and return."""
        message = (
            f"{self._command}{self._val_pfx}{denon_const.TELNET_QUERY}"
            f"{denon_const.TELNET_SEPARATOR}"
        )
        return DenonTelnetCommand(
            self._name,
            self._command,
            self._values,
            self._val_pfx,
            self._func,
            self._zero,
            denon_const.TELNET_QUERY,
            message,
        )

    @property
    def command(self) -> str:
        """The command portion of the message."""
        return self._command

    @property
    def message(self) -> str:
        """The complete message; command + argument."""
        if not self._message:
            raise Exception
        return self._message

    @property
    def name(self) -> str:
        """The name of the command."""
        return self._name

    @property
    def val(self) -> str:
        """The argument of the command."""
        return self._val

    @property
    def values(self) -> list:
        """Return the valid argument values."""
        return self._values


def get_command_lookup(command_dict):
    """Return the command lookup dict."""
    command_lookup = {}
    for cmd, entry in command_dict.items():
        try:
            val_range = entry.get(const.COMMAND_RANGE)
            zero = entry.get(const.COMMAND_ZERO)
            func = entry.get(const.COMMAND_FUNCTION)
            func = parse["num_to_db"] if func == const.FUNCTION_VOLUME else None
        except AttributeError:
            val_range, zero, func = None, None, None

        if const.COMMAND_PARAMS not in entry:
            # No nested params, make entry and continue loop
            val_pfx = ""
            if const.COMMAND_NAME in entry:
                name = entry[const.COMMAND_NAME]
            else:
                name = cmd
            add_command(
                command_lookup, entry, name, cmd, val_pfx, val_range, zero, func
            )
            continue

        if const.COMMAND_PARAMS in entry and const.COMMAND_NAME in entry:
            # Nested params and main entry, make entry and stay in loop
            val_pfx = ""
            if const.COMMAND_NAME in entry:
                name = entry[const.COMMAND_NAME]
            else:
                name = cmd
            add_command(
                command_lookup, entry, name, cmd, val_pfx, val_range, zero, func
            )

        # Nested params, iterate and make entries
        val_pfx = " "
        for prm, sub_entry in entry.items():
            if prm.startswith("^"):
                # prm is not a command
                continue
            try:
                sub_val_range = sub_entry.get(const.COMMAND_RANGE)
                sub_range_zero = sub_entry.get(const.COMMAND_ZERO)
                sub_func = sub_entry.get(const.COMMAND_FUNCTION)
                sub_func = (
                    parse["num_to_db"] if sub_func == const.FUNCTION_VOLUME else func
                )
            except AttributeError:
                sub_val_range, sub_range_zero, sub_func = None, None, None
            if sub_entry and const.COMMAND_NAME in sub_entry:
                full_name = sub_entry[const.COMMAND_NAME]
            elif name := entry.get(const.COMMAND_NAME):
                full_name = f"{name}/{prm}"
            else:
                full_name = f"{cmd}/{prm}"
            command = f"{cmd}{prm}"
            add_command(
                command_lookup,
                sub_entry,
                full_name,
                command,
                val_pfx,
                sub_val_range,
                sub_range_zero,
                sub_func,
            )
    return command_lookup


def add_command(ref, entry, name, cmd, val_pfx, val_range, zero, func):
    """Add the command to the command dictionary, ref."""
    values = []
    try:
        for item in entry:
            if str(item).startswith("^"):
                continue
            values.append(item)
    except TypeError:
        pass
    if val_range is not None and func:
        val_range = [func(str(x), zero) for x in val_range]
    values = values or val_range
    ref[name] = DenonTelnetCommand(
        name=name,
        command=cmd,
        values=values,
        val_pfx=val_pfx,
        func=parse["db_to_num"] if func else None,
        zero=zero,
    )


def identity(args, **kwargs):
    """The identity function returns the input."""
    # pylint: disable=unused-argument
    return args
