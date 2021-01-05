"""Test responses from Denon/Marantz."""
from pyavreceiver.denon.response import DenonMessage


def test_separate(message_none):
    """Test separation of messages."""
    assert message_none.separate("PWON") == ("PW", None, "ON")
    assert message_none.separate("PWSTANDBY") == ("PW", None, "STANDBY")

    assert message_none.separate("MVMAX 80") == ("MV", "MAX", "80")

    assert message_none.separate("CVFL 60 ") == ("CV", "FL", "60")
    assert message_none.separate("CVFL60") == ("CV", "FL", "60")
    assert message_none.separate("CV FHL 44") == ("CV", "FHL", "44")
    assert message_none.separate("CVNEW SPEC 55") == ("CV", "NEW SPEC", "55")
    assert message_none.separate("CVUNKNOWNCOMMAND55") == (
        "CV",
        "UNKNOWNCOMMAND55",
        None,
    )

    assert message_none.separate("MUON") == ("MU", None, "ON")

    assert message_none.separate("SIPHONO") == ("SI", None, "PHONO")
    assert message_none.separate("SI PHONO ") == ("SI", None, "PHONO")
    assert message_none.separate("SIUSB DIRECT") == ("SI", None, "USB DIRECT")
    assert message_none.separate("SINEW SOURCE VARIETY") == (
        "SI",
        None,
        "NEW SOURCE VARIETY",
    )

    assert message_none.separate("SLPOFF") == ("SLP", None, "OFF")
    assert message_none.separate("SLP OFF") == ("SLP", None, "OFF")

    assert message_none.separate("MSDOLBY D+ +PL2X C") == (
        "MS",
        None,
        "DOLBY D+ +PL2X C",
    )
    assert message_none.separate("MSYET ANOTHER POINTLESS DSP") == (
        "MS",
        None,
        "YET ANOTHER POINTLESS DSP",
    )

    assert message_none.separate("PSDELAY 000") == ("PS", "DELAY", "000")
    assert message_none.separate("PSTONE CTRL ON") == ("PS", "TONE CTRL", "ON")
    assert message_none.separate("PSTONE CTRLOFF") == ("PS", "TONE CTRL", "OFF")
    assert message_none.separate("PSSB MTRX ON") == ("PS", "SB", "MTRX ON")
    assert message_none.separate("PSSB ON") == ("PS", "SB", "ON")
    assert message_none.separate("PSMULTEQ BYP.LR") == ("PS", "MULTEQ", "BYP.LR")
    assert message_none.separate("PSDCO OFF") == ("PS", "DCO", "OFF")
    assert message_none.separate("PSLFE -8") == ("PS", "LFE", "-8")
    assert message_none.separate("PSNEWPARAM OK") == ("PS", "NEWPARAM", "OK")
    assert message_none.separate("PSUNKNOWNCOMMAND55") == (
        "PS",
        "UNKNOWNCOMMAND55",
        None,
    )

    assert message_none.separate("MV60") == ("MV", None, "60")
    assert message_none.separate("MV595") == ("MV", None, "595")

    assert message_none.separate("Z2PSBAS 51") == ("Z2PS", "BAS", "51")
    assert message_none.separate("Z260") == ("Z2", None, "60")
    assert message_none.separate("Z2ON") == ("Z2", None, "ON")
    assert message_none.separate("Z2PHONO") == ("Z2", None, "PHONO")

    assert message_none.separate("Z3PSBAS 51") == ("Z3PS", "BAS", "51")
    assert message_none.separate("Z360") == ("Z3", None, "60")
    assert message_none.separate("Z3ON") == ("Z3", None, "ON")
    assert message_none.separate("Z3PHONO") == ("Z3", None, "PHONO")

    assert message_none.separate("NEWCMD 50") == ("NEWCMD", None, "50")
    assert message_none.separate("NEWCMD WITH PARAMS 50") == (
        "NEWCMD WITH PARAMS",
        None,
        "50",
    )
    assert message_none.separate("UNPARSABLE") == ("UNPARSABLE", None, None)
    assert message_none.separate("FAKEFOR TESTS") == ("FAKEFO", None, "R TESTS")
    assert message_none.separate("FAKENORTEST") == ("FAKEN", "OR", "TEST")


