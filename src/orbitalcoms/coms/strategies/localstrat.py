from __future__ import annotations

import multiprocessing as mp
import time
from typing import List, Set, Tuple

from ..messages import ComsMessage, construct_message
from .strategy import ComsStrategy


class LocalComsStrategy(ComsStrategy):
    """Basic communication stategy for testing on local machine"""

    def __init__(self) -> None:
        self._listening: Set[LocalComsStrategy] = set()

        # needs to be shared bc read is often in different proc than write
        self._messages: List[str] = mp.Manager().list()

    def read(self) -> ComsMessage:
        """Wait for and return a message placed in the
        stategies message list

        :returns: Latest messsage in the message list
        :rtype: ComsMessage
        """
        while True:
            if self._messages:
                return construct_message(self._messages.pop(0))
            time.sleep(0.2)

    def write(self, m: ComsMessage) -> None:
        """Place new message in all listening stategies message list

        :param m: A message to write to send to all listening strategies
        :type m: ComsMessage
        """
        for li in self._listening:
            li._messages.append(m.as_str)

    def listen_to(self, com: LocalComsStrategy) -> None:
        """Add a local strategy set of strategies to send
        ComsMessgaes to

        :param com: A local strategy to send messages to
        :type com: LocalComsStrategy
        """
        com._listening.add(self)


def get_linked_local_strats() -> Tuple[LocalComsStrategy, LocalComsStrategy]:
    """Helper function to create two local strategies for
    testing purposes

    NOTE: ``LocalComsStrategy``s are just for tetsing. As such
    this function should not be exported in __init__.py

    :returns: Linked local strategies
    :rtype: Tuple[LocalComsStrategy, LocalComsStrategy]
    """
    a = LocalComsStrategy()
    b = LocalComsStrategy()
    a.listen_to(b)
    b.listen_to(a)
    return a, b
