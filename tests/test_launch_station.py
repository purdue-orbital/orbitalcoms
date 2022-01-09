import threading as th
from typing import List, Tuple

import pytest

from orbitalcoms.coms.drivers.localcomsdriver import LocalComsDriver
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.subscribers.subscription import ComsSubscription
from orbitalcoms.stations.launchstation import LaunchStation


@pytest.fixture
def ls_and_loc() -> Tuple[LaunchStation, LocalComsDriver]:
    a, b = LocalComsDriver.create_linked_coms()
    ls = LaunchStation(a)
    yield ls, b
    a.end_read_loop()
    b.end_read_loop()


def test_all_fields_start_false(ls_and_loc: Tuple[LaunchStation, LocalComsDriver]):
    ls, _ = ls_and_loc
    assert ls.abort is False
    assert ls.qdm is False
    assert ls.stab is False
    assert ls.launch is False
    assert ls.armed is False
    assert ls.data is None


def test_bind_queue(ls_and_loc: Tuple[LaunchStation, LocalComsDriver]):
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


def test_state_updated_on_read(ls_and_loc: Tuple[LaunchStation, LocalComsDriver]):
    ls, loc = ls_and_loc
    ls_read: List[ComsMessage] = []
    ls.bind_queue(ls_read)

    def read():
        ls._coms.read(timeout=5)

    def assert_state_updated(a, q, s, ln):
        t = th.Thread(target=read, daemon=True)
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


def test_data_updated_on_send(ls_and_loc: Tuple[LaunchStation, LocalComsDriver]):
    ls, _ = ls_and_loc

    def send_msg(msg):
        ls.send(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"msg": msg}))
        assert ls.data["msg"] == msg

    send_msg("Sending the first set of data")
    send_msg("Here is a second set of data")
    send_msg("All done!")
    send_msg(":)")

    assert ls.data["msg"] == ":)"


def test_send_bad_msg_fails(ls_and_loc: Tuple[LaunchStation, LocalComsDriver]):
    ls, loc = ls_and_loc
    loc_read = []
    loc.register_subscriber(ComsSubscription(lambda m: loc_read.append(m)))
    loc.start_read_loop()
    assert ls.send("Do not send this!") is False
    assert len(loc_read) == 0
