import time

from orbitalcoms.coms.drivers.basedriver import BaseComsDriver, ComsDriverReadLooop


class WastTimeStrat:
    def __init__(self, time_) -> None:
        self.time = time_

    def write(self, m):
        time.sleep(self.time)

    def read(self):
        time.sleep(self.time)


def test_start_stop_read_loop():
    # Not gonna pass type checking, just make sure it wakes up and dies
    rl = ComsDriverReadLooop(BaseComsDriver(WastTimeStrat(1)), daemon=True)
    rl.start()
    time.sleep(1)
    assert rl.is_alive()
    rl.stop()
    assert not rl.is_alive()


def test_ends_on_stop_in_short_time():
    rl = ComsDriverReadLooop(BaseComsDriver(WastTimeStrat(10000)), daemon=True)
    start = time.time()
    rl.start()
    time.sleep(1)
    rl.stop()
    end = time.time()
    assert end - start < 5  # must end in less than 5 sec
    assert not rl.is_alive()
