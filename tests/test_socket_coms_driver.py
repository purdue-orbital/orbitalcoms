import threading as th
import time
from typing import Optional
from orbitalcoms.coms.drivers.socketcomsdriver import SocketComsDriver
from orbitalcoms.coms.messages.message import ComsMessage


def test_coms_driver_connects():
    host_read = ComsMessage(0, 0, 0, 0)
    client_read = ComsMessage(0, 0, 0, 0)

    msg_str_1 = '{"ABORT": 1, "ARMED": 1, "QDM": 1, "STAB": 0, "LAUNCH": 0}'
    msg_str_2 = '{"ABORT": 0, "ARMED": 0, "QDM": 1, "STAB": 0, "LAUNCH": 0}'

    def _host():
        nonlocal host_read
        coms = SocketComsDriver.accept_connection_at("127.0.1.1", 5000)
        coms.start_read_loop()
        coms.write(ComsMessage.from_string(msg_str_1))
        host_read = coms.read()
        coms.end_read_loop()

    def _client():
        nonlocal client_read
        coms = SocketComsDriver.connect_to("127.0.1.1", 5000)
        coms.start_read_loop()
        coms.write(ComsMessage.from_string(msg_str_2))
        client_read = coms.read()
        coms.end_read_loop()

    host_th = th.Thread(target=_host, daemon=True)
    client_th = th.Thread(target=_client, daemon=True)
    host_th.start()
    time.sleep(0.2)
    client_th.start()
    client_th.join()
    host_th.join()

    assert str(host_read) == str(ComsMessage.from_string(msg_str_2))
    assert str(client_read) == str(ComsMessage.from_string(msg_str_1))

    assert host_read.QDM
    assert client_read.QDM
