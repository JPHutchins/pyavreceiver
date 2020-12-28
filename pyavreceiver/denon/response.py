"""Implement a Denon telnet message."""
import logging

from pyavreceiver import const
from pyavreceiver.denon.error import DenonCannotParse
from pyavreceiver.denon.parse import parse
from pyavreceiver.response import Message

_LOGGER = logging.getLogger(__name__)


class DenonMessage(Message):
    """Define a Denon telnet message representation."""

    def __init__(self, message: str = None, command_dict: dict = None):
        """Init a new Denon message."""
        self._message = None  # type: str
        self._raw_val = None  # type: str
        self._cmd = None  # type: str
        self._prm = None  # type: str
        self._val = None
        self._name = None  # type: str
        self._command_dict = command_dict or {}
        self._new_command = None

        self._state_update = self._parse(message) if message else {}

    def __str__(self):
        """Get user readable message."""
        return self._message

    def __repr__(self):
        """Get readable message."""
        return self._message

    def _parse(self, message: str) -> dict:
        """Parse message, assign attributes, return a state update dict."""
        self._message = message
        self._cmd, self._prm, self._raw_val = self.separate(message)
        try:
            self._val = self.parse_value(self._cmd, self._prm, self._raw_val)
        except DenonCannotParse:
            return {}
        return self._make_state_update()

    def _make_state_update(self) -> dict:
        """Return the state update dict."""
        entry = self._command_dict.get(self._cmd) or self._cmd
        key = entry
        val = self._val if self._val is not None else self._raw_val
        try:
            if const.COMMAND_NAMES in entry:
                try:
                    _ = int(val)
                    val_type = "number"
                except ValueError:
                    val_type = val
                key = entry[const.COMMAND_NAMES].get(val_type)
                if key is None:
                    key = entry[const.COMMAND_NAMES]["other"]

            if const.COMMAND_NAME in entry and const.COMMAND_PARAMS in entry:
                cmd_name = entry[const.COMMAND_NAME]
                key = f"{cmd_name}_{self._prm.lower()}" if self._prm else cmd_name
                entry = entry.get(self._prm)

            try:
                key = (
                    entry.get(const.COMMAND_NAME)
                    or key.get(const.COMMAND_NAME)  # key may be string
                    or f"{self._cmd}{'_' + self._prm if self._prm else ''}"
                )
            except AttributeError:
                pass

            _ = entry.get(self._raw_val)
            val = _ if _ is not None else self._val or val
            entry = entry.get(self._prm)
            val = entry.get(self._raw_val) or self._val or val

            key = (
                self._command_dict[self._cmd][self._prm].get(const.COMMAND_NAME) or key
            )

        except (KeyError, AttributeError):
            pass
        self._name = key
        return {key: val}

    def separate(self, message) -> tuple:
        """Separate command category, parameter, and value."""
        return DenonMessage._search(self._command_dict, 0, message, (), self=self)

    @staticmethod
    def _search(lvl: dict, depth: int, rem: str, cur: tuple, self=None) -> tuple:
        """Search dict for best match."""
        # pylint: disable=protected-access
        if rem in lvl:
            if depth == 1:
                return (*cur, None, rem)
        elif const.COMMAND_RANGE in lvl and rem.isnumeric():
            return (*cur, None, rem)
        elif const.COMMAND_PARAMS in lvl:
            prm = rem
            val = ""
            # Check for match at each partition
            for _ in range(len(prm)):
                if prm in lvl:
                    return (*cur, prm.strip(), val.strip())
                val = prm[-1:] + val
                prm = prm[:-1]
            # No match found: return new entry, assume val after last space
            words = rem.split(" ")
            if len(words) < 2:
                _LOGGER.info(
                    "Added new event with empty value: %s, %s, None", *cur, rem
                )
                if self:
                    self._new_command = {"cmd": cur[0], "prm": rem, "val": None}
                return (*cur, words[0], None)
            prm = " ".join(words[:-1]).strip()
            val = words[-1].strip()
            _LOGGER.info("Added new event: %s, %s, %s", *cur, prm, val)
            if self:
                self._new_command = {"cmd": cur[0], "prm": prm, "val": val}
            return (*cur, prm, val)
        elif depth == 1:
            self._new_command = {"cmd": cur[0], "prm": None, "val": rem.strip()}
            return (*cur, None, rem.strip())
        # Search for matches at every prefix/postfix
        for i in range(-1, -len(rem), -1):
            prefix = rem[:i]
            if prefix not in lvl:
                continue
            return DenonMessage._search(
                lvl[prefix], depth + 1, rem[i:], (*cur, prefix), self=self
            )
        # No match found: return new entry, assume val after last space
        words = rem.split(" ")
        if len(words) < 2:
            _LOGGER.error("Unparsable event: %s", rem)
            return (rem, None, None)
        cmd = " ".join(words[:-1]).strip()
        val = words[-1].strip()
        _LOGGER.info("Parsed new cmd event: %s, None, %s", cmd, val)
        if self:
            self._new_command = {"cmd": cmd, "prm": None, "val": val}
        return (cmd, None, val)

    def parse_value(self, cmd: str, prm: str, val: str):
        """Parse a value from val."""
        if not isinstance(self._command_dict.get(cmd), dict):
            return val
        entry = self._command_dict[cmd].get(prm) or self._command_dict[cmd]
        if const.COMMAND_FUNCTION in entry:
            function_name = entry[const.COMMAND_FUNCTION]
        elif const.COMMAND_FUNCTION in self._command_dict[cmd]:
            function_name = self._command_dict[cmd][const.COMMAND_FUNCTION]
        else:
            return val
        if function_name == const.FUNCTION_VOLUME:
            parser = parse[const.FUNCTION_NUM_TO_DB]
            return parser(
                num=val,
                zero=entry.get(const.COMMAND_ZERO),
                valid_strings=entry.get(const.COMMAND_STRINGS),
            )
        raise Exception

    @property
    def parsed(self) -> tuple:
        """Return the message parsed into (command, param, value)."""
        return (self._cmd, self._prm, self._val)

    @property
    def message(self) -> str:
        return self._message

    @property
    def raw_value(self) -> str:
        return self._raw_val

    @property
    def state_update(self) -> dict:
        return self._state_update

    @property
    def command(self) -> str:
        return self._cmd + (self._prm or "")

    @property
    def new_command(self) -> dict:
        return self._new_command

    @property
    def name(self) -> str:
        return self._name
