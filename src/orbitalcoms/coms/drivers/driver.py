from __future__ import annotations

import logging
from threading import Condition
from typing import TYPE_CHECKING, Set

from ..._utils import log
from ..errors import ComsDriverReadError, ComsDriverWriteError
from ..messages import construct_message
from ..subscribers import OneTimeComsSubscription
from .driverreadloop import ComsDriverReadLoop

if TYPE_CHECKING:
    from ..messages import ComsMessage, ParsableComType
    from ..strategies import ComsStrategy
    from ..subscribers import ComsSubscriberLike

logger = log.make_logger(__name__, logging.ERROR)


class ComsDriver:
    """Drive Communication using a strategy"""

    def __init__(self, strategy: ComsStrategy) -> None:
        self.subscrbers: Set[ComsSubscriberLike] = set()
        self._read_loop: ComsDriverReadLoop | None = None
        self._strategy = strategy

    @property
    def strategy(self) -> ComsStrategy:
        return self._strategy

    def start_read_loop(self, block: bool = False) -> ComsDriverReadLoop:
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

    def _spawn_read_loop_thread(self) -> ComsDriverReadLoop:
        return ComsDriverReadLoop(self, daemon=True)

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
            except Exception as e:
                logger.error(f"subscriber through exception: {e}")
                if not s.expect_err:
                    self.unregister_subscriber(s)
