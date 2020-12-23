"""Test the DenonReceiver class."""
from pyavreceiver import const
from pyavreceiver.denon.receiver import DenonReceiver


def test_receiver():
    """Test the receiver."""
    avr = DenonReceiver("localhost")
    assert avr.host == "localhost"
    assert avr.connection_state == const.STATE_DISCONNECTED
    assert avr.state == {}