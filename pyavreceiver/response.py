"""Define the telnet message public interface."""
from abc import ABC, abstractmethod


class Message(ABC):
    """Define the telnet Message interface."""

    @property
    @abstractmethod
    def message(self) -> str:
        """Return the message."""

    @property
    @abstractmethod
    def raw_value(self) -> str:
        """Return the raw value from the message."""

    @property
    @abstractmethod
    def state_update(self) -> dict:
        """Return the derived state update."""

    @property
    @abstractmethod
    def command(self) -> str:
        """Return the command and parameter category."""

    @property
    def new_command(self) -> dict:
        """Return new command if it was parsed, else None."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name. Maybe the same as command."""
