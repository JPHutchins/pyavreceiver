"""Define Denon/Marantz commands."""
from collections import defaultdict
from typing import Union

import pyavreceiver.denon.const as denon_const
from pyavreceiver import const
from pyavreceiver.command import CommandValues, TelnetCommand, identity
from pyavreceiver.denon.parse import parse


class DenonTelnetCommand(TelnetCommand):
    """Representation of a Denon telnet message command."""

    def set_val(
        self, val: Union[int, float, str] = None, qos: int = None, sequence: int = -1
    ) -> TelnetCommand:
        """Format the command with argument and return."""

        qos = qos or self._qos

        if val is not None:
            val = (
                self._values.get(bool(val))
                or self._values.get(val)
                or self._values.get(str(val).lower())
                or val
            )
            val = "ON" if val is True else val
            val = "OFF" if val is False else val
            try:
                val = val.upper()
            except AttributeError:
                pass
            message = (
                f"{self._command}{self._val_pfx}"
                f"{self._func(val, zero=self._zero, valid_strings=self._valid_strings)}"
                f"{denon_const.TELNET_SEPARATOR}"
            )
        else:
            message = f"{self._command}{denon_const.TELNET_SEPARATOR}"
        return DenonTelnetCommand(
            name=self._name,
            command=self._command,
            values=self._values,
            val_pfx=self._val_pfx,
            func=self._func,
            zero=self._zero,
            val=val,
            message=message,
            valid_strings=self._valid_strings,
            qos=qos,
            sequence=sequence,
        )

    def set_query(self, qos: int = None) -> TelnetCommand:
        """Format the command with query and return."""
        if qos is None:
            qos = 0
        message = (
            f"{self._command}{self._val_pfx}{denon_const.TELNET_QUERY}"
            f"{denon_const.TELNET_SEPARATOR}"
        )
        return DenonTelnetCommand(
            name=self._name,
            command=self._command,
            values=self._values,
            val_pfx=self._val_pfx,
            func=self._func,
            zero=self._zero,
            val=denon_const.TELNET_QUERY,
            message=message,
            valid_strings=self._valid_strings,
            qos=qos,
        )


def get_command_lookup(command_dict):
    """Return the command lookup dict."""
    command_lookup = defaultdict(None)
    for cmd, entry in command_dict.items():
        try:
            val_range = entry.get(const.COMMAND_RANGE)
            zero = entry.get(const.COMMAND_ZERO)
            func = entry.get(const.COMMAND_FUNCTION)
            func = parse["num_to_db"] if func == const.FUNCTION_VOLUME else None
            valid_strings = entry.get(const.COMMAND_STRINGS)
        except AttributeError:
            val_range, zero, func, valid_strings = None, None, None, None

        if const.COMMAND_PARAMS not in entry:
            # No nested params, make entry and continue loop
            val_pfx = ""
            if const.COMMAND_NAME in entry:
                names = [entry[const.COMMAND_NAME]]
            elif const.COMMAND_NAMES in entry:
                names = entry[const.COMMAND_NAMES].values()
            else:
                names = [cmd]
            for name in names:
                add_command(
                    command_lookup,
                    entry,
                    name,
                    cmd,
                    val_pfx,
                    val_range,
                    zero,
                    func,
                    valid_strings,
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
                valid_strings,
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
                sub_valid_strings = sub_entry.get(const.COMMAND_STRINGS)
            except AttributeError:
                sub_val_range, sub_range_zero, sub_func, sub_valid_strings = (
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
                sub_valid_strings or valid_strings,
            )
    return command_lookup


def add_command(ref, entry, name, cmd, val_pfx, val_range, zero, func, valid_strings):
    """Add the command to the command dictionary, ref."""
    values = {}
    try:
        for item in entry:
            if str(item).startswith("^"):
                continue
            if entry[item] is not None:
                try:
                    values[entry[item].lower()] = item
                    if entry[item].lower() == "off":
                        values[False] = item
                    elif entry[item].lower() == "on":
                        values[True] = item
                except AttributeError:
                    values[entry[item]] = item
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
        valid_strings=valid_strings,
    )