def test_format_db(message_none):
    """Test format to decibel."""
    assert message_none.parse_value("MV", None, "60") == -20
    assert message_none.parse_value("MV", None, "595") == -20.5
    assert message_none.parse_value("MV", None, "80") == 0
    assert message_none.parse_value("MV", None, "805") == 0.5
    assert message_none.parse_value("MV", None, "00") == -80

    assert message_none.parse_value("MV", "MAX", "80") == 0

    assert message_none.parse_value("CV", "FL", "50") == 0
    assert message_none.parse_value("CV", "SL", "39") == -11
    assert message_none.parse_value("CV", "FHL", "545") == 4.5

    assert message_none.parse_value("SSLEV", "FL", "50") == 0

    assert message_none.parse_value("PS", "BAS", "50") == 0
    assert message_none.parse_value("PS", "BAS", "39") == -11
    assert message_none.parse_value("PS", "TRE", "545") == 4.5

    assert message_none.parse_value("PS", "LFE", "-6") == -6

    assert message_none.parse_value("Z2", None, "60") == -20
    assert message_none.parse_value("Z2", None, "595") == -20.5
    assert message_none.parse_value("Z2", None, "80") == 0
    assert message_none.parse_value("Z2", None, "805") == 0.5
    assert message_none.parse_value("Z2", None, "00") == -80


def test_attribute_assignment(command_dict):
    """Test assignment of attr."""
    msg = DenonMessage("PWON", command_dict)
    assert msg.parsed == ("PW", None, "ON")
    assert str(msg) == "PWON"
    assert repr(msg) == "PWON"
    assert msg.command == "PW"

    msg = DenonMessage("MV75", command_dict)
    assert msg.parsed == ("MV", None, -5)
    assert msg.message == "MV75"
    assert msg.raw_value == "75"

    msg = DenonMessage("MVMAX 80", command_dict)
    assert msg.parsed == ("MV", "MAX", 0)
    assert msg.message == "MVMAX 80"
    assert msg.raw_value == "80"

    msg = DenonMessage("CVFL 51", command_dict)
    assert msg.parsed == ("CV", "FL", 1)
    assert msg.message == "CVFL 51"
    assert msg.raw_value == "51"
    assert msg.command == "CVFL"

    msg = DenonMessage("MSDOLBY D+ +PL2X C", command_dict)
    assert msg.parsed == ("MS", None, "DOLBY D+ +PL2X C")

    msg = DenonMessage("PSDYNVOL LOW", command_dict)
    assert msg.parsed == ("PS", "DYNVOL", "LOW")
    assert msg.message == "PSDYNVOL LOW"
    assert msg.raw_value == "LOW"
    assert msg.command == "PSDYNVOL"

    msg = DenonMessage("PSDELAY 000", command_dict)
    assert msg.parsed == ("PS", "DELAY", "000")
    assert msg.message == "PSDELAY 000"
    assert msg.raw_value == "000"
    assert msg.command == "PSDELAY"


def test_state_update_dict(command_dict):
    """Test create the update dict."""
    assert DenonMessage("PWON", command_dict).state_update == {"power": True}
    assert DenonMessage("MVMAX 80", command_dict).state_update == {"max_volume": 0}
    assert DenonMessage("PWSTANDBY", command_dict).state_update == {"power": False}
    assert DenonMessage("MV75", command_dict).state_update == {"volume": -5}
    assert DenonMessage("MV56", command_dict).state_update == {"volume": -24}
    assert DenonMessage("CVFL 51", command_dict).state_update == {"channel_level_fl": 1}
    assert DenonMessage("SSLEVFL 50", command_dict).state_update == {
        "channel_level_fl": 0
    }
    assert DenonMessage("PSNEWPARAM LOW", command_dict).state_update == {
        "PS_NEWPARAM": "LOW"
    }
    assert DenonMessage("MSDOLBY D+ +PL2X C", command_dict).state_update == {
        "sound_mode": "DOLBY D+ +PL2X C"
    }
    assert DenonMessage("PSBAS 39", command_dict).state_update == {"bass": -11}
    assert DenonMessage("MUON", command_dict).state_update == {"mute": True}
    assert DenonMessage("SIPHONO", command_dict).state_update == {"source": "PHONO"}
    assert DenonMessage("SIBD", command_dict).state_update == {"source": "BD"}
    assert DenonMessage("SINEW SOURCE TYPE", command_dict).state_update == {
        "source": "NEW SOURCE TYPE"
    }
    assert DenonMessage("DCAUTO", command_dict).state_update == {
        "digital_signal_mode": "AUTO"
    }
    assert DenonMessage("PSTONE CTRL ON", command_dict).state_update == {
        "tone_control": True
    }
    assert DenonMessage("PSSBMTRX ON", command_dict).state_update == {
        "surround_back": "MTRX ON"
    }
    assert DenonMessage("PSDYNVOL MED", command_dict).state_update == {
        "dsp_dynamic_range_control": "medium"
    }
    assert DenonMessage("NEWPARAM ANYVALUE", command_dict).state_update == {
        "NEWPARAM": "ANYVALUE"
    }
    assert DenonMessage("PSNEWPARAM ANYVALUE", command_dict).state_update == {
        "PS_NEWPARAM": "ANYVALUE"
    }
    assert DenonMessage("PSNEWPARAM", command_dict).state_update == {
        "PS_NEWPARAM": None
    }


def test_bad_value_handling(command_dict):
    """Test error handling for values that don't conform to spec."""
    assert DenonMessage("MVSTRING", command_dict).state_update == {
        "volume_string": None
    }
    assert DenonMessage("MV1000", command_dict).state_update == {}


def test_multiple_types(command_dict):
    """Test handling multiple types of value."""
    assert DenonMessage("PSDIL OFF", command_dict).state_update == {
        "dialog_level": False
    }
    assert DenonMessage("PSDIL ON", command_dict).state_update == {"dialog_level": True}
    assert DenonMessage("PSDIL 55", command_dict).state_update == {"dialog_level": 5}
    assert DenonMessage("PSDIL 45", command_dict).state_update == {"dialog_level": -5}


def test_unnamed_param(command_dict):
    """Test an unnamed parsed parameter."""
    assert DenonMessage("PSDELAY 000", command_dict).state_update == {"PS_DELAY": "000"}


def test_zones(command_dict):
    """Test parsing zone commands."""
    assert DenonMessage("ZMON", command_dict).state_update == {"zone1_power": True}
    assert DenonMessage("ZMOFF", command_dict).state_update == {"zone1_power": False}

    assert DenonMessage("Z2PSBAS 51", command_dict).state_update == {"zone2_bass": 1}
    assert DenonMessage("Z3PSTRE 445", command_dict).state_update == {
        "zone3_treble": -5.5
    }

    assert DenonMessage("Z260", command_dict).state_update == {"zone2_volume": -20}
    assert DenonMessage("Z2ON", command_dict).state_update == {"zone2_power": True}
    assert DenonMessage("Z2PHONO", command_dict).state_update == {
        "zone2_source": "PHONO"
    }
    assert DenonMessage("Z2SOURCE", command_dict).state_update == {
        "zone2_source": "SOURCE"
    }

    assert DenonMessage("Z360", command_dict).state_update == {"zone3_volume": -20}
    assert DenonMessage("Z3OFF", command_dict).state_update == {"zone3_power": False}
    assert DenonMessage("Z3SOURCE", command_dict).state_update == {
        "zone3_source": "SOURCE"
    }


def test_sequence(command_dict):
    """Test a long sequence."""
    seq = [
        "PW?"
        "PWON"
        "MV56"
        "MVMAX 80"
        "MUOFF"
        "SITV"
        "SVOFF"
        "PSDYNVOL OFF"
        "PWON"
        "PWON"
        "MV56"
        "MVMAX 80"
    ]
    for command in seq:
        DenonMessage(command, command_dict)

    invalid_seq = [
        "90f9jf3^F*)UF(U(*#fjliuF(#)U(F@ujniljf(@#)&%T^GHkjbJBVKjY*(Y#*(@&5-00193ljl",
        "",
        " ",
        " b b b   ",
        ".:':>,",
        "578934",
        "None",
        "\r",
        "MV                                                   ",
        "                 MV",
    ]
    for command in invalid_seq:
        DenonMessage(command, command_dict)


def test_learning_commands(command_dict):
    """Test saving learned commands."""
    assert DenonMessage("PWON", command_dict).new_command is None
    assert DenonMessage("PWSCREENSAVER", command_dict).new_command == {
        "cmd": "PW",
        "prm": None,
        "val": "SCREENSAVER",
    }
    assert DenonMessage("PSNEW", command_dict).new_command == {
        "cmd": "PS",
        "prm": "NEW",
        "val": None,
    }

    # The parser matches param to "EFF" and then sees "ECT" as value
    # - this is not ideal behavior - the parser should know that "ECT"
    #   as an argument should be preceded by a space
    assert DenonMessage("PSEFFECT", command_dict).parsed == ("PS", "EFF", "ECT")
    assert DenonMessage("PSEFF ECT", command_dict).parsed == ("PS", "EFF", "ECT")

    assert DenonMessage("CVATMOS RIGHT 52", command_dict).new_command == {
        "cmd": "CV",
        "prm": "ATMOS RIGHT",
        "val": "52",
    }
    assert DenonMessage("NEWCMD MEDIUM", command_dict).new_command == {
        "cmd": "NEWCMD",
        "prm": None,
        "val": "MEDIUM",
    }
    assert DenonMessage("UNPARSABLE", command_dict).new_command is None
