from time import sleep
from orbitalcoms.coms.drivers.basedriver import ComsDriverReadLooop


def test_start_stop_read_loop():
    # Not gonna pass type checking, just make sure it wakes up and dies
    rl = ComsDriverReadLooop(
        get_msg=lambda: sleep(1), on_msg=lambda: sleep(1), daemon=True
    )
    rl.start()
    sleep(2)
    assert rl.is_alive()
    rl.stop()
    sleep(2)
    assert not rl.is_alive()
