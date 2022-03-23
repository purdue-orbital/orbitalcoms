from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from threading import Event, Thread
from types import TracebackType
from typing import Any, Callable, Dict, Type

from typing_extensions import Protocol

from .._utils.log import make_logger
from ..coms import (
    ComsDriver,
    ComsMessage,
    ComsSubscription,
    ParsableComType,
    construct_message,
)
from ..coms.errors import ComsMessageParseError

logger = make_logger(__name__, logging.WARNING)


class Station(ABC):
    def __init__(self, coms: ComsDriver, send_interval: float = 0.0):
        self._coms = coms

        self._last_sent: ComsMessage | None = None
        self._last_received: ComsMessage | None = None
        self._last_data: Dict[str, Any] | None = None
        self._last_sent_time: float | None = None
        self._last_received_time: float | None = None

        self.queue: Queueable | None = None

        self._send_interval_time = 0.0
        self._send_interval_thread: _AutoSendOnInterval | None = None

        if send_interval:
            self.set_send_interval(send_interval)

        def receive(message: ComsMessage) -> None:
            self._on_receive(message)
            self._last_received = message
            if self.queue is not None:
                self.queue.append(message)
            self._last_received_time = time.time()

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
        """Deconstruct Station"""
        self.__cleanup()

    def __cleanup(self) -> None:
        """Clean up resources used by the station"""
        self._coms.end_read_loop()
        self._end_current_interval_send()

    @property
    @abstractmethod
    def abort(self) -> bool:
        """Station"""
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

    @property
    def last_sent_time(self) -> float | None:
        return self._last_sent_time

    @property
    def last_received_time(self) -> float | None:
        return self._last_received_time

    def _on_receive(self, new: ComsMessage) -> Any:
        """Callback for when a message is received
        
        :param new: The received message
        :type new: ComsMessage
        :return: Ignored return value
        :rtype: Any
        """
        ...

    def _on_send(self, new: ComsMessage) -> Any:
        """Callback for when a message is successfully sent
        
        :param new: The received message
        :type new: ComsMessage
        :return: Ignored return value
        :rtype: Any
        """
        ...

    def send(self, data: ParsableComType) -> bool:
        """Construct and send a ComsMessage from the provided object
        
        :param data: Object to send as a ComsMessage
        :type data: ParsableComType
        :return bool: wether or not sending the object was successful
        :rtype: bool
        """
        try:
            message = construct_message(data)
        except (TypeError, ComsMessageParseError):
            return False
        if self._coms.write(message, suppress_errors=True):
            self._on_send(message)
            self._last_sent = message
            self._start_new_interval_send()
            self._last_sent_time = time.time()
            return True
        return False

    def resend_last(self) -> None:
        if self._last_sent is not None:
            self._coms.write(self._last_sent, suppress_errors=True)
            self._on_send(self._last_sent)
        else:
            # FIXME: This should send an all empty state message
            logger.warning("No previous message sent to interval again on interval")

    def set_send_interval(self, interval: float | None) -> None:
        if interval is not None and not isinstance(interval, (int, float)):
            raise TypeError("Expected interval of type `float` or `None`")

        if interval is None:
            interval = 0.0
        elif interval < 0:
            raise ValueError("Send interval cannot be less than 0")

        if self._send_interval_time == interval:
            return

        self._end_current_interval_send()
        self._send_interval_time = interval
        self._start_new_interval_send()

    def _start_new_interval_send(self) -> None:
        self._end_current_interval_send()
        if self._send_interval_time != 0:
            self._send_interval_thread = _AutoSendOnInterval(
                self.resend_last, self._send_interval_time
            )
            self._send_interval_thread.start()

    def _end_current_interval_send(self) -> None:
        if self._send_interval_thread and self._send_interval_thread.is_alive():
            self._send_interval_thread.stop()

    def bind_queue(self, queue: Queueable | None) -> None:
        """Alias for bindQueue
        
        :param queue: Object to append messages to 
        :type queue: Queueable | None
        """
        return self.bindQueue(queue)

    def bindQueue(self, queue: Queueable | None) -> None:
        """Supply or remove reference to a queueable object

        The station will then try to append recieved messages to the
        supplied object, ot stop trying to append messages if the
        reference is to None.
        
        :param queue: Object to append messages to 
        :type queue: Queueable | None
        """
        self.queue = queue

    def getLaunchFlag(self) -> bool:
        """Alias to the ``launch`` property for backward compatibility
        
        :return: value of ``launch`` property
        :rtype: bool
        """
        return self.launch

    def getQDMFlag(self) -> bool:
        """Alias to the ``qdm`` property for backward compatibility
        
        :return: value of ``qdm`` property
        :rtype: bool
        """
        return self.qdm

    def getAbortFlag(self) -> bool:
        """Alias to the ``armed`` property for backward compatibility
        
        :return: value of ``armed`` property
        :rtype: bool
        """
        return self.abort

    def getStabFlag(self) -> bool:
        """Alias to the ``stab`` property for backward compatibility
        
        :return: value of ``stab`` property
        :rtype: bool
        """
        return self.stab

    def getArmedFlag(self) -> bool:
        """Alias to the ``armed`` property for backward compatibility
        
        :return: value of ``armed`` property
        :rtype: bool
        """
        return self.armed


class _AutoSendOnInterval(Thread):
    def __init__(
        self, resend_func: Callable[[], None], interval: float, *a: Any, **kw: Any
    ) -> None:
        super().__init__(*a, **kw)
        self.stop_event = Event()
        self.resend_func = resend_func
        self.interval = interval

    def run(self) -> None:
        while not self.stop_event.wait(self.interval):
            if not self.stop_event.is_set():
                self.resend_func()

    def stop(self, timeout: float | None = None) -> None:
        self.stop_event.set()
        self.join(timeout=timeout)


class Queueable(Protocol):
    """Protocol of type to be able to queue messages"""

    def append(self, t: Any) -> Any:
        ...
