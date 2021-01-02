"""Define a priority queue for managing streams of commands."""
from collections import OrderedDict
from typing import Any, Tuple

from pyavreceiver.command import Command


class PriorityQueue:
    """Implementation of a priority queue interface."""

    def __init__(self, *, qos_levels: int = 5):
        """Initialize an array of queues."""
        self._queues = [OrderedDict() for _ in range(qos_levels)]
        self._qos_levels = qos_levels
        self._size = 0

    def __contains__(self, name) -> bool:
        for queue in self._queues:
            if name in queue:
                return True
        return False

    def __len__(self) -> int:
        return self._size

    def check_ri(self):
        """Check representation invariant - debugging."""
        result = True
        all_names = set()
        for queue in self._queues:
            for name in queue.keys():
                if name in all_names:
                    print(f"RI violation: {name} found at multiple QoS.")
                    result = False
                all_names.add(name)
        return result

    def get(self, name) -> Any:
        """Get the item from queue if it exists."""
        for queue in self._queues:
            if name in queue:
                return queue[name]
        return None

    def _popitemleft(self) -> Tuple[str, Any]:
        """Pop the highest priority item from the queue."""
        qos = self._qos_levels - 1
        item = None
        # Starting from the highest QoS, try to pop item
        while qos >= 0:
            try:
                item = self._queues[qos].popitem(last=False)
                break
            except KeyError:
                qos -= 1
        # If all QoS queues are empty return None
        if item is None:
            return None
        self._size -= 1
        return item

    def popcommand(self) -> Command:
        """Pop the highest priority command from the queue."""
        item = self._popitemleft()
        if item is not None:
            return item[1]
        return None

    def push(self, command):
        """Push command to the queue overwriting conflicts."""
        if command.qos > self._qos_levels - 1:
            raise Exception

        # A new command will always have >= QoS than one reissued by QoS
        # When a command is reissued it will be previous QoS - 1

        for qos, queue in enumerate(self._queues):
            if command.command in queue:
                # Don't add duplicated command at lower QoS
                if command.qos < qos:
                    return
                # Update value of command at equal QoS (maintains priority)
                if command.qos == qos:
                    queue[command.command] = command
                    return
                # Delete matching command found at lower QoS
                del queue[command.command]
                self._size -= 1
                break
        # Add command to the queue at the specified QoS level
        self._queues[command.qos][command.command] = command
        self._size += 1
