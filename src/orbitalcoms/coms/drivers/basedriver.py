from __future__ import annotations

import multiprocessing as mp
from abc import ABC, abstractmethod
from threading import Condition, Event, Thread
from typing import TYPE_CHECKING, Any, Callable, Optional, Set, Tuple, TypedDict, cast

from ..errors import ComsDriverReadError, ComsDriverWriteError
from ..messages import construct_message
from ..subscribers import OneTimeComsSubscription

if TYPE_CHECKING:
    from ..messages import ComsMessage, ParsableComType
    from ..subscribers import ComsSubscriberLike


class BaseComsDriver(ABC):
    """Base Class for any Communication Strategies"""

    def __init__(self) -> None:
        super().__init__()
        self.subscrbers: Set[ComsSubscriberLike] = set()
        self._read_loop: ComsDriverReadLooop | None = None

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
        return ComsDriverReadLooop(
            lambda: self._read(), lambda m: self._notify_subscribers(m), daemon=True
        )

    @property
    def is_reading(self) -> bool:
        return self._read_loop is not None and self._read_loop.is_alive()

    def read(self) -> ComsMessage:
        cv = Condition()
        message: ComsMessage | None = None

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
            self._write(construct_message(m))
            return True
        except Exception as e:
            if suppress_errors:
                return False
            raise ComsDriverWriteError(f"Failed to send message '{m}'") from e

    @abstractmethod
    def _write(self, m: ComsMessage) -> None:
        ...

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
    class GetMsgResults(TypedDict):
        result: ComsMessage | None
        error: Exception | None

    def __init__(
        self,
        get_msg: Callable[[], ComsMessage],
        on_msg: Callable[[ComsMessage], Any],
        name: str | None = None,
        daemon: bool | None = None,
    ) -> None:
        super().__init__(name=name, daemon=daemon)
        self._stop_event = Event()
        self._get_msg = get_msg
        self._on_msg = on_msg
        self._mngr = mp.Manager()

    def run(self) -> None:
        proc, shared = self._spawn_get_msg_proc()
        proc.start()

        while not self._stop_event.is_set():
            if not proc.is_alive():
                if shared["result"]:
                    self._on_msg(shared["result"])
                else:
                    # TODO: Add logging
                    ...
                proc, shared = self._spawn_get_msg_proc()
                proc.start()
            proc.join(timeout=1)

        if proc.is_alive():
            proc.terminate()

    def _spawn_get_msg_proc(
        self,
    ) -> Tuple[mp.Process, ComsDriverReadLooop.GetMsgResults]:
        shared = cast(
            ComsDriverReadLooop.GetMsgResults,
            self._mngr.dict({"result": None, "error": None}),
        )

        def get_msg(s: ComsDriverReadLooop.GetMsgResults) -> None:
            try:
                s["result"] = self._get_msg()
            except Exception as e:
                s["error"] = e

        return mp.Process(target=get_msg, args=(shared,), daemon=True), shared

    def stop(self, timeout: float | None = None) -> None:
        self._stop_event.set()
        self.join(timeout=timeout)
