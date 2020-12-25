"""Tests for parsing Denon/Marantz messages."""
import pytest

from pyavreceiver import const
from pyavreceiver.denon.commands import get_command_lookup
from pyavreceiver.denon.error import DenonCannotParse
from pyavreceiver.denon.parse import parse
from pyavreceiver.error import AVReceiverInvalidArgumentError


def test_parse():
    """Test number parsing."""
    num_to_db = parse.num_to_db
    db_to_num = parse.db_to_num

    assert db_to_num(0, 0) == "0"
    assert db_to_num(10.5, 0) == "105"
    assert db_to_num(10.749, 0) == "105"
    assert db_to_num(9.99, 0) == "10"
    assert db_to_num(10.75, 0) == "11"

    with pytest.raises(DenonCannotParse):
        _ = num_to_db("3859")

    assert num_to_db("0", 0) == 0
    assert num_to_db("80", 80) == 0
    assert num_to_db("805", 80) == 0.5
    assert num_to_db("0", 80) == -80
    assert num_to_db("005", 80) == -79.5
    assert num_to_db("60", 50) == 10
    assert num_to_db("555", 50) == 5.5
    assert num_to_db("495", 50) == -0.5
    assert num_to_db("-5", 0) == -5

    def num_db_num(arg, zero, str_len=0):
        return db_to_num(num_to_db(arg, zero), zero, str_len) == arg

    assert num_db_num("80", 80)
    assert num_db_num("805", 80)
    assert num_db_num("0", 80)
    assert num_db_num("005", 80, str_len=3)
    assert num_db_num("60", 50)
    assert num_db_num("555", 50)
    assert num_db_num("495", 50)

    def db_num_db(arg, zero, str_len=0):
        return (
            num_to_db(
                db_to_num(arg, zero, str_len),
                zero,
            )
            == arg
        )

    assert db_num_db(0, 80)
    assert db_num_db(0.5, 80)
    assert db_num_db(-80, 80)
    assert db_num_db(-79.5, 80, str_len=3)
    assert db_num_db(10, 50)
    assert db_num_db(5.5, 50)
    assert db_num_db(-0.5, 50)


def test_make_command_lookup(command_dict):
    """Test creation of command lookup for values dict and min/max range."""
    command_lookup = get_command_lookup(command_dict)

    command = command_lookup[const.ATTR_VOLUME]
    assert command.values.min == -80
    assert command.values.max == 18

    command = command_lookup[const.ATTR_BASS]
    assert command.values["min"] == -6
    assert command.values["max"] == 6

    command = command_lookup["channel_level_fl"]
    assert command.values.min == -12
    assert command.values["max"] == 12

    command = command_lookup[const.ATTR_LFE_LEVEL]
    assert command.values["min"] == -10
    assert command.values["max"] == 0

    command = command_lookup[const.ATTR_DSP_DRC]
    assert str(command.values)
    assert command.values["off"] == "OFF"
    assert command.values.off == "OFF"
    assert command.values["low"] == "LIT"
    assert command.values["lit"] == "LIT"
    assert command.values.medium == "MED"
    assert command.values.med == "MED"
    assert command.values["high"] == "HEV"
    assert command.values["hev"] == "HEV"
    with pytest.raises(AVReceiverInvalidArgumentError):
        assert command.values.de == "HEV"
    assert command.values.max is None
    assert command.values["max"] is None

    command = command_lookup["audyssey_multi_eq"]
    assert str(command.values)
    assert command.values["off"] == "OFF"
    assert command.values["audyssey"] == "AUDYSSEY"
    assert command.values["byp.lr"] == "BYP.LR"


def test_generate_commands(command_dict):
    """Test creation of command messages."""
    command_lookup = get_command_lookup(command_dict)

    assert "channel_level_fr" in command_lookup

    with pytest.raises(Exception):
        _ = command_lookup[const.ATTR_POWER].message
    assert command_lookup[const.ATTR_POWER].set_val(True).message == "PWON\r"
    assert command_lookup[const.ATTR_POWER].set_val(False).message == "PWOFF\r"
    assert command_lookup[const.ATTR_POWER].set_query().message == "PW?\r"
    assert command_lookup[const.ATTR_POWER].name == "power"

    assert command_lookup[const.ATTR_VOLUME].set_val(-5).message == "MV75\r"
    assert command_lookup[const.ATTR_VOLUME].set_val(-30.5).message == "MV495\r"
    assert command_lookup[const.ATTR_VOLUME].set_query().message == "MV?\r"
    assert command_lookup[const.ATTR_VOLUME_UP].set_val().message == "MVUP\r"
    assert command_lookup[const.ATTR_VOLUME_DOWN].set_val().message == "MVDOWN\r"

    assert command_lookup[const.ATTR_MUTE].set_val(True).message == "MUON\r"
    assert command_lookup[const.ATTR_MUTE].set_val(False).message == "MUOFF\r"
    assert command_lookup[const.ATTR_MUTE].set_query().message == "MU?\r"

    assert command_lookup[const.ATTR_SOURCE].set_val("phono").message == "SIPHONO\r"
    assert command_lookup[const.ATTR_SOURCE].set_val("sat/CbL").message == "SISAT/CBL\r"
    assert command_lookup[const.ATTR_SOURCE].set_query().message == "SI?\r"

    assert (
        command_lookup[const.ATTR_SOUND_MODE].set_val("pure direct").message
        == "MSPURE DIRECT\r"
    )

    assert (
        command_lookup[const.ATTR_TONE_CONTROL].set_val(True).message
        == "PSTONE CTRL ON\r"
    )
    assert (
        command_lookup[const.ATTR_TONE_CONTROL].set_query().message == "PSTONE CTRL ?\r"
    )

    assert command_lookup[const.ATTR_TREBLE].set_val(3).message == "PSTRE 53\r"
    assert command_lookup[const.ATTR_TREBLE].set_val(-3.5).message == "PSTRE 465\r"

    assert command_lookup[const.ATTR_BASS].set_val(0).message == "PSBAS 50\r"

    assert command_lookup[const.ATTR_DSP_DRC].set_val(False).message == "PSDYNVOL OFF\r"
    assert command_lookup[const.ATTR_DSP_DRC].set_query().message == "PSDYNVOL ?\r"
    assert command_lookup[const.ATTR_DSP_DRC].set_val("HEV").message == "PSDYNVOL HEV\r"
    assert (
        command_lookup[const.ATTR_DSP_DRC].set_val("high").message == "PSDYNVOL HEV\r"
    )

    assert command_lookup[const.ATTR_LFE_LEVEL].set_val(0).message == "PSLFE 0\r"
    assert command_lookup[const.ATTR_LFE_LEVEL].set_val(-7).message == "PSLFE -7\r"

    assert command_lookup[const.ATTR_ZONE1_POWER].set_val(True).message == "ZMON\r"
    assert command_lookup[const.ATTR_ZONE1_POWER].set_val(False).message == "ZMOFF\r"

    # check that this works - won't be supported:
    assert command_lookup["Z3CS"].set_val("st").message == "Z3CSST\r"
