from __future__ import annotations

import multiprocessing as mp
from abc import ABC, abstractmethod
from multiprocessing.connection import Connection
from threading import Condition, Event, Thread
from typing import TYPE_CHECKING, Protocol, Set, Tuple

from ..errors import ComsDriverReadError, ComsDriverWriteError
from ..messages import construct_message
from ..subscribers import OneTimeComsSubscription

if TYPE_CHECKING:
    from ..messages import ComsMessage, ParsableComType
    from ..subscribers import ComsSubscriberLike


class ComsStrategy(Protocol):
    def read(self) -> ComsMessage:
        ...

    def write(self, m: ComsMessage) -> None:
        ...


class BaseComsDriver:
    """Base Class for any Communication Strategies"""

    def __init__(self, strategy: ComsStrategy) -> None:
        self.subscrbers: Set[ComsSubscriberLike] = set()
        self._read_loop: ComsDriverReadLooop | None = None
        self._strategy = strategy

    @property
    def strategy(self) -> ComsStrategy:
        return self._strategy

    def start_read_loop(self, block: bool = False) -> ComsDriverReadLooop:
        if self._read_loop:
            self.end_read_loop()
        self._read_loop = self._spawn_read_loop_thread()
        self._read_loop.start()
        if block:
            self._read_loop.join()
        return self._read_loop

    def end_read_loop(self, timeout: float | None = None) -> None:
        if self._read_loop:
            if self._read_loop.is_alive():
                self._read_loop.stop(timeout=timeout)
            self._read_loop = None

    def _spawn_read_loop_thread(self) -> ComsDriverReadLooop:
        return ComsDriverReadLooop(self, daemon=True)

    @property
    def is_reading(self) -> bool:
        return self._read_loop is not None and self._read_loop.is_alive()

    def read(self, timeout: float | None = None) -> ComsMessage:
        cv = Condition()
        message: ComsMessage | None = None

        def _get_next(m: ComsMessage) -> None:
            nonlocal message
            with cv:
                message = m
                cv.notify()

        self.register_subscriber(OneTimeComsSubscription(_get_next))
        with cv:
            cv.wait_for(lambda: message is not None, timeout=timeout)
            if message is None:
                raise ComsDriverReadError("Failed to read next message")
        return message

    def write(self, m: ParsableComType, suppress_errors: bool = False) -> bool:
        try:
            self._strategy.write(construct_message(m))
            return True
        except Exception as e:
            if suppress_errors:
                return False
            raise ComsDriverWriteError(f"Failed to send message '{m}'") from e

    def register_subscriber(self, sub: ComsSubscriberLike) -> None:
        self.subscrbers.add(sub)

    def unregister_subscriber(self, sub: ComsSubscriberLike) -> None:
        if sub in self.subscrbers:
            self.subscrbers.remove(sub)

    def _notify_subscribers(self, m: ComsMessage) -> None:
        for s in self.subscrbers.copy():
            try:
                s.update(m, self)
            except Exception:
                # TODO: Add logging here
                if not s.expect_err:
                    self.unregister_subscriber(s)


class ComsDriverReadLooop(Thread):
    def __init__(
        self,
        coms: BaseComsDriver,
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
