"""Test the DenonReceiver class."""
from pyavreceiver.dispatch import Dispatcher
from pyavreceiver import const
from pyavreceiver.denon.receiver import DenonReceiver


def test_receiver_init():
    """Test the receiver initiliazation."""
    avr = DenonReceiver("localhost")
    assert avr.host == "localhost"
    assert avr.connection_state == const.STATE_DISCONNECTED
    assert avr.state == {}
    assert isinstance(avr.dispatcher, Dispatcher)
    assert avr.main is None


def test_receiver_update():
    """Test the receiver."""
    avr = DenonReceiver("")
    assert avr.state == {}
    assert avr.update_state({"power": True})
    assert avr.state["power"]
    assert not avr.update_state({"power": True})
    assert avr.state["power"]
    assert avr.update_state({"power": False})
    assert not avr.state["power"]

    assert avr.update_state({"volume": -18.5})
    assert avr.state["volume"] == -18.5
    assert avr.update_state({"volume": -15})
    assert avr.state["volume"] == -15
