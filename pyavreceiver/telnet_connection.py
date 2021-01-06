"""Define persistent connection to an AV Receiver."""
import asyncio
import logging
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from datetime import datetime, timedelta
from typing import Coroutine, Dict, Optional, Tuple

import telnetlib3

from pyavreceiver import const
from pyavreceiver.command import TelnetCommand
from pyavreceiver.priority_queue import PriorityQueue
from pyavreceiver.response import Message

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

# Monkey patch misbehaving repr until fixed
telnetlib3.client_base.BaseClient.__repr__ = lambda x: "AV Receiver"


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
        self._command_dict = {}
        self._command_lookup = {}
        self._command_timeout = const.DEFAULT_TELNET_TIMEOUT
        self._learned_commands = {}
        self.timeout = timeout  # type: int
        self._reader = None  # type: telnetlib3.TelnetReader
        self._writer = None  # type: telnetlib3.TelnetWriter
        self._response_handler_task = None  # type: asyncio.Task
        self._command_queue = PriorityQueue()
        self._command_queue_task = None  # type: asyncio.Task
        self._expected_responses = ExpectedResponseQueue()
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
    def _load_command_dict(self, path=None):
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
        self._load_command_dict()
        await self.connect(
            auto_reconnect=auto_reconnect, reconnect_delay=reconnect_delay
        )
        self._command_lookup = self._get_command_lookup(self._command_dict)
        return self.disconnect

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
        if self._expected_responses:
            self._expected_responses.cancel_tasks()
        if self._writer:
            self._writer.close()
            self._writer = None
        self._reader = None
        self._sequence = 0
        self._command_queue.clear()

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
        self._command_queue.push(command)

    def async_send_command(self, command: TelnetCommand) -> Coroutine:
        """Execute an async command and return awaitable coroutine."""
        _LOGGER.debug("queueing command: %s", command.message)
        # Give command a unique sequence id and increment
        command.set_sequence(self._sequence)
        self._sequence += 1
        status, cancel = self._command_queue.push(command)
        if status == const.QUEUE_FAILED:
            _LOGGER.debug("Command not queued.")
            return cancel.wait()
        if status == const.QUEUE_CANCEL:
            try:
                self._expected_responses[cancel].overwrite_command(command)
                return self._expected_responses[cancel].wait()
            except KeyError:
                # Can happen when a query returns multiple responses to one query
                # self._expected_responses[command] = ExpectedResponse(command, self)
                # return self._expected_responses[command].wait()
                async def blank_awaitable():
                    """Blank awaitable."""
                    return None

                return blank_awaitable()
        if status == const.QUEUE_NO_CANCEL:
            self._expected_responses[command] = ExpectedResponse(command, self)
            return self._expected_responses[command].wait()

    async def _process_command_queue(self):
        while True:
            wait_time = 0.02
            if self._command_queue.is_empty:
                await asyncio.sleep(wait_time)
                continue
            try:
                time_since_last_command = datetime.utcnow() - self._last_command_time
                threshold = timedelta(milliseconds=self._message_interval_limit)
                wait_time = self._message_interval_limit / 1000  # ms -> s
                if (time_since_last_command > threshold) and (
                    command := self._command_queue.popcommand()
                ):
                    _LOGGER.debug("Popped command: %s", command.message)
                    # Send command message
                    self._writer.write(command.message)
                    await self._writer.drain()
                    # Record time sent and update the expected response
                    self._last_command_time = datetime.utcnow()
                    try:
                        self._expected_responses[command].set_sent(
                            self._last_command_time
                        )
                    except KeyError:
                        # QoS 0 command
                        pass
                    wait_time = self._message_interval_limit / 1000 + 0.002
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
                _LOGGER.critical(Exception(err))
                await asyncio.sleep(0.05)

    def _handle_event(self, resp: Message):
        """Handle a response event."""
        if resp.state_update == {}:
            _LOGGER.debug("No state update in message: %s", resp.message)
        if self._avr.update_state(resp.state_update):
            self._avr.dispatcher.send(const.SIGNAL_STATE_UPDATE, resp.message)
            _LOGGER.debug("Event received: %s", resp.state_update)
        if expected_response_items := self._expected_responses.popmatch(resp.command):
            _, expected_response = expected_response_items
            expected_response.set(resp)
        else:
            _LOGGER.debug("No expected response matched: %s", resp.command)

    @property
    def commands(self) -> dict:
        """Get the dict of commands."""
        return self._command_lookup

    @property
    def state(self) -> str:
        """Get the current state of the connection."""
        return self._state


