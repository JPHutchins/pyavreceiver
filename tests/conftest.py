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
