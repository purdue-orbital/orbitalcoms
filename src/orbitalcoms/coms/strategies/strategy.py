from typing_extensions import Protocol

from ..messages.message import ComsMessage


class ComsStrategy(Protocol):
    def read(self) -> ComsMessage:
        ...

    def write(self, m: ComsMessage) -> None:
        ...
