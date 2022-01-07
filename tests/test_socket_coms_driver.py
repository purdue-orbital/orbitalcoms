import socket
import threading as th
import time

import pytest

from orbitalcoms.coms.drivers.socketcomsdriver import SocketComsDriver
from orbitalcoms.coms.messages.message import ComsMessage


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
def test_write_read(msg_a, msg_b):
    host_read = None
    client_read = None

    portcv = th.Condition()
    readcv = th.Condition()
    ready_switcher = False
    port = -1

    def _host():
        nonlocal host_read, port, ready_switcher
        # coms = SocketComsDriver.accept_connection_at("127.0.1.1", 0)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("127.0.1.1", 0))
            port = server.getsockname()[1]

        with portcv:
            portcv.notify()

        coms = SocketComsDriver.accept_connection_at("127.0.1.1", port)
        coms.start_read_loop()

        with readcv:
            ready_switcher = True
            readcv.notify()
        host_read = coms.read()

        with readcv:
            readcv.wait_for(lambda: not ready_switcher)

        time.sleep(0.5)
        coms.write(msg_a)

        coms.end_read_loop()
        coms._sock.close()

    def _client():
        nonlocal client_read, ready_switcher
        time.sleep(0.3)
        coms = SocketComsDriver.connect_to("127.0.1.1", port)
        coms.start_read_loop()

        with readcv:
            readcv.wait_for(lambda: ready_switcher)

        time.sleep(0.5)
        coms.write(msg_b)

        with readcv:
            ready_switcher = False
            readcv.notify()

        client_read = coms.read()
        coms.end_read_loop()

        coms._sock.shutdown(socket.SHUT_RDWR)
        coms._sock.close()

    # TODO: This threading can deadlock, doesn't happen for the most part so good
    # enough for now, but shouldn't deadlock in first place
    # For safety, errors out automatically after ~20secs
    host_th = th.Thread(target=_host, daemon=True)
    client_th = th.Thread(target=_client, daemon=True)

    host_th.start()
    with portcv:
        portcv.wait_for(lambda: port > 0)
    time.sleep(0.2)

    client_th.start()
    time.sleep(0.2)
    client_th.join(timeout=10)
    host_th.join(timeout=10)

    assert not client_th.is_alive()
    assert not host_th.is_alive()

    expected_host_read = ComsMessage(ABORT=1, ARMED=1, QDM=1, STAB=0, LAUNCH=0)
    expected_client_read = ComsMessage(ABORT=0, ARMED=0, QDM=1, STAB=0, LAUNCH=0)

    assert str(host_read) == str(expected_host_read)
    assert str(client_read) == str(expected_client_read)

    assert host_read.QDM
    assert client_read.QDM


def test_error_when_cannot_connect():
    # this test will fail if something is running on 5000
    with pytest.raises(ConnectionRefusedError):
        SocketComsDriver.connect_to("127.0.1.1", 5000)
