import pytest
from attrs import exceptions

from orbitalcoms.coms.messages.message import ComsMessage


def test_construction():
    m = ComsMessage(ABORT=1, LAUNCH=0, STAB=0, QDM=1)
    assert isinstance(m, ComsMessage)
    assert m.ABORT == 1
    assert m.LAUNCH == 0
    assert m.STAB == 0
    assert m.QDM == 1
    assert m.DATA is None
    assert m.ARMED is None


def test_optional_params_construction():
    m = ComsMessage(
        ABORT=0, LAUNCH=1, STAB=1, QDM=0, DATA={"msg": "a message"}, ARMED=1
    )
    assert m.ABORT == 0
    assert m.LAUNCH == 1
    assert m.STAB == 1
    assert m.QDM == 0
    assert m.DATA["msg"] == "a message"
    assert m.ARMED == 1


def test_message_is_frozen():
    with pytest.raises(exceptions.FrozenInstanceError):
        ComsMessage(ABORT=1, LAUNCH=0, STAB=0, QDM=1).ABORT = 0


def test_missing_params():
    with pytest.raises(TypeError):
        ComsMessage(ABORT=0, QDM=0)


def test_construction_from_str():
    m = ComsMessage.from_string(
        '{"ABORT": 0, "QDM": 0, "STAB": 0, "LAUNCH": 0, "ARMED": 1, '
        + '"DATA": {"hello": "world"}}'
    )
    assert m.ABORT == 0
    assert m.LAUNCH == 0
    assert m.STAB == 0
    assert m.QDM == 0
    assert m.DATA["hello"] == "world"
    assert m.ARMED == 1


def test_message_to_str():
    construct_str = (
        '{"ABORT": 0, "QDM": 0, "STAB": 0, "LAUNCH": 0, "ARMED": 1, '
        '"DATA": {"hello": "world"}}'
    )

    msg_str = ComsMessage.from_string(construct_str).as_str

    assert construct_str is not msg_str
    assert construct_str == msg_str


def test_square_bracket_access():
    m = ComsMessage(
        ABORT=0, LAUNCH=1, STAB=1, QDM=0, DATA={"msg": "a message"}, ARMED=1
    )
    assert m["ABORT"] == 0
    assert m["LAUNCH"] == 1
    assert m["STAB"] == 1
    assert m["QDM"] == 0
    assert m["DATA"]["msg"] == "a message"
    assert m["ARMED"] == 1
