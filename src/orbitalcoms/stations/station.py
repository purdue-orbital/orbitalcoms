from __future__ import annotations

from abc import ABC, abstractmethod
from threading import Event, Thread
from types import TracebackType
from typing import Any, Callable, Dict, Type

from typing_extensions import Protocol

from ..coms.errors import ComsMessageParseError

from ..coms import (
    ComsDriver,
    ComsMessage,
    ComsSubscription,
    ParsableComType,
    construct_message,
)

class Station(ABC):
    def __init__(self, coms: ComsDriver, timeout: float = 0.0):
        self._coms = coms

        self._last_sent: ComsMessage | None = None
        self._last_received: ComsMessage | None = None
        self._last_data: Dict[str, Any] | None = None

        self.queue: Queueable | None = None

        self._timeout = timeout

        self._timeout_thread = _AutoSendOnInterval(
            self.resend_last, self._timeout
        )

        def receive(message: ComsMessage) -> None:
            self._on_receive(message)
            self._last_received = message
            if self.queue is not None:
                self.queue.append(message)

        self._coms.register_subscriber(ComsSubscription(receive))
        self._coms.start_read_loop()

    def __enter__(self) -> Station:
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.__cleanup()

    def __del__(self) -> None:
        self.__cleanup()

    def __cleanup(self) -> None:
        self._coms.end_read_loop()

    @property
    @abstractmethod
    def abort(self) -> bool:
        ...

    @property
    @abstractmethod
    def qdm(self) -> bool:
        ...

    @property
    @abstractmethod
    def stab(self) -> bool:
        ...

    @property
    @abstractmethod
    def launch(self) -> bool:
        ...

    @property
    @abstractmethod
    def armed(self) -> bool:
        ...

    @property
    def data(self) -> Dict[str, Any] | None:
        return self._last_data

    @property
    def last_sent(self) -> ComsMessage | None:
        return self._last_sent

    @property
    def last_received(self) -> ComsMessage | None:
        return self._last_received

    def _on_receive(self, new: ComsMessage) -> Any:
        ...

    def _on_send(self, new: ComsMessage) -> Any:
        ...

    def send(self, data: ParsableComType) -> bool:
        try:
            message = construct_message(data)
        except (TypeError, ComsMessageParseError):
            return False
        if self._coms.write(message, suppress_errors=True):
            self._on_send(message)
            self._last_sent = message

            if self._timeout_thread.is_alive():
                self._timeout_thread.stop()

            if self._timeout != 0:
                self._timeout_thread = _AutoSendOnInterval(self.resend_last, self._timeout)
                self._timeout_thread.start()

            return True
        return False

    def resend_last(self) -> None:
        if self._last_sent is not None:
            self._coms.write(self._last_sent, suppress_errors=True)
            self._on_send(self._last_sent)
        else:
            ...  # maybe raise error? log?
    
    def set_send_interval(self, interval: float | None) -> None:
        if interval is not None and not isinstance(interval, (int, float)):
            raise TypeError("Expected interval of type `float` or `None`")
        
        if interval is None:
            interval = 0.0
        elif interval < 0:
            raise ValueError("Send inverval cannot be less than 0")
        
        self._timeout = interval

    def bind_queue(self, queue: Queueable | None) -> None:
        """Alias for bindQueue"""
        return self.bindQueue(queue)

    def bindQueue(self, queue: Queueable | None) -> None:
        """Supply a queue reference for data placement"""
        self.queue = queue

    def getLaunchFlag(self) -> bool:
        return self.launch

    def getQDMFlag(self) -> bool:
        return self.qdm

    def getAbortFlag(self) -> bool:
        return self.abort

    def getStabFlag(self) -> bool:
        return self.stab

    def getArmedFlag(self) -> bool:
        return self.armed


class _AutoSendOnInterval(Thread):
    def __init__(self, resend_func: Callable[[], None], interval: float, *a: Any, **kw: Any) -> None:
        super().__init__(*a, **kw)
        self.stop_event = Event()
        self.resend_func = resend_func
        self.interval = interval

    def run(self) -> None:
        while not self.stop_event.is_set():
            self.stop_event.wait(self.interval)
            if not self.stop_event.is_set():
                self.resend_func()

    def stop(self) -> None:
        self.stop_event.set()
        self.join()

class Queueable(Protocol):
    """Class able to queue messages"""

    def append(self, t: Any) -> Any:
        ...
