"""Define commands."""
from abc import ABC, abstractmethod


class TelnetCommand(ABC):
    """Define the telnet command interface."""

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
