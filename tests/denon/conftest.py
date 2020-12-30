"""Configure the Denon/Marantz tests."""
from importlib import resources

import pytest
import yaml

from pyavreceiver.denon.response import DenonMessage


@pytest.fixture(name="message_none")
def denon_message_none():
    """Create an empty DenonMessage."""
    with resources.open_text("pyavreceiver.denon", "commands.yaml") as file:
        command_dict = yaml.safe_load(file.read())
        command_dict.update(fake_entries)
    return DenonMessage(None, command_dict)


@pytest.fixture(name="command_dict")
def denon_command_dict():
    """Create the command dict."""
    with resources.open_text("pyavreceiver.denon", "commands.yaml") as file:
        command_dict = yaml.safe_load(file.read())
        command_dict.update(fake_entries)
    return command_dict


fake_entries = {
    "FAKEFORTEST": {},
    "FAKE": {"FOR TESTS": {}},
    "FAKEFO": {"R T E STS": {}},
    "FAKEN": {"^params": True, "OR": "TEST"},
}
