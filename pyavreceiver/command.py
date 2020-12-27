"""Define commands."""
from abc import ABC, abstractmethod

from pyavreceiver.error import AVReceiverInvalidArgumentError


def identity(arg, **kwargs):
    """The identity function returns the input."""
    # pylint: disable=unused-argument
    return arg


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


class TelnetCommand(ABC):
    """Define the telnet command interface."""

    def __init__(
        self,
        *,
        name: str,
        command: str,
        values: CommandValues,
        val_pfx: str = "",
        func=identity,
        zero: int = 0,
        val=None,
        valid_strings: list = None,
        message: str = None,
    ):
        self._name = name
        self._command = command
        self._values = values
        self._val_pfx = val_pfx
        self._func = func
        self._zero = zero
        self._val = val
        self._valid_strings = valid_strings

        self._val_translate = {"True": "ON", "False": "OFF"}
        self._message = message

    @abstractmethod
    def set_val(self, val) -> str:
        """Format the command with argument and return."""

    @abstractmethod
    def set_query(self) -> str:
        """Format the command with query and return."""

    @property
    @abstractmethod
    def command(self) -> str:
        """The command portion of the message."""

    @property
    @abstractmethod
    def message(self) -> str:
        """The complete message; command + argument."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the command."""

    @property
    @abstractmethod
    def val(self) -> str:
        """The argument of the command."""

    @property
    @abstractmethod
    def values(self) -> list:
        """Return the valid argument values."""
