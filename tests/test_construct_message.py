from typing import Type
import pytest

from orbitalcoms.coms.errors.errors import ComsMessageParseError
from orbitalcoms.coms.messages.message import ComsMessage, construct_message


def test_construct_from_message():
    msg = ComsMessage(ARMED=1, ABORT=0, LAUNCH=1, STAB=1, QDM=0, DATA={"height": 500})
    new_msg = construct_message(msg)

    assert isinstance(new_msg, ComsMessage)
    assert msg.ARMED == new_msg.ARMED
    assert msg.ABORT == new_msg.ABORT
    assert msg.LAUNCH == new_msg.LAUNCH
    assert msg.QDM == new_msg.QDM
    assert msg.DATA["height"] == new_msg.DATA["height"]


def test_construct_from_str():
    msg = construct_message(
        (
            "{"
            '"ABORT": 0,'
            '"QDM": 0,'
            '"STAB": 1,'
            '"LAUNCH": 1,'
            '"ARMED": 1,'
            '"DATA": {"height": 500}'
            "}"
        )
    )

    assert isinstance(msg, ComsMessage)
    assert 1 == msg.ARMED
    assert 0 == msg.ABORT
    assert 1 == msg.LAUNCH
    assert 0 == msg.QDM
    assert 1 == msg.STAB
    assert 500 == msg.DATA["height"]


def test_cannot_parse_str():
    with pytest.raises(ComsMessageParseError):
        construct_message("This is not a parsable string")


def test_construct_from_dict():
    msg = construct_message(
        {
            "ABORT": 0,
            "QDM": 0,
            "STAB": 1,
            "LAUNCH": 1,
            "ARMED": 1,
            "DATA": {"height": 500},
        }
    )

    assert isinstance(msg, ComsMessage)
    assert 1 == msg.ARMED
    assert 0 == msg.ABORT
    assert 1 == msg.LAUNCH
    assert 0 == msg.QDM
    assert 1 == msg.STAB
    assert 500 == msg.DATA["height"]


def test_cannot_parse_dict():
    with pytest.raises(TypeError):
        construct_message({"Error": "This is not a valid dict"})


def test_accepts_int_type():
    construct_message({"ABORT": 1, "LAUNCH": 0, "STAB": 0, "QDM": 1})


def test_accepts_boolean_type():
    m = construct_message({"ABORT": True, "LAUNCH": False, "STAB": False, "QDM": True})

    assert m.ABORT == 1
    assert m.LAUNCH == 0
    assert m.STAB == 0
    assert m.QDM == 1


def test_error_on_invalid_type():
    with pytest.raises(TypeError):
        construct_message({"ABORT": "t", "LAUNCH": "f", "STAB": "f", "QDM": "t"})


def test_error_on_invalid_arm_option():
    with pytest.raises(TypeError):
        construct_message({"ABORT": 1, "LAUNCH": 0, "STAB": 0, "QDM": 1, "ARMED": "t"})


def test_error_on_invalid_data_option():
    with pytest.raises(TypeError):
        construct_message({"ABORT": 1, "LAUNCH": 0, "STAB": 0, "QDM": 1, "DATA": 0})