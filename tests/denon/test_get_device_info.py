"""Test getting device information via HTTP API."""
from pyavreceiver.denon.http_connection import DenonHTTPApi


def test_read_device_info_x_series_xml():
    """Test getting model, mac, and zone count from X-series."""
    with open("tests/denon/fixtures/Deviceinfo-X1500H.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.get_info(xml)
    assert info["model_name"] == "AVR-X1500H"
    assert info["mac_address"] == "0005CDD1F6E8"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-X8500H.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.get_info(xml)
    assert info["model_name"] == "AVC-X8500H"
    assert info["mac_address"] == "0005CDA60D0C"
    assert info["zones"] == "3"

    with open("tests/denon/fixtures/Deviceinfo-X2000.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.get_info(xml)
    assert info["model_name"] == "*AVR-X2000"
    assert info["mac_address"] == "0005CD3A0525"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-X1100W.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.get_info(xml)
    assert info["model_name"] == "*AVR-X1100W"
    assert info["mac_address"] == "0005CD49AC13"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-SR5008.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.get_info(xml)
    assert info["model_name"] == "*SR5008"
    assert info["mac_address"] == "0006781D2F2F"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-NR1604.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.get_info(xml)
    assert info["model_name"] == "*NR1604"
    assert info["mac_address"] == "0006781C2177"
    assert info["zones"] == "2"
