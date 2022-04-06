import threading as th
import time
from typing import List, Tuple

import pytest

from orbitalcoms.coms.drivers.driver import ComsDriver
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.strategies.localstrat import (
    LocalComsStrategy,
    get_linked_local_strats,
)
from orbitalcoms.coms.subscribers.subscription import ComsSubscription
from orbitalcoms.stations.launchstation import LaunchStation


@pytest.fixture
def ls_and_loc() -> Tuple[LaunchStation, ComsDriver]:
    a_strat, b_strat = get_linked_local_strats()
    a = ComsDriver(a_strat)
    b = ComsDriver(b_strat)
    ls = LaunchStation(a)
    yield ls, b
    a.end_read_loop()
    b.end_read_loop()


def test_all_fields_start_false(ls_and_loc: Tuple[LaunchStation, ComsDriver]):
    ls, _ = ls_and_loc
    assert ls.abort is False
    assert ls.qdm is False
    assert ls.stab is False
    assert ls.launch is False
    assert ls.armed is False
    assert ls.data is None


def test_bind_queue(ls_and_loc: Tuple[LaunchStation, ComsDriver]):
    ls, loc = ls_and_loc
    ls_read: List[ComsMessage] = []
    ls.bind_queue(ls_read)

    def read():
        ls._coms.read(timeout=5)
        ls._coms.read(timeout=5)
        ls._coms.read(timeout=5)

    t = th.Thread(target=read, daemon=True)
    t.start()

    loc.write(
        ComsMessage(
            ABORT=0, QDM=0, STAB=1, LAUNCH=1, ARMED=1, DATA={"msg": "this is msg #1"}
        )
    )
    loc.write(
        ComsMessage(
            ABORT=0, QDM=0, STAB=1, LAUNCH=1, ARMED=1, DATA={"msg": "this is msg #2"}
        )
    )
    loc.write(
        ComsMessage(
            ABORT=0, QDM=0, STAB=1, LAUNCH=1, ARMED=1, DATA={"msg": "this is msg #3"}
        )
    )
    t.join()

    assert len(ls_read) == 3
    for i, msg in enumerate(ls_read):
        assert msg.DATA["msg"] == f"this is msg #{i+1}"


def test_state_updated_on_read(ls_and_loc: Tuple[LaunchStation, ComsDriver]):
    ls, loc = ls_and_loc
    ls_read: List[ComsMessage] = []
    ls.bind_queue(ls_read)

    def assert_state_updated(a, q, s, ln):
        t = th.Thread(target=ls._coms.read, kwargs={"timeout": 5}, daemon=True)
        t.start()
        loc.write(ComsMessage(ABORT=a, QDM=q, STAB=s, LAUNCH=ln, ARMED=1))
        t.join()
        assert ls.abort == ls.getAbortFlag() == bool(a)
        assert ls.qdm == ls.getQDMFlag() == bool(q)
        assert ls.stab == ls.getStabFlag() == bool(s)
        assert ls.launch == ls.getLaunchFlag() == bool(ln)
        assert ls.armed == ls.getArmedFlag() and ls.armed is True

    assert_state_updated(0, 0, 1, 0)
    assert_state_updated(0, 0, 1, 1)
    assert_state_updated(1, 0, 1, 1)
    assert_state_updated(1, 1, 1, 1)


def test_data_updated_on_send(ls_and_loc: Tuple[LaunchStation, ComsDriver]):
    ls, _ = ls_and_loc

    def send_msg(msg):
        ls.send(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"msg": msg}))
        assert ls.data is not None
        assert ls.data["msg"] == msg

    send_msg("Sending the first set of data")
    send_msg("Here is a second set of data")
    send_msg("All done!")
    send_msg(":)")

    assert ls.data["msg"] == ":)"


def test_send_bad_msg_fails(ls_and_loc: Tuple[LaunchStation, ComsDriver]):
    ls, loc = ls_and_loc
    loc_read = []
    loc.register_subscriber(ComsSubscription(lambda m: loc_read.append(m)))
    loc.start_read_loop()
    assert ls.send("Do not send this!") is False
    assert len(loc_read) == 0


def test_gs_recv_time(ls_and_loc: Tuple[LaunchStation, ComsDriver]):
    ls, loc = ls_and_loc

    assert ls.last_received_time is None

    assert loc.write(ComsMessage(0, 0, 0, 0, ARMED=1))
    time.sleep(0.4)
    assert isinstance(ls.last_received_time, float)
    last_recv = ls.last_received_time

    loc.write(ComsMessage(0, 0, 0, 0, ARMED=1))
    time.sleep(0.4)
    assert last_recv != ls.last_received_time


def test_gs_send_time(ls_and_loc: Tuple[LaunchStation, ComsDriver]):
    ls, _ = ls_and_loc

    assert ls.last_sent_time is None

    ls.send(ComsMessage(0, 0, 0, 0, ARMED=1))
    time.sleep(0.2)
    assert isinstance(ls.last_sent_time, float)
    last_send = ls.last_sent_time

    ls.send(ComsMessage(0, 0, 0, 0, ARMED=1))
    time.sleep(0.2)
    assert last_send != ls.last_sent_time


def test_clean_up_on_end_ctx():
    starting_num_threads = th.active_count()
    with LaunchStation(ComsDriver(LocalComsStrategy())):
        time.sleep(1)
        assert th.active_count() == starting_num_threads + 1
    assert th.active_count() == starting_num_threads
