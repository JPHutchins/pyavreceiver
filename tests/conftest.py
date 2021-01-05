"""Test fixtures for pyheos."""
import asyncio

import pytest
import telnetlib3


@pytest.fixture(name="mock_telnet")
def mock_telnet_fixture(event_loop: asyncio.AbstractEventLoop):
    """Mock a silent telnet server."""
    messages = []

    async def shell(reader: telnetlib3.stream_reader, writer: telnetlib3.stream_writer):
        message = await reader.readuntil(separator=b"\r")
        if message:
            msg = message.decode()
            messages.append(msg)

    coro = telnetlib3.create_server(port=4000, shell=shell)
    server = event_loop.run_until_complete(coro)
    yield messages
    server.close()
    event_loop.run_until_complete(server.wait_closed())


@pytest.fixture(name="response_in_order_telnet")
def mock_telnet_in_order(event_loop: asyncio.AbstractEventLoop):
    """Mock a silent telnet server."""

    async def shell(reader: telnetlib3.TelnetReader, writer: telnetlib3.TelnetWriter):
        await reader.readuntil(separator=b"\r")
        writer.write("PWON\ra1\r")
        await writer.drain()
        await asyncio.sleep(1)

        writer.write("a\r")
        await writer.drain()

        await asyncio.sleep(0.05)
        writer.write("b\r")
        await writer.drain()

        await asyncio.sleep(0.05)
        writer.write("c\r")
        await writer.drain()

        await asyncio.sleep(0.05)
        writer.write("d\r")
        await writer.drain()

    coro = telnetlib3.create_server(port=4000, shell=shell)
    server = event_loop.run_until_complete(coro)
    yield
    server.close()
    event_loop.run_until_complete(server.wait_closed())


@pytest.fixture(name="slow_then_wrong_telnet")
def mock_telnet_echo(event_loop: asyncio.AbstractEventLoop):
    """Mock a silent telnet server."""

    async def shell(reader: telnetlib3.TelnetReader, writer: telnetlib3.TelnetWriter):
        await reader.readuntil(separator=b"\r")
        writer.write("PWON\ra1\r")
        await writer.drain()

        await asyncio.sleep(1)
        writer.write("a\r")
        await writer.drain()

        await asyncio.sleep(0.25)
        writer.write("a\r")
        await writer.drain()

        await asyncio.sleep(0.25)
        writer.write("a\r")
        await writer.drain()

    coro = telnetlib3.create_server(port=4000, shell=shell)
    server = event_loop.run_until_complete(coro)
    yield
    server.close()
    event_loop.run_until_complete(server.wait_closed())


@pytest.fixture
def handler():
    """Fixture handler to mock in the dispatcher."""

    def target(*args, **kwargs):
        target.fired = True
        target.args = args
        target.kwargs = kwargs

    target.fired = False
    return target


@pytest.fixture
def async_handler():
    """Fixture async handler to mock in the dispatcher."""

    async def target(*args, **kwargs):
        target.fired = True
        target.args = args
        target.kwargs = kwargs

    target.fired = False
    return target
