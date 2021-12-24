from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Condition, Event, Thread
from typing import TYPE_CHECKING, Any, Callable, Optional, Set

from ..errors import ComsDriverReadError
from ..subscribers import OneTimeComsSubscription

if TYPE_CHECKING:
    from ..messages import ComsMessage, ParsableComType
    from ..subscribers import ComsSubscriberLike


class BaseComsDriver(ABC):
    """Base Class for any Communication Strategies"""

    def __init__(self) -> None:
        super().__init__()
        self.subscrbers: Set[ComsSubscriberLike] = set()
        self._read_loop: Optional[ComsDriverReadLooop] = None

    def start_read_loop(self, block: bool = False) -> ComsDriverReadLooop:
        if self._read_loop:
            self.end_read_loop()
        self._read_loop = self._spawn_read_loop_thread()
        self._read_loop.start()
        if block:
            self._read_loop.join()
        return self._read_loop

    def end_read_loop(self) -> None:
        if self._read_loop:
            if self._read_loop.is_alive():
                self._read_loop.stop()
            self._read_loop = None

    def _spawn_read_loop_thread(self) -> ComsDriverReadLooop:
        return ComsDriverReadLooop(
            lambda: self._notify_subscribers(self._read()), daemon=True
        )

    @property
    def is_reading(self) -> bool:
        return self._read_loop is not None and self._read_loop.is_alive()

    def read(self) -> ComsMessage:
        cv = Condition()
        message: Optional[ComsMessage] = None

        def _get_next(m: ComsMessage) -> None:
            nonlocal message
            with cv:
                message = m
                cv.notify()

        self.register_subscriber(OneTimeComsSubscription(_get_next))
        with cv:
            cv.wait_for(lambda: message is not None)
            if message is None:
                raise ComsDriverReadError("Failed to read next message")
        return message

    @abstractmethod
    def _read(self) -> ComsMessage:
        ...

    def write(self, m: ParsableComType, suppress_errors: bool = False) -> bool:
        try:
            self._write(m)
            return True
        except Exception:
            if suppress_errors:
                return False
            raise

    @abstractmethod
    def _write(self, m: ParsableComType) -> None:
        ...

    def register_subscriber(self, sub: ComsSubscriberLike) -> None:
        self.subscrbers.add(sub)

    def unregister_subscriber(self, sub: ComsSubscriberLike) -> None:
        if sub in self.subscrbers:
            self.subscrbers.remove(sub)

    def _notify_subscribers(self, m: ComsMessage) -> None:
        for s in self.subscrbers.copy():
            s.update(m, self)


class ComsDriverReadLooop(Thread):
    def __init__(
        self,
        read: Callable[[], Any],
        name: Optional[str] = None,
        daemon: Optional[bool] = None,
    ) -> None:
        super().__init__(name=name, daemon=daemon)
        self._stop_event = Event()
        self.read = read

    def run(self) -> None:
        while not self._stop_event.is_set():
            self.read()
            self._stop_event.wait(1)

    def stop(self, timeout: Optional[float] = None) -> None:
        self._stop_event.set()
        self.join(timeout=timeout)
