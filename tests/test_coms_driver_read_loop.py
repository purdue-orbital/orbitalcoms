from time import sleep
from orbitalcoms.coms.drivers.basedriver import ComsDriverReadLooop


def test_start_stop_read_loop():
    rl = ComsDriverReadLooop(read=lambda: sleep(1), daemon=True)
    rl.start()
    sleep(2)
    assert rl.is_alive()
    rl.stop()
    sleep(2)
    assert not rl.is_alive()