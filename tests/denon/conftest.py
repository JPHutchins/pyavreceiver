"""Configure the Denon/Marantz tests."""
import pytest
import yaml

from pyavreceiver.denon.response import DenonMessage


@pytest.fixture(name="message_none")
def denon_message_none():
    """Create an empty DenonMessage."""
    with open("tests/denon/commands.yaml") as file:
        command_dict = yaml.safe_load(file.read())
    return DenonMessage(None, command_dict)


@pytest.fixture(name="command_dict")
def denon_command_dict():
    """Create the command dict."""
    with open("tests/denon/commands.yaml") as file:
        command_dict = yaml.safe_load(file.read())
    return command_dict
