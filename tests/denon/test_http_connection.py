"""Test getting device information via HTTP API."""
from pyavreceiver.denon import const as denon_const
from pyavreceiver.denon.http_connection import DenonHTTPApi


def test_get_renamed_and_deleted_sources():
    """Test getting dict of renamed sources."""
    with open("tests/denon/fixtures/GetRename-Delete.xml") as file:
        xml = file.read()
    rename_map = DenonHTTPApi.make_renamed_dict(xml)
    assert rename_map["STEAM"] == denon_const.SOURCE_CABLE
    assert rename_map["Test"] == denon_const.SOURCE_DVD
    assert rename_map["XBOX 360"] == denon_const.SOURCE_BLURAY
    assert not rename_map.get("Game")  # deleted source
    assert rename_map["AUX"] == denon_const.SOURCE_AUX
    assert rename_map["Media Player"] == denon_const.SOURCE_MEDIA_PLAYER
    assert rename_map["Tuner"] == denon_const.SOURCE_TUNER
    assert rename_map["HEOS Music"] == denon_const.SOURCE_NETWORK
    assert rename_map["TV Audio"] == denon_const.SOURCE_TV_AUDIO
    assert rename_map["Bluetooth"] == denon_const.SOURCE_BLUETOOTH
    assert rename_map["Phono"] == denon_const.SOURCE_PHONO


def test_read_device_info_x_series_xml():
    """Test getting model, mac, and zone count from X-series."""
    with open("tests/denon/fixtures/Deviceinfo-X1500H.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.make_device_info_dict(xml)
    assert info["model_name"] == "AVR-X1500H"
    assert info["mac_address"] == "0005CDD1F6E8"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-X8500H.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.make_device_info_dict(xml)
    assert info["model_name"] == "AVC-X8500H"
    assert info["mac_address"] == "0005CDA60D0C"
    assert info["zones"] == "3"

    with open("tests/denon/fixtures/Deviceinfo-X2000.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.make_device_info_dict(xml)
    assert info["model_name"] == "*AVR-X2000"
    assert info["mac_address"] == "0005CD3A0525"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-X1100W.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.make_device_info_dict(xml)
    assert info["model_name"] == "*AVR-X1100W"
    assert info["mac_address"] == "0005CD49AC13"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-SR5008.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.make_device_info_dict(xml)
    assert info["model_name"] == "*SR5008"
    assert info["mac_address"] == "0006781D2F2F"
    assert info["zones"] == "2"

    with open("tests/denon/fixtures/Deviceinfo-NR1604.xml") as file:
        xml = file.read()
    info = DenonHTTPApi.make_device_info_dict(xml)
    assert info["model_name"] == "*NR1604"
    assert info["mac_address"] == "0006781C2177"
    assert info["zones"] == "2"
