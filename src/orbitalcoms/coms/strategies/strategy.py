from abc import abstractmethod

from typing_extensions import Protocol

from ..messages.message import ComsMessage


class ComsStrategy(Protocol):
    """Protocol that informs how to read and write ``ComsMessages``
    to a particular source
    """

    @abstractmethod
    def read(self) -> ComsMessage:
        """Method that informs how to read ``ComsMessage``.

        This method can be blocking. It is very likely that this
        will invlove reading a str/bytes/json and constructing
        a ``ComsMessage`` from that.

        :returns: Newly read message
        :rtype: ComsMessage
        """
        ...

    @abstractmethod
    def write(self, m: ComsMessage) -> None:
        """Takes an already constructed ``ComsMessage`` and writes
        it to a source

        :param m: A message to write to source
        :type m: ComsMessage
        """
        ...
