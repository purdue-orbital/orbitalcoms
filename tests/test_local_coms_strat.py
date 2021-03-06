import threading
import time
from typing import Tuple

import pytest

from orbitalcoms.coms.drivers.driver import ComsDriver
from orbitalcoms.coms.errors.errors import ComsDriverWriteError
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.strategies.localstrat import get_linked_local_strats
from orbitalcoms.coms.subscribers.subscription import ComsSubscription


@pytest.fixture
def coms_drivers():
    a_strat, b_strat = get_linked_local_strats()
    a = ComsDriver(a_strat)
    b = ComsDriver(b_strat)
    yield a, b
    a.end_read_loop()
    b.end_read_loop()


@pytest.mark.parametrize(
    "msg_a, msg_b",
    [
        pytest.param(
            ComsMessage(
                ABORT=1, STAB=0, LAUNCH=0, QDM=1, ARMED=1, DATA={"msg": "msg #1"}
            ),
            ComsMessage(
                ABORT=0, STAB=1, LAUNCH=1, QDM=0, ARMED=0, DATA={"msg": "msg #2"}
            ),
            id="ComsMessages",
        ),
        pytest.param(
            '{"ABORT": 1, "QDM": 1, "STAB": 0, "LAUNCH": 0, "ARMED": 1, "DATA": {"msg": "msg #1"} }',
            '{"ABORT": 0, "QDM": 0, "STAB": 1, "LAUNCH": 1, "ARMED": 0, "DATA": {"msg": "msg #2"} }',
            id="strings",
        ),
        pytest.param(
            {
                "ABORT": 1,
                "QDM": 1,
                "STAB": 0,
                "LAUNCH": 0,
                "ARMED": 1,
                "DATA": {"msg": "msg #1"},
            },
            {
                "ABORT": 0,
                "QDM": 0,
                "STAB": 1,
                "LAUNCH": 1,
                "ARMED": 0,
                "DATA": {"msg": "msg #2"},
            },
            id="dictionaries",
        ),
    ],
)
def test_write_read(coms_drivers: Tuple[ComsDriver, ComsDriver], msg_a, msg_b):
    a, b = coms_drivers

    a_read = []
    b_read = []

    a.register_subscriber(ComsSubscription(lambda m: a_read.append(m)))
    b.register_subscriber(ComsSubscription(lambda m: b_read.append(m)))
    a.start_read_loop()
    b.start_read_loop()

    assert threading.active_count() == 3
    assert a.is_reading
    assert b.is_reading

    a.write(msg_b)
    b.write(msg_b)
    a.write(msg_a)

    time.sleep(1.2)

    a_expected = [
        ComsMessage(ABORT=0, STAB=1, LAUNCH=1, QDM=0, ARMED=0, DATA={"msg": "msg #2"}),
    ]

    b_expected = [
        ComsMessage(ABORT=0, STAB=1, LAUNCH=1, QDM=0, ARMED=0, DATA={"msg": "msg #2"}),
        ComsMessage(ABORT=1, STAB=0, LAUNCH=0, QDM=1, ARMED=1, DATA={"msg": "msg #1"}),
    ]

    assert len(a_read) == len(a_expected)
    assert len(b_read) == len(b_expected)

    def msgs_not_same_but_equal(m1: ComsMessage, m2: ComsMessage):
        assert m1 is not m2
        assert m1.ABORT == m2.ABORT
        assert m1.STAB == m2.STAB
        assert m1.LAUNCH == m2.LAUNCH
        assert m1.QDM == m2.QDM
        assert m1.ARMED == m2.ARMED
        assert m1.DATA == m2.DATA

    for m1, m2 in zip(a_read, a_expected):
        msgs_not_same_but_equal(m1, m2)

    for m1, m2 in zip(b_read, b_expected):
        msgs_not_same_but_equal(m1, m2)


def test_send_invailid(coms_drivers):
    with pytest.raises(ComsDriverWriteError):
        a, _ = coms_drivers
        a.write("Invalid")


def test_send_invalid_ignore_err(coms_drivers):
    a, _ = coms_drivers
    assert a.write("Invalid", suppress_errors=True) is False


def test_dont_start_multiple_read_loops(coms_drivers):
    a, _ = coms_drivers
    a.start_read_loop()
    a.start_read_loop()
    a.start_read_loop()
    assert threading.active_count() == 2
