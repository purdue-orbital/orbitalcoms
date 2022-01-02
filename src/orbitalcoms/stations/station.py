from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol

from ..coms import (
    BaseComsDriver,
    ComsMessage,
    ComsSubscription,
    ParsableComType,
    construct_message,
)


class Station(ABC):
    def __init__(self, coms: BaseComsDriver):
        self._coms = coms

        self._last_sent: ComsMessage | None = None
        self._last_recieved: ComsMessage | None = None
        self._last_data: Dict[str, Any] | None = None

        self.queue: Queueable | None = None

        def recieve(message: ComsMessage) -> None:
            self._on_receive(message)
            self._last_recieved = message
            if self.queue is not None:
                self.queue.append(message)

        self._coms.register_subscriber(ComsSubscription(recieve))
        self._coms.start_read_loop()

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
    def last_recieved(self) -> ComsMessage | None:
        return self._last_recieved

    def _on_receive(self, new: ComsMessage) -> Any:
        ...

    def _on_send(self, new: ComsMessage) -> Any:
        ...

    def send(self, data: ParsableComType) -> bool:
        try:
            message = construct_message(data)
        except Exception:
            return False
        if self._coms.write(message, suppress_errors=True):
            self._on_send(message)
            self._last_sent = message
            return True
        return False

    def bind_queue(self, queue: Queueable) -> None:
        """Alias for bindQueue"""
        return self.bindQueue(queue)

    def bindQueue(self, queue: Queueable) -> None:
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


class Queueable(Protocol):
    """Class able to queue messages"""

    def append(self, t: Any) -> Any:
        ...
