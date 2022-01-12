from __future__ import annotations

import multiprocessing as mp
from multiprocessing.connection import Connection
from threading import Event, Thread
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from .driver import ComsDriver


class ComsDriverReadLoop(Thread):
    def __init__(
        self,
        coms: ComsDriver,
        name: str | None = None,
        daemon: bool | None = None,
    ) -> None:
        super().__init__(name=name, daemon=daemon)
        self._stop_event = Event()
        self._coms = coms

    def run(self) -> None:
        proc, conn = self._spawn_get_msg_proc()
        proc.start()

        while not self._stop_event.is_set():
            if not proc.is_alive():
                recived = conn.recv()
                if isinstance(recived, Exception):
                    # TODO: Add logging
                    ...
                else:
                    self._coms._notify_subscribers(recived)
                proc, conn = self._spawn_get_msg_proc()
                proc.start()
            proc.join(timeout=1)

        if proc.is_alive():
            proc.terminate()

    def _spawn_get_msg_proc(
        self,
    ) -> Tuple[mp.Process, Connection]:
        a, b = mp.Pipe()

        def get_msg(conn: Connection) -> None:
            try:
                conn.send(self._coms.strategy.read())
            except Exception as e:
                conn.send(e)

        return mp.Process(target=get_msg, args=(a,), daemon=True), b

    def stop(self, timeout: float | None = None) -> None:
        self._stop_event.set()
        self.join(timeout=timeout)
