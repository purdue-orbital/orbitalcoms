from __future__ import annotations

import logging
import multiprocessing as mp
from multiprocessing.connection import Connection
from threading import Event, Thread
from typing import TYPE_CHECKING, Any, Callable, Tuple

from ..._utils import log

if TYPE_CHECKING:
    from ..messages import ComsMessage
    from ..strategies.strategy import ComsStrategy

logger = log.make_logger(__name__, logging.ERROR)


class ComsDriverReadLoop(Thread):
    def __init__(
        self,
        coms_strat: ComsStrategy,
        recv_callback: Callable[[ComsMessage], Any],
        name: str | None = None,
        daemon: bool | None = None,
    ) -> None:
        super().__init__(name=name, daemon=daemon)
        self._stop_event = Event()
        self._coms_strat = coms_strat
        self._recv_callback = recv_callback

    def run(self) -> None:
        proc, conn = self._spawn_get_msg_proc()
        proc.start()

        while not self._stop_event.is_set():
            if not proc.is_alive():
                received = conn.recv()
                if isinstance(received, Exception):
                    logger.error(f"received exception: {received}")
                else:
                    self._recv_callback(received)
                proc, conn = self._spawn_get_msg_proc()
                proc.start()
            proc.join(timeout=1)

        if proc.is_alive():
            proc.terminate()

    def _spawn_get_msg_proc(self) -> Tuple[mp.Process, Connection]:
        a, b = mp.Pipe()

        return (
            mp.Process(target=_get_msg, args=(self._coms_strat, a), daemon=True),
            b,
        )

    def stop(self, timeout: float | None = None) -> None:
        self._stop_event.set()
        self.join(timeout=timeout)


def _get_msg(strat: ComsStrategy, conn: Connection) -> None:
    """Function run to get receive next message
    NOTE: This function must be top level to work with
    multiprocessing spawn start on windows and macos
    """
    try:
        conn.send(strat.read())
    except Exception as e:
        conn.send(e)
