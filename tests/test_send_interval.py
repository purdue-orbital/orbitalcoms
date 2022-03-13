import pytest
import time

from typing import Tuple

from orbitalcoms.coms.drivers.driver import ComsDriver
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.strategies.localstrat import get_linked_local_strats
from orbitalcoms import GroundStation, LaunchStation


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
