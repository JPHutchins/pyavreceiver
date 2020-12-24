"""Tests for the TelnetConnection class."""
import asyncio

import pytest

from pyavreceiver import const
from pyavreceiver.dispatch import Dispatcher
from tests import GenericTelnetConnection


class FakeAvr:
    """Mock AVR."""

    def __init__(self):
        self.dispatcher = Dispatcher()


def test_init():
    """Test init sets properties."""
    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")
    assert conn.host == "127.0.0.1"
    assert conn.port == 4000
    assert conn.state == const.STATE_DISCONNECTED


@pytest.mark.asyncio
async def test_connect(mock_telnet):
    """Test connect to telnet device."""
    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")
    await conn.init()
    assert conn.state == const.STATE_CONNECTED

    await conn.disconnect()


@pytest.mark.asyncio
async def test_disconnect(mock_telnet):
    """Test disconnect from telnet device."""
    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")
    await conn.init()
    assert conn.state == const.STATE_CONNECTED

    await conn.disconnect()
    assert conn.state == const.STATE_DISCONNECTED


@pytest.mark.asyncio
async def test_heartbeat(mock_telnet):
    """Test connect to telnet device."""
    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1", heart_beat=0.5)
    await conn.init()
    await asyncio.sleep(1)

    assert len(mock_telnet) == 1
    assert mock_telnet[0] == "PW?\r"

    await conn.disconnect()


@pytest.mark.asyncio
async def test_connect_fails():
    """Test connect to non-existing device."""
    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")

    with pytest.raises(Exception):
        await conn.init()
    assert conn.state == const.STATE_DISCONNECTED

    await conn.disconnect()


@pytest.mark.asyncio
async def test_connect_timeout(mock_telnet):
    """Test connect to unresponsive device."""
    conn = GenericTelnetConnection(FakeAvr(), "www.google.com", timeout=1)

    with pytest.raises(Exception):
        await conn.init()
    assert conn.state == const.STATE_DISCONNECTED

    with pytest.raises(Exception):
        await conn.init(auto_reconnect=True)
    assert conn.state == const.STATE_DISCONNECTED

    await conn.disconnect()
