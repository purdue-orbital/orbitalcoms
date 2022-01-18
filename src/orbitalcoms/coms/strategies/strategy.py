from abc import abstractmethod

from typing_extensions import Protocol

from ..messages.message import ComsMessage


class ComsStrategy(Protocol):
    @abstractmethod
    def read(self) -> ComsMessage:
        ...

    @abstractmethod
    def write(self, m: ComsMessage) -> None:
        ...
