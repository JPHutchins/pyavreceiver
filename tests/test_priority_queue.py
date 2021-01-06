"""Tests for the PriorityQueue class."""
from typing import Union

import pytest

from pyavreceiver.command import TelnetCommand
from pyavreceiver.priority_queue import PriorityQueue


class GenericCommand(TelnetCommand):
    """Generic Telnet Command."""

    def set_val(
        self, val: Union[int, float, str] = None, qos: int = 0, sequence: int = -1
    ) -> TelnetCommand:
        return GenericCommand(
            command=self._command,
            val=val,
            qos=qos,
        )

    def set_query(self, qos=0) -> TelnetCommand:
        return self.set_val("?", 0)


def test_priority_queue():
    """Test the priority queue."""
    # pylint: disable=invalid-name
    pq = PriorityQueue()
    command = GenericCommand(command="aa")
    command_series = [
        command.set_val(1, 0),
        command.set_val(1, 2),
        command.set_val(1, 1),
        command.set_val(1, 4),
        command.set_val(1, 3),
    ]
    for command in command_series:
        pq.push(command)
        assert pq.check_ri()
        assert len(pq) == 1
        assert command.command in pq
    assert pq.popcommand().qos == 4

    command_series = [
        GenericCommand(command="a").set_val(1),
        GenericCommand(command="b").set_val(1),
        GenericCommand(command="c").set_val(1),
    ]
    for i, command in enumerate(command_series):
        pq.push(command)
        assert pq.check_ri()
        assert len(pq) == i + 1
    assert pq.get("a") == command_series[0]
    assert pq.popcommand().command == "a"
    assert pq.popcommand().command == "b"
    assert pq.popcommand().command == "c"
    assert len(pq) == 0
    assert pq.popcommand() is None
    assert "a" not in pq
    assert pq.get("a") is None

    command_series = [
        GenericCommand(command="a").set_val(1, 0),
        GenericCommand(command="b").set_val(1, 1),
        GenericCommand(command="c").set_val(1, 2),
    ]
    for i, command in enumerate(command_series):
        pq.push(command)
        assert pq.check_ri()
        assert len(pq) == i + 1
    assert pq.popcommand().command == "c"
    assert pq.popcommand().command == "b"
    assert pq.popcommand().command == "a"
    assert len(pq) == 0

    command_series = [
        GenericCommand(command="c").set_val(1, 0),
        GenericCommand(command="a").set_val(1, 0),
        GenericCommand(command="b").set_val(1, 1),
        GenericCommand(command="c").set_val(1, 2),
        GenericCommand(command="b").set_val(1, 0),
        GenericCommand(command="c").set_val(1, 2),
    ]
    for i, command in enumerate(command_series):
        pq.push(command)
        assert pq.check_ri()
    assert pq.popcommand().command == "c"
    assert pq.popcommand().command == "b"
    assert pq.popcommand().command == "a"
    assert len(pq) == 0

    command_series = [
        GenericCommand(command="a").set_val(1, 1),
        GenericCommand(command="a").set_val(2, 1),
    ]
    for i, command in enumerate(command_series):
        pq.push(command)
        assert pq.check_ri()
    assert pq.popcommand().val == 2
    assert len(pq) == 0
    with pytest.raises(Exception):
        pq.push(GenericCommand().set_val(1, 5))

    command_series = [
        GenericCommand(command="a").set_val(1, 0),
    ]
    for i, command in enumerate(command_series):
        pq.push(command)
        assert pq.check_ri()
        assert len(pq) == i + 1
    # pylint: disable=protected-access
    pq._queues[1]["a"] = GenericCommand(command="a").set_val(1, 1)
    assert pq.check_ri() is False