class ExpectedResponse:
    """Define an awaitable command event response."""

    __slots__ = (
        "_attempts",
        "_event",
        "_command",
        "_response",
        "_time_sent",
        "_qos_task",
        "_expire_task",
        "_command_timeout",
        "_connection",
    )

    def __init__(self, command: TelnetCommand, connection: TelnetConnection):
        """Init a new instance of the CommandEvent."""
        self._attempts = 0
        self._event = asyncio.Event()
        self._command = command
        self._connection = connection
        self._command_timeout = const.DEFAULT_TELNET_TIMEOUT
        self._response = None
        self._time_sent = None
        self._qos_task = None  # type: asyncio.Task
        self._expire_task = None  # type: asyncio.Task

    async def cancel_tasks(self) -> None:
        """Cancel the QoS and/or expire tasks."""
        if self._qos_task:
            self._qos_task.cancel()
            try:
                await self._qos_task
            except asyncio.CancelledError:
                pass
            self._qos_task = None
        if self._expire_task:
            self._expire_task.cancel()
            try:
                await self._expire_task
            except asyncio.CancelledError:
                pass
            self._expire_task = None

    async def _expire(self):
        """Wait until timeout has expired and remove expected response."""
        # pylint: disable=protected-access
        await asyncio.sleep(const.DEFAULT_COMMAND_EXPIRATION)
        self.set(None)

    async def wait(self) -> str:
        """Wait until the event is set."""
        # pylint: disable=protected-access
        await self._event.wait()
        await self.cancel_tasks()  # cancel any remaining QoS or expire tasks
        await self._connection._expected_responses.cancel_expected_response(
            self._command
        )
        return self._response

    def overwrite_command(self, command) -> None:
        """Overwrite the stale command with newer one."""
        self._command = command

    def set(self, message: Message) -> None:
        """Set the response."""
        self._response = message
        self._event.set()

    def set_sent(self, time=datetime.utcnow()) -> None:
        """Set the time that the command was sent."""
        if not self._expire_task:
            self._expire_task = asyncio.create_task(self._expire())
        if self._attempts >= 1:
            query = self._command.set_query(qos=0)
            self._connection.send_command(query)
        if self._attempts == 0:
            self._command.raise_qos()  # prioritize resends
        self._attempts += 1
        self._time_sent = time
        self._qos_task = asyncio.create_task(self._resend_command())

    async def _resend_command(self) -> None:
        await asyncio.sleep(self._command_timeout)
        if self._attempts <= self._command.retries:
            # pylint: disable=protected-access
            status, cancel = self._connection._command_queue.push(self._command)
            if status == const.QUEUE_FAILED:
                # A resend at higher qos was already sent
                # This shouldn't happen
                self._connection._expected_responses[
                    self._command
                ] = self._connection._expected_responses[cancel]
            if status == const.QUEUE_CANCEL:
                # The resend will overwrite a queued command, set that commands response to
                # trigger on resolution of this command
                self._connection._expected_responses[cancel] = self
                _LOGGER.debug("QoS requeueing command: %s", self._command.message)
            if status == const.QUEUE_NO_CANCEL:
                # The resend is treated as if it is the original command
                _LOGGER.debug("QoS requeueing command: %s", self._command.message)
        else:
            _LOGGER.debug(
                "Command %s failed after %s attempts",
                self._command.message,
                self._attempts,
            )
            self.set(None)

    @property
    def command(self) -> int:
        """Get the command that represents this event."""
        return self._command.command


class ExpectedResponseQueue:
    """Define a queue of ExpectedResponse."""

    def __init__(self):
        """Init the data structure."""
        self._queue = defaultdict(
            OrderedDict
        )  # type: Dict[OrderedDict[TelnetCommand, ExpectedResponse]]

    def __getitem__(self, command: TelnetCommand) -> ExpectedResponse:
        """Get item shortcut through both dicts."""
        return self._queue[command.command][command]

    def __setitem__(self, command: TelnetCommand, expected_response: ExpectedResponse):
        """Set item shortcut through both dicts."""
        self._queue[command.command][command] = expected_response

    def get(self, command_group) -> Optional[OrderedDict]:
        """Get the (command, response) entries for command_group, if any."""
        return self._queue.get(command_group)

    def popmatch(
        self, command_group
    ) -> Optional[Tuple[TelnetCommand, ExpectedResponse]]:
        """Pop the oldest matching expected response entry, if any."""
        if match := self._queue.get(command_group):
            try:
                command, expected_response = match.popitem(last=False)
            except KeyError:
                return None
            return (command, expected_response)

    async def cancel_expected_response(self, command) -> None:
        """Cancel and delete the expected response for a specific command."""
        try:
            expected_response = self._queue[command.command][command]
            expected_response.set(None)
            await expected_response.cancel_tasks()
            del self._queue[command.command][command]
            try:
                self._queue[command.command][command]
            except KeyError:
                return
            _LOGGER.warning("Expected response: %s, was not deleted", expected_response)
            raise AttributeError
        except KeyError:
            return

    def cancel_tasks(self) -> None:
        """Cancel all tasks in the queue and clear dicts."""
        for group in self._queue.values():
            for expected_response in group.values():
                expected_response.set(None)
        self._queue = defaultdict(OrderedDict)
