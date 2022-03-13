import time
from typing import List, Tuple

import pytest

from orbitalcoms import GroundStation, LaunchStation
from orbitalcoms.coms.drivers.driver import ComsDriver
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.strategies.localstrat import get_linked_local_strats


@pytest.fixture
def gs_and_ls() -> Tuple[GroundStation, ComsDriver]:
    a_strat, b_strat = get_linked_local_strats()
    a = ComsDriver(a_strat)
    b = ComsDriver(b_strat)

    gs = GroundStation(a)
    ls = LaunchStation(b)

    yield gs, ls

    a.end_read_loop()
    b.end_read_loop()

    if gs._timeout_thread and gs._timeout_thread.is_alive():
        gs._timeout_thread.stop()
    if ls._timeout_thread and ls._timeout_thread.is_alive():
        ls._timeout_thread.stop()


@pytest.mark.parametrize(
    "int_time,wait_time",
    [
        pytest.param(2, 5, id="short interval"),
        pytest.param(5, 12, id="long interval"),
    ],
)
def test_gs_send_interval_msgs(gs_and_ls, int_time, wait_time):
    gs, ls = gs_and_ls

    q = []
    ls.bind_queue(q)
    gs.set_send_interval(int_time)
    gs.send(ComsMessage(0, 0, 0, 0))
    time.sleep(wait_time)

    assert len(q) == 3


@pytest.mark.parametrize(
    "int_time,wait_time",
    [
        pytest.param(2, 5, id="short interval"),
        pytest.param(5, 12, id="long interval"),
    ],
)
def test_ls_send_interval(gs_and_ls, int_time, wait_time):
    gs, ls = gs_and_ls

    q = []
    gs.bind_queue(q)
    ls.set_send_interval(int_time)
    ls.send(ComsMessage(0, 0, 0, 0))
    time.sleep(wait_time)

    assert len(q) == 3


def test_send_interval_is_stoppable(gs_and_ls):
    gs, ls = gs_and_ls
    q = []

    gs.set_send_interval(4)
    gs.send(ComsMessage(0, 0, 0, 0, ARMED=1))
    time.sleep(1)

    ls.bind_queue(q)
    time.sleep(1)

    gs.set_send_interval(None)
    time.sleep(3)

    assert q == []


def test_interval_sends_updated_states(gs_and_ls: Tuple[GroundStation, LaunchStation]):
    gs, ls = gs_and_ls

    q: List[ComsMessage] = []
    gs.set_send_interval(3)
    gs.send(ComsMessage(0, 0, 0, 0, ARMED=1))
    time.sleep(1)

    ls.bind_queue(q)
    time.sleep(4)

    gs.send(ComsMessage(1, 0, 0, 0, ARMED=1))
    time.sleep(4)

    gs.set_send_interval(None)
    abort_over_time = [m.ABORT for m in q]
    assert abort_over_time == [0, 1, 1]


@pytest.mark.skip(reason="Feature not implimented")
def test_send_empty_message_with_no_prev_send(gs_and_ls):
    gs, ls = gs_and_ls

    q = []
    ls.bind_queue(q)
    gs.set_interval(2)
    time.sleep(3)

    ls.bind_queue(None)
    assert len(q) > 0

    msg: ComsMessage = q.pop()
    assert msg.ABORT == 0
    assert msg.LAUNCH == 0
    assert msg.QDM == 0
    assert msg.STAB == 0
