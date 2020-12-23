"""Tests for command base classes."""
import pytest

from pyavreceiver.command import TelnetCommand


def test_telnet_command():
    """Test telnet command abstract base class."""
    with pytest.raises(TypeError):
        # pylint: disable=abstract-class-instantiated
        TelnetCommand()
