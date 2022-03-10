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


def test_gs_send_interval(gs_and_ls):
    q = []
    ls, gs = gs_and_ls
    ls.bind_queue(q)
    gs.set_send_interval(2)
    gs.send(ComsMessage(0, 0, 0, 0, 0))
    time.sleep(5)

    assert len(q) == 3

    q = []
    ls.bind_queue(q)
    gs.set_send_interval(5)
    gs.send(ComsMessage(0, 0, 0, 0, 0))
    time.sleep(12)

    assert len(q) == 3