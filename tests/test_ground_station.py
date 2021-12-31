import threading as th
from typing import List, Tuple

import pytest

from orbitalcoms.coms.drivers.localcomsdriver import LocalComsDriver
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.subscribers.subscription import ComsSubscription
from orbitalcoms.stations.groundstation import GroundStation


@pytest.fixture
def gs_and_loc() -> Tuple[GroundStation, LocalComsDriver]:
    a, b = LocalComsDriver.create_linked_coms()
    gs = GroundStation(a)
    yield gs, b
    a.end_read_loop()
    b.end_read_loop()


def test_all_fields_start_false(gs_and_loc: Tuple[GroundStation, LocalComsDriver]):
    gs, _ = gs_and_loc
    assert gs.abort is False
    assert gs.qdm is False
    assert gs.stab is False
    assert gs.launch is False
    assert gs.armed is False
    assert gs.data is None


def test_bind_queue(gs_and_loc: Tuple[GroundStation, LocalComsDriver]):
    gs, loc = gs_and_loc
    gs_read: List[ComsMessage] = []
    gs.bind_queue(gs_read)

    def read():
        gs._coms.read()
        gs._coms.read()
        gs._coms.read()

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

    assert len(gs_read) == 3
    for i, msg in enumerate(gs_read):
        assert msg.DATA["msg"] == f"this is msg #{i+1}"


def test_state_mataches_sent(gs_and_loc: Tuple[GroundStation, LocalComsDriver]):
    gs, _ = gs_and_loc

    def send_msg(a, q, s, ln):
        gs.send(ComsMessage(ABORT=a, QDM=q, STAB=s, LAUNCH=ln, ARMED=1))
        assert gs.abort == gs.getAbortFlag() == bool(a)
        assert gs.qdm == gs.getQDMFlag() == bool(q)
        assert gs.launch == gs.getLaunchFlag() == bool(ln)
        assert gs.stab == gs.getStabFlag() == bool(s)
        assert gs.armed == gs.getArmedFlag() and gs.armed is True

    send_msg(0, 0, 1, 0)
    send_msg(0, 0, 1, 1)
    send_msg(1, 0, 1, 1)
    send_msg(1, 1, 1, 1)


def test_data_matches_last_recv(gs_and_loc: Tuple[GroundStation, LocalComsDriver]):
    gs, loc = gs_and_loc

    def send_msg(msg):
        t = th.Thread(target=lambda: gs._coms.read(), daemon=True)
        t.start()
        loc.write(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"msg": msg}))
        t.join()
        assert gs.data["msg"] == msg

    send_msg("This is a message")
    send_msg("Sending another to make sure it updates")
    send_msg(":)")

    assert gs.data["msg"] == ":)"


def test_send_bad_msg_fails(gs_and_loc: Tuple[GroundStation, LocalComsDriver]):
    gs, loc = gs_and_loc
    loc_read = []
    loc.register_subscriber(ComsSubscription(lambda m: loc_read.append(m)))
    loc.start_read_loop()
    assert gs.send("Not a good msg") is False
    assert len(loc_read) == 0


@pytest.mark.skip(reason="Feature not implimented")
def test_data_retains_unupdated_keys(gs_and_loc: Tuple[GroundStation, LocalComsDriver]):
    gs, loc = gs_and_loc

    loc.write(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"key1": 1}))
    loc.write(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"key2": 2}))
    loc.write(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"key3": ":)"}))
    loc.write(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"key2": 4}))

    assert gs.data["key1"] == 1
    assert gs.data["key2"] == 4
    assert gs.data["key3"] == ":)"


@pytest.mark.skip(reason="Feature not implimented")
def test_station_does_not_unarm(gs_and_loc: Tuple[GroundStation, LocalComsDriver]):
    gs, _ = gs_and_loc

    with pytest.raises(Exception):  # TODO: tighter exception needed
        gs.send(ComsMessage(0, 0, 0, 0, ARMED=1, DATA={"key1": 1}))
        gs.send(ComsMessage(0, 0, 0, 0, ARMED=0, DATA={"key2": 2}))