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
def test_coms_driver_connects(msg_a, msg_b):
    host_read = None
    client_read = None

    cv = th.Condition()
    port = -1

    def _host():
        nonlocal host_read, port
        # coms = SocketComsDriver.accept_connection_at("127.0.1.1", 0)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("127.0.1.1", 0))
            port = server.getsockname()[1]

        with cv:
            cv.notify()

        coms = SocketComsDriver.accept_connection_at("127.0.1.1", port)
        coms.start_read_loop()
        coms.write(msg_a)
        host_read = coms.read()
        coms.end_read_loop()
        coms._sock.shutdown(socket.SHUT_RDWR)
        coms._sock.close()

    def _client():
        nonlocal client_read
        coms = SocketComsDriver.connect_to("127.0.1.1", port)
        coms.start_read_loop()
        coms.write(msg_b)
        client_read = coms.read()
        coms.end_read_loop()
        coms._sock.shutdown(socket.SHUT_RDWR)
        coms._sock.close()

    host_th = th.Thread(target=_host, daemon=True)
    client_th = th.Thread(target=_client, daemon=True)

    host_th.start()
    with cv:
        cv.wait_for(lambda: port > 0)
    time.sleep(0.2)

    client_th.start()
    time.sleep(0.2)
    client_th.join()
    host_th.join()

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
