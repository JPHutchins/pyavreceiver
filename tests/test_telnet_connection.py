"""Tests for the TelnetConnection class."""
import asyncio
from typing import Union
from unittest.mock import patch

import pytest

from pyavreceiver import const
from pyavreceiver.command import TelnetCommand
from pyavreceiver.dispatch import Dispatcher
from tests import GenericTelnetConnection


class FakeAvr:
    """Mock AVR."""

    def __init__(self):
        self.dispatcher = Dispatcher()


class GenericCommand(TelnetCommand):
    """Generic Telnet Command."""

    def set_val(
        self, val: Union[int, float, str] = None, qos: int = 0, sequence: int = -1
    ) -> TelnetCommand:
        return GenericCommand(
            command=self._command, val=val, qos=qos, message=self._command + str(val)
        )

    def set_query(self, qos=0) -> TelnetCommand:
        return self.set_val("?", 0)


@patch("pyavreceiver.const.DEFAULT_COMMAND_EXPIRATION", 0.25)
@pytest.mark.asyncio
async def test_command_expires(mock_telnet):
    """Test command expires."""

    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")
    await conn.init()

    command = GenericCommand(command="a").set_val(1, 4)
    response = conn.async_send_command(command)
    assert await response is None
    await conn.disconnect()


@pytest.mark.asyncio
async def test_cancel_tasks(mock_telnet):
    """Test clear queues."""

    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")
    await conn.init()

    command = GenericCommand(command="a").set_val(1, 4)
    response = conn.async_send_command(command)
    # pylint: disable=protected-access
    conn._expected_responses.cancel_tasks()
    conn._command_queue.clear()
    assert conn._command_queue.is_empty
    assert await response is None

    responses = [
        conn.async_send_command(GenericCommand(command="a").set_val(1, 3)),
        conn.async_send_command(GenericCommand(command="b").set_val(1, 3)),
        conn.async_send_command(GenericCommand(command="c").set_val(1, 3)),
        conn.async_send_command(GenericCommand(command="d").set_val(1, 3)),
    ]
    conn._expected_responses.cancel_tasks()
    results = await asyncio.gather(*responses)
    for result in results:
        assert result is None

    await conn.disconnect()


@pytest.mark.asyncio
async def test_qos(response_in_order_telnet):
    """Test send command QoS."""

    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")
    await conn.init()
    await asyncio.sleep(1)

    command = GenericCommand(command="a").set_val(1, 3)
    response = conn.async_send_command(command)
    assert await response == "OK!"

    command = GenericCommand(command="b").set_val(1, 1)
    response = conn.async_send_command(command)
    assert await response == "OK!"

    command = GenericCommand(command="c").set_val(1, 2)
    response = conn.async_send_command(command)
    assert await response == "OK!"

    command = GenericCommand(command="d").set_val(1, 1)
    response = conn.async_send_command(command)
    assert await response == "OK!"

    await conn.disconnect()


@pytest.mark.asyncio
async def test_qos_slow_and_fail(slow_then_wrong_telnet):
    """Test send command QoS."""

    conn = GenericTelnetConnection(FakeAvr(), "127.0.0.1")
    await conn.init()
    await asyncio.sleep(1)

    command = GenericCommand(command="a").set_val(1, 3)
    response = conn.async_send_command(command)
    assert await response == "OK!"

    command = GenericCommand(command="b").set_val(1, 3)
    assert await conn.async_send_command(command) is None

    await conn.disconnect()


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
