from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Dict, Type

from typing_extensions import Protocol

from orbitalcoms import ComsMessageParseError

from ..coms import (
    ComsDriver,
    ComsMessage,
    ComsSubscription,
    ParsableComType,
    construct_message,
)


class Station(ABC):
    def __init__(self, coms: ComsDriver):
        self._coms = coms

        self._last_sent: ComsMessage | None = None
        self._last_received: ComsMessage | None = None
        self._last_data: Dict[str, Any] | None = None

        self.queue: Queueable | None = None

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
        """Deconstruct Station"""
        self.__cleanup()

    def __cleanup(self) -> None:
        """Clean up resources used by the station"""
        self._coms.end_read_loop()

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
            return True
        return False

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


class Queueable(Protocol):
    """Protocol of type to be able to queue messages"""

    def append(self, t: Any) -> Any:
        ...
