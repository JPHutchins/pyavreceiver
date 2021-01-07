"""Test getting device information via HTTP API."""
from pyavreceiver.denon import const as denon_const
from pyavreceiver.denon.http_api import DenonHTTPApi


def test_get_renamed_and_deleted_sources():
    """Test getting dict of renamed sources."""
    # AppCommand
    with open("tests/denon/fixtures/GetRename-Delete-X1500H.xml") as file:
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

    with open("tests/denon/fixtures/GetRename-Delete-NR1604.xml") as file:
        xml = file.read()
    rename_map = DenonHTTPApi.make_renamed_dict(xml)
    assert rename_map == {
        "TUNER": "TUNER",
        "CD": "CD",
        "M-XPort": "M-XPORT",
        "NETWORK": "NET",
        "DVD": "DVD",
        "Blu-ray": "BD",
        "TV AUDIO": "TV",
        "CBL/SAT": "SAT/CBL",  # would like confirmation
        "GAME": "GAME",
        "AUX1": "AUX1",
        "AUX2": "AUX2",
        "MEDIA PLAYER": "MPLAY",
        "iPod/USB": "USB/IPOD",
    }

    # MainZoneXml
    with open("tests/denon/fixtures/MainZoneXml-1912.xml") as file:
        xml = file.read()
    rename_map = DenonHTTPApi.make_renamed_dict_legacy(xml)
    assert rename_map == {
        "TUNER": "TUNER",
        "NET/USB": "NET/USB",
        "Chrome": "DVD",
        "Kodi": "BD",
        "Chrome A": "DOCK",
    }
    with open("tests/denon/fixtures/MainZoneXml-3311CI.xml") as file:
        xml = file.read()
    rename_map = DenonHTTPApi.make_renamed_dict_legacy(xml)
    assert rename_map == {
        "PHONO": "PHONO",
        "SqzBox": "CD",
        "SACD": "DVD",
        "BluRay": "BD",
        "SAT/CBL": "SAT/CBL",
        "HDMI5": "GAME",
        "GAME": "DVR",
        "V.AUX": "V.AUX",
    }

    # MainZoneXmlStatus - doesn't specify deleted sources
    with open("tests/denon/fixtures/MainZoneXmlStatus-1912.xml") as file:
        xml = file.read()
    rename_map = DenonHTTPApi.make_renamed_dict_legacy(xml)
    assert rename_map == {
        "TUNER": "TUNER",
        "CD": "CD",
        "NET/USB": "NET/USB",
        "Chrome": "DVD",
        "Kodi": "BD",
        "TV": "TV",
        "SAT": "SAT/CBL",
        "Chrome A": "DOCK",
        "GAME2": "GAME2",
        "GAME1": "GAME",
        "V.AUX": "V.AUX",
    }


def test_read_device_info_x_series_xml():
    """Test getting model, mac, and zone count from X-series."""
    with open("tests/denon/fixtures/Deviceinfo-X1500H.xml") as file:
        xml = file.read()
    api = DenonHTTPApi("")
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "AVR-X1500H"
    assert api.device_info["mac_address"] == "0005CDD1F6E8"
    assert api.device_info["zones"] == 2

    with open("tests/denon/fixtures/Deviceinfo-X8500H.xml") as file:
        xml = file.read()
    api = DenonHTTPApi("")
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "AVC-X8500H"
    assert api.device_info["mac_address"] == "0005CDA60D0C"
    assert api.device_info["zones"] == 3

    with open("tests/denon/fixtures/Deviceinfo-X2000.xml") as file:
        xml = file.read()
    api = DenonHTTPApi("")
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "*AVR-X2000"
    assert api.device_info["mac_address"] == "0005CD3A0525"
    assert api.device_info["zones"] == 2

    with open("tests/denon/fixtures/Deviceinfo-X1100W.xml") as file:
        xml = file.read()
    api = DenonHTTPApi("")
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "*AVR-X1100W"
    assert api.device_info["mac_address"] == "0005CD49AC13"
    assert api.device_info["zones"] == 2

    with open("tests/denon/fixtures/Deviceinfo-SR5008.xml") as file:
        xml = file.read()
    api = DenonHTTPApi("")
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "*SR5008"
    assert api.device_info["mac_address"] == "0006781D2F2F"
    assert api.device_info["zones"] == 2

    with open("tests/denon/fixtures/Deviceinfo-NR1604.xml") as file:
        xml = file.read()
    api = DenonHTTPApi("")
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "*NR1604"
    assert api.device_info["mac_address"] == "0006781C2177"
    assert api.device_info["zones"] == 2

    with open("tests/denon/fixtures/upnp-X1500H.xml") as file:
        xml = file.read()
    api = DenonHTTPApi("")
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "Denon AVR-X1500H"
    assert api.device_info["mac_address"] is None
    assert api.device_info["serial_number"] == "AYW27181117704"
    assert api.device_info["zones"] == 1
    assert api.device_info["manufacturer"] == "Denon"
    assert api.device_info["friendly_name"] == "TV Speakers"

    # Test parsing the info then upnp, as in the get_device_info function
    api = DenonHTTPApi("")
    with open("tests/denon/fixtures/Deviceinfo-X1500H.xml") as file:
        xml = file.read()
    api.make_device_info_dict(xml)
    with open("tests/denon/fixtures/upnp-X1500H.xml") as file:
        xml = file.read()
    api.make_device_info_dict(xml)
    assert api.device_info["model_name"] == "AVR-X1500H"
    assert api.device_info["mac_address"] == "0005CDD1F6E8"
    assert api.device_info["serial_number"] == "AYW27181117704"
    assert api.device_info["zones"] == 2
    assert api.device_info["manufacturer"] == "Denon"
    assert api.device_info["friendly_name"] == "TV Speakers"
