"""Define Denon/Marantz commands."""
import pyavreceiver.denon.const as denon_const
from pyavreceiver import const
from pyavreceiver.command import TelnetCommand
from pyavreceiver.denon.parse import parse
from pyavreceiver.error import AVReceiverInvalidArgumentError


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
        strings=None,
    ):
        self._name = name
        self._command = command
        self._values = values
        self._val_pfx = val_pfx
        self._func = func or identity
        self._zero = zero
        self._val = val
        self._strings = strings

        self._val_translate = {"True": "ON", "False": "OFF"}
        self._message = message

    def set_val(self, val=None) -> str:
        """Format the command with argument and return."""
        if val is not None:
            val = self._val_translate.get(str(val)) or val
            val = self._values.get(str(val).lower()) or val
            try:
                val = val.upper()
            except AttributeError:
                pass
            message = (
                f"{self._command}{self._val_pfx}{self._func(val, zero=self._zero, strings=self._strings)}"
                f"{denon_const.TELNET_SEPARATOR}"
            )
        else:
            message = f"{self._command}{denon_const.TELNET_SEPARATOR}"
        return DenonTelnetCommand(
            self._name,
            self._command,
            self._values,
            self._val_pfx,
            self._func,
            self._zero,
            val,
            message,
            self._strings,
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
            self._strings,
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


class CommandValues:
    """Possible values for a command."""

    def __init__(self, values: dict):
        self._values = values
        self._values["min"] = self._values.get("min")
        self._values["max"] = self._values.get("max")

    def __repr__(self):
        return str(self._values)

    def __str__(self):
        return str({x for x in self._values if self._values[x] is not None})

    def get(self, name):
        """Patch to dict.get()."""
        return self._values.get(name)

    def __getattr__(self, name: str) -> str:
        if name in self._values:
            return self._values[name]
        raise AVReceiverInvalidArgumentError

    def __getitem__(self, name: str) -> str:
        if name in self._values:
            return self._values[name]
        raise AVReceiverInvalidArgumentError


def get_command_lookup(command_dict):
    """Return the command lookup dict."""
    command_lookup = {}
    for cmd, entry in command_dict.items():
        try:
            val_range = entry.get(const.COMMAND_RANGE)
            zero = entry.get(const.COMMAND_ZERO)
            func = entry.get(const.COMMAND_FUNCTION)
            func = parse["num_to_db"] if func == const.FUNCTION_VOLUME else None
            strings = entry.get(const.COMMAND_STRINGS)
        except AttributeError:
            val_range, zero, func, strings = None, None, None, None

        if const.COMMAND_PARAMS not in entry:
            # No nested params, make entry and continue loop
            val_pfx = ""
            if const.COMMAND_NAME in entry:
                name = entry[const.COMMAND_NAME]
            else:
                name = cmd
            add_command(
                command_lookup,
                entry,
                name,
                cmd,
                val_pfx,
                val_range,
                zero,
                func,
                strings,
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
                command_lookup,
                entry,
                name,
                cmd,
                val_pfx,
                val_range,
                zero,
                func,
                strings,
            )

        # Nested params, iterate and make entries
        val_pfx = " "
        for prm, sub_entry in entry.items():
            if prm.startswith("^"):
                # prm is not a command
                continue
            try:
                print(prm)
                sub_val_range = sub_entry.get(const.COMMAND_RANGE)
                sub_range_zero = sub_entry.get(const.COMMAND_ZERO)
                sub_func = sub_entry.get(const.COMMAND_FUNCTION)
                sub_func = (
                    parse["num_to_db"] if sub_func == const.FUNCTION_VOLUME else func
                )
                sub_strings = sub_entry.get(const.COMMAND_STRINGS)
            except AttributeError:
                sub_val_range, sub_range_zero, sub_func, sub_strings = (
                    None,
                    None,
                    None,
                    None,
                )
            if sub_entry and const.COMMAND_NAME in sub_entry:
                full_name = sub_entry[const.COMMAND_NAME]
            elif name := entry.get(const.COMMAND_NAME):
                full_name = f"{name}_{prm.lower()}"
            else:
                full_name = f"{cmd}_{prm}"
            command = f"{cmd}{prm}"
            add_command(
                command_lookup,
                sub_entry,
                full_name,
                command,
                val_pfx,
                sub_val_range or val_range,
                sub_range_zero or zero,
                sub_func or func,
                sub_strings or strings,
            )
    return command_lookup


def add_command(ref, entry, name, cmd, val_pfx, val_range, zero, func, strings):
    """Add the command to the command dictionary, ref."""
    if name == "channel_level_fl":
        print("channel", entry, val_range)
    values = {}
    try:
        for item in entry:
            if str(item).startswith("^"):
                continue
            if entry[item] is not None:
                values[entry[item].lower()] = item
            values[item.lower()] = item
    except (TypeError, AttributeError):
        pass
    func = func or identity
    if val_range is not None:
        val_range = {
            "min": func(str(val_range[0]), zero=zero),
            "max": func(str(val_range[1]), zero=zero),
        }
    if values and val_range:
        values = values.update(val_range)
    values = val_range or values
    ref[name] = DenonTelnetCommand(
        name=name,
        command=cmd,
        values=CommandValues(values),
        val_pfx=val_pfx,
        func=parse["db_to_num"] if func else None,
        zero=zero,
        strings=strings,
    )


def identity(args, **kwargs):
    """The identity function returns the input."""
    # pylint: disable=unused-argument
    return args
