"""Define persistent connection to an AV Receiver."""
import asyncio
import logging
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict, deque
from datetime import datetime, timedelta
from typing import Optional

import telnetlib3

from pyavreceiver import const
from pyavreceiver.response import Message

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)


class TelnetConnection(ABC):
    """Define the telnet connection interface."""

    def __init__(
        self,
        avr,
        host: str,
        *,
        port: int = const.CLI_PORT,
        timeout: float = const.DEFAULT_TIMEOUT,
        heart_beat: Optional[float] = const.DEFAULT_HEART_BEAT,
    ):
        """Init the connection."""
        self._avr = avr
        self.host = host
        self.port = port
        self.commands = None
        self._command_dict = {}
        self._command_lookup = {}
        self._learned_commands = {}
        self.timeout = timeout  # type: int
        self._reader = None  # type: telnetlib3.TelnetReader
        self._writer = None  # type: telnetlib3.TelnetWriter
        self._response_handler_task = None  # type: asyncio.Task
        self._queued_commands = OrderedDict()
        self._command_queue_task = None  # type: asyncio.Task
        self._expected_responses = defaultdict(deque)
        self._sequence = 0  # type: int
        self._state = const.STATE_DISCONNECTED  # type: str
        self._auto_reconnect = True  # type: bool
        self._reconnect_delay = const.DEFAULT_RECONNECT_DELAY  # type: float
        self._reconnect_task = None  # type: asyncio.Task
        self._last_activity = datetime(1970, 1, 1)  # type: datetime
        self._last_command_time = datetime(2020, 1, 1)  # type: datetime
        self._heart_beat_interval = heart_beat  # type: Optional[float]
        self._heart_beat_task = None  # type: asyncio.Task
        self._message_interval_limit = const.MESSAGE_INTERVAL_LIMIT

    @abstractmethod
    async def _load_command_dict(self, path=None):
        """Load the commands YAML."""

    @abstractmethod
    def _get_command_lookup(self, command_dict):
        """Create a command lookup dict."""

    @abstractmethod
    async def _response_handler(self):
        """Handle messages received from the device."""

    def _heartbeat_command(self):
        command = self._command_lookup[const.ATTR_POWER].set_query()
        self.send_command(command, heartbeat=True)

    async def init(self, *, auto_reconnect: bool = True, reconnect_delay: float = -1):
        """Await the async initialization."""
        await self._load_command_dict()
        await self.connect(
            auto_reconnect=auto_reconnect, reconnect_delay=reconnect_delay
        )
        self._command_lookup = self._get_command_lookup(self._command_dict)

    async def connect(
        self, *, auto_reconnect: bool = False, reconnect_delay: float = -1
    ):
        """Connect to the AV Receiver - called by init only."""
        if self._state == const.STATE_CONNECTED:
            return
        if reconnect_delay < 0:
            reconnect_delay = self._reconnect_delay
        self._auto_reconnect = False
        await self._connect()
        self._auto_reconnect = auto_reconnect

    async def _connect(self):
        """Make Telnet connection."""
        try:
            open_future = telnetlib3.open_connection(self.host, self.port)
            self._reader, self._writer = await asyncio.wait_for(
                open_future, self.timeout
            )
        except Exception as error:
            raise error from error
        self._response_handler_task = asyncio.create_task(self._response_handler())
        self._state = const.STATE_CONNECTED
        self._command_queue_task = asyncio.create_task(self._process_command_queue())
        if self._heart_beat_interval is not None and self._heart_beat_interval > 0:
            self._heart_beat_task = asyncio.create_task(self._heart_beat())

        _LOGGER.debug("Connected to %s", self.host)
        self._avr.dispatcher.send(const.SIGNAL_TELNET_EVENT, const.EVENT_CONNECTED)

    async def disconnect(self):
        """Disconnect from the AV Receiver."""
        if self._state == const.STATE_DISCONNECTED:
            return
        if self._reconnect_task:
            self._reconnect_task.cancel()
            await self._reconnect_task
            self._reconnect_task = None
        await self._disconnect()
        self._state = const.STATE_DISCONNECTED

        _LOGGER.debug("Disconnected from %s", self.host)
        self._avr.dispatcher.send(const.SIGNAL_TELNET_EVENT, const.EVENT_DISCONNECTED)

    async def _disconnect(self):
        """Cancel response handler and pending tasks."""
        if self._heart_beat_task:
            self._heart_beat_task.cancel()
            try:
                await self._heart_beat_task
            except asyncio.CancelledError:
                pass
            self._heart_beat_task = None
        if self._response_handler_task:
            self._response_handler_task.cancel()
            try:
                await self._response_handler_task
            except asyncio.CancelledError:
                pass
            self._response_handler_task = None
        if self._command_queue_task:
            self._command_queue_task.cancel()
            try:
                await self._command_queue_task
            except asyncio.CancelledError:
                pass
            self._command_queue_task = None
        if self._writer:
            self._writer.close()
            self._writer = None
        self._reader = None
        self._sequence = 0
        self._queued_commands.clear()
        self._expected_responses.clear()

    async def _handle_connection_error(self, error: Exception = "hearbeat"):
        """Handle connection failures and schedule reconnect."""
        if self._reconnect_task:
            return
        await self._disconnect()
        if self._auto_reconnect:
            self._state = const.STATE_RECONNECTING
            self._reconnect_task = asyncio.create_task(self._reconnect())
        else:
            self._state = const.STATE_DISCONNECTED

        _LOGGER.debug("Disconnected from %s: %s", self.host, error)
        self._avr.dispatcher.send(const.SIGNAL_TELNET_EVENT, const.EVENT_DISCONNECTED)

    async def _reconnect(self):
        """Perform core reconnection logic."""
        # pylint: disable=broad-except
        while self._state != const.STATE_CONNECTED:
            try:
                await self._connect()
                self._reconnect_task = None
                return
            except Exception as err:
                # Occurs when we could not reconnect
                _LOGGER.debug("Failed to reconnect to %s: %s", self.host, err)
                await self._disconnect()
                await asyncio.sleep(self._reconnect_delay)
            except asyncio.CancelledError:
                # Occurs when reconnect is cancelled via disconnect
                return

    async def _heart_beat(self):
        """Check for activity and send a heartbeat to check for connection."""
        while self._state == const.STATE_CONNECTED:
            old_last_activity = self._last_activity
            last_activity = datetime.utcnow() - self._last_activity
            threshold = timedelta(seconds=self._heart_beat_interval)
            if last_activity > threshold:
                self._heartbeat_command()
                await asyncio.sleep(5)
                if self._last_activity <= old_last_activity:
                    await self._handle_connection_error()
            await asyncio.sleep(self._heart_beat_interval / 2)

    def send_command(self, command, heartbeat=False):
        """Execute a command."""
        if not heartbeat and self._state != const.STATE_CONNECTED:
            _LOGGER.debug(
                "Command failed %s - Not connected to device %s",
                command.message,
                self.host,
            )
            return

        _LOGGER.debug("queueing command: %s", command.message)

        self._queued_commands[command.command] = {
            "message": command.message,
            "command": command.command,
            "val": command.val,
            "attempt": 0,
        }

    async def _process_command_queue(self):
        while True:
            try:
                time_since_last_command = datetime.utcnow() - self._last_command_time
                threshold = timedelta(milliseconds=self._message_interval_limit)
                wait_time = self._message_interval_limit / 1000  # ms -> s
                if time_since_last_command > threshold:
                    next_command = None
                    try:
                        _, next_command = self._queued_commands.popitem(last=False)
                        if next_command is not None:
                            _LOGGER.debug("Popped command: %s", next_command["message"])
                            self._writer.write(next_command["message"])
                            await self._writer.drain()
                            self._last_command_time = datetime.utcnow()
                            wait_time = self._message_interval_limit / 1000 + 0.002
                            self._expected_responses[next_command["command"]].append(
                                ExpectedResponse(
                                    next_command["command"], next_command["val"]
                                )
                            )
                    except KeyError:
                        pass
                else:
                    wait_time = (
                        threshold.total_seconds()
                        - time_since_last_command.total_seconds()
                        + 0.002
                    )
                await asyncio.sleep(wait_time)
            # pylint: disable=broad-except, fixme
            except Exception as err:
                # TODO: error handling
                _LOGGER.critical(err)
                await asyncio.sleep(0.05)

    def _handle_event(self, resp: Message):
        """Handle a response event."""
        if resp.state_update == {}:
            _LOGGER.debug("No state update in message: %s", resp.message)
            return
        updated = self._avr.update_state(resp.state_update)
        expected_response_deque = self._expected_responses.get(resp.command)
        if expected_response_deque:
            try:
                expected_response = expected_response_deque.popleft()
                expected_response.set(resp)
            except IndexError:
                _LOGGER.debug("No expected response for: %s", resp.command)
        else:
            _LOGGER.debug("No expected response matched: %s", resp.command)
        if updated:
            self._avr.dispatcher.send(const.SIGNAL_STATE_UPDATE, resp.message)
        _LOGGER.debug("Event received: %s", resp.state_update)

    @property
    def state(self) -> str:
        """Get the current state of the connection."""
        return self._state


class ExpectedResponse:
    """Define an awaitable command event response."""

    def __init__(self, command: str, val: str):
        """Init a new instance of the CommandEvent."""
        self._event = asyncio.Event()
        self._command = command
        self._val = val
        self._response = None
        self._time_sent = datetime.utcnow()

    async def wait(self):
        """Wait until the event is set."""
        await self._event.wait()
        return self._response

    def set(self, message: Message):
        """Set the response."""
        self._response = message
        self._event.set()

    @property
    def command(self) -> int:
        """Get the command that represents this event."""
        return self._command
