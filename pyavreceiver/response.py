"""Define the telnet message public interface."""
from abc import ABC, abstractmethod


class Message(ABC):
    """Define the telnet Message interface."""

    @property
    @abstractmethod
    def message(self) -> str:
        """Return the message."""
        raise NotImplementedError

    @property
    @abstractmethod
    def raw_value(self) -> str:
        """Return the raw value from the message."""
        raise NotImplementedError

    @property
    @abstractmethod
    def state_update(self) -> dict:
        """Return the derived state update."""
        raise NotImplementedError

    @property
    @abstractmethod
    def command(self) -> str:
        """Return the command and parameter category."""
        raise NotImplementedError
