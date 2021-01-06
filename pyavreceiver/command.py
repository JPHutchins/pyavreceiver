"""Define commands."""
from abc import ABC, abstractmethod
from typing import Callable, Sequence, Tuple, Union

from pyavreceiver.error import AVReceiverInvalidArgumentError


def identity(arg, **kwargs):
    """The identity function returns the input."""
    # pylint: disable=unused-argument
    return arg


class CommandValues:
    """Possible values for a command."""

    __slots__ = ("_values",)

    def __init__(self, values: dict):
        self._values = values
        if self._values.get("min") is not None:
            self._values["min"] = self._values.get("min")
        if self._values.get("max") is not None:
            self._values["max"] = self._values.get("max")

    def __repr__(self) -> str:
        return str(self._values)

    def __str__(self) -> str:
        return str({x for x in self._values if self._values[x] is not None})

    def get(self, name) -> Union[int, str, float]:
        """Patch to dict.get()."""
        return self._values.get(name)

    def update(self, _dict):
        """Patch to dict.update()."""
        self._values.update(_dict)

    def items(self) -> Sequence[Tuple[str, Union[int, str, float]]]:
        """Patch to dict.items()."""
        return self._values.items()

    def __getattr__(self, name: str) -> Union[int, str, float]:
        if name in self._values:
            return self._values[name]
        raise AVReceiverInvalidArgumentError

    def __getitem__(self, name: str) -> Union[int, str, float]:
        if name in self._values:
            return self._values[name]
        raise AVReceiverInvalidArgumentError

    def __setitem__(self, name: str, val):
        """Only set if name does not exist."""
        if name not in self._values:
            self._values[name] = val


class Command(ABC):
    """Command base class."""


class TelnetCommand(Command, ABC):
    """Define the telnet command interface."""

    __slots__ = (
        "_name",
        "_command",
        "_values",
        "_val_pfx",
        "_func",
        "_zero",
        "_val",
        "_valid_strings",
        "_message",
        "_qos",
        "_sequence",
        "_retries",
    )

    def __init__(
        self,
        *,
        name: str = None,
        command: str = None,
        values: CommandValues = None,
        val_pfx: str = "",
        func: Callable = identity,
        zero: int = 0,
        val: Union[float, int, str] = None,
        valid_strings: list = None,
        message: str = None,
        qos: int = 0,
        sequence: int = -1
    ):
        self._name = name
        self._command = command
        self._values = values
        self._val_pfx = val_pfx
        self._func = func
        self._zero = zero
        self._val = val
        self._valid_strings = valid_strings
        self._message = message
        self._qos = qos
        self._sequence = sequence
        self._retries = [0, 1, 2, 2, 2][qos]  # qos defines number of retries

    def __hash__(self):
        return self._sequence

    def __eq__(self, other):
        try:
            return self._sequence == other._sequence
        except AttributeError:
            return False

    @abstractmethod
    def set_val(self, val: Union[int, float, str], qos: int = None, sequence: int = -1):
        """Format the command with argument and return."""

    @abstractmethod
    def set_query(self, qos: int = None) -> str:
        """Format the command with query and return."""

    def init_values(self, values: CommandValues) -> None:
        """Init the values attribite with values."""
        self._values = values

    def set_sequence(self, sequence) -> None:
        """Set the sequence to use as hash and id."""
        self._sequence = sequence

    def lower_qos(self):
        """Lower the QoS level by one."""
        self._qos -= 1

    def raise_qos(self):
        """Raise the QoS level by one."""
        self._qos += 1

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
    def retries(self) -> int:
        """The number of retries to attempt if the command fails."""
        return self._retries

    @property
    def val(self) -> str:
        """The argument of the command."""
        return self._val

    @property
    def values(self) -> list:
        """Return the valid argument values."""
        return self._values

    @property
    def qos(self) -> int:
        """Return the QoS level."""
        return self._qos
