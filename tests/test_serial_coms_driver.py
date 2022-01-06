import os
import pty
import time

import pytest

from orbitalcoms.coms.drivers.serialcomsdriver import SerialComsDriver
from orbitalcoms.coms.messages.message import ComsMessage, construct_message
from orbitalcoms.coms.subscribers.subscription import ComsSubscription


def test_port_access():
    m, _ = pty.openpty()
    m_name = os.ttyname(m)
    s = SerialComsDriver(m_name, 9600)

    assert m_name == s.port
    with pytest.raises(AttributeError):
        s.port = "should not be assignable"


def test_baudrate_access():
    m, _ = pty.openpty()
    m_name = os.ttyname(m)
    s = SerialComsDriver(m_name, 9600)

    assert 9600 == s.baudrate
    with pytest.raises(AttributeError):
        s.baudrate = 5000


@pytest.mark.parametrize(
    "msg_a, msg_b",
    [
        pytest.param(
            ComsMessage(ABORT=0, ARMED=0, QDM=1, STAB=0, LAUNCH=0),
            ComsMessage(ABORT=1, ARMED=1, QDM=1, STAB=0, LAUNCH=0),
            id="ComsMessages",
        ),
        pytest.param(
            '{"ABORT": 0, "ARMED": 0, "QDM": 1, "STAB": 0, "LAUNCH": 0}',
            '{"ABORT": 1, "ARMED": 1, "QDM": 1, "STAB": 0, "LAUNCH": 0}',
            id="strings",
        ),
        pytest.param(
            {"ABORT": 0, "ARMED": 0, "QDM": 1, "STAB": 0, "LAUNCH": 0},
            {"ABORT": 1, "ARMED": 1, "QDM": 1, "STAB": 0, "LAUNCH": 0},
            id="dictionaries",
        ),
    ],
)
def test_write(msg_a, msg_b):
    m, s = pty.openpty()
    s_name = os.ttyname(s)
    coms = SerialComsDriver(s_name, 9600)

    coms.write(msg_b)
    coms.write(msg_b)
    coms.write(msg_a)
    time.sleep(0.1)

    # make sure messages read
    pty_contents = os.read(m, 3000).decode()
    assert pty_contents.endswith("&")
    msgs = pty_contents.split("&")
    msgs.pop()
    read = [construct_message(m) for m in msgs]

    expected = [
        ComsMessage(ABORT=1, ARMED=1, QDM=1, STAB=0, LAUNCH=0),
        ComsMessage(ABORT=1, ARMED=1, QDM=1, STAB=0, LAUNCH=0),
        ComsMessage(ABORT=0, ARMED=0, QDM=1, STAB=0, LAUNCH=0),
    ]

    assert len(read) == len(expected)

    def msgs_not_same_but_equal(m1: ComsMessage, m2: ComsMessage):
        return (
            m1 is not m2
            and m1.ABORT == m2.ABORT
            and m1.STAB == m2.STAB
            and m1.LAUNCH == m2.LAUNCH
            and m1.QDM == m2.QDM
            and m1.ARMED == m2.ARMED
            and m1.DATA == m2.DATA
        )

    for m1, m2 in zip(read, expected):
        assert msgs_not_same_but_equal(m1, m2)


def test_preproc_and_read():
    m, s = pty.openpty()
    s_name = os.ttyname(s)
    coms = SerialComsDriver(s_name, 9600)

    msg_a = ComsMessage(ABORT=0, ARMED=0, QDM=1, STAB=0, LAUNCH=0)
    msg_b = ComsMessage(ABORT=1, ARMED=1, QDM=1, STAB=0, LAUNCH=0)
    read = []
    coms.register_subscriber(ComsSubscription(lambda m: read.append(m)))
    os.write(m, SerialComsDriver._preprocess_write_msg(msg_b))
    os.write(m, SerialComsDriver._preprocess_write_msg(msg_a))
    os.write(m, SerialComsDriver._preprocess_write_msg(msg_b))
    coms.start_read_loop()
    coms.read(timeout=5)
    coms.read(timeout=5)
    coms.read(timeout=5)
    coms.end_read_loop()

    expected = [
        ComsMessage(ABORT=1, ARMED=1, QDM=1, STAB=0, LAUNCH=0),
        ComsMessage(ABORT=0, ARMED=0, QDM=1, STAB=0, LAUNCH=0),
        ComsMessage(ABORT=1, ARMED=1, QDM=1, STAB=0, LAUNCH=0),
    ]

    assert len(read) == len(expected)

    def msgs_not_same_but_equal(m1: ComsMessage, m2: ComsMessage):
        return (
            m1 is not m2
            and m1.ABORT == m2.ABORT
            and m1.STAB == m2.STAB
            and m1.LAUNCH == m2.LAUNCH
            and m1.QDM == m2.QDM
            and m1.ARMED == m2.ARMED
            and m1.DATA == m2.DATA
        )

    for m1, m2 in zip(read, expected):
        assert msgs_not_same_but_equal(m1, m2)
