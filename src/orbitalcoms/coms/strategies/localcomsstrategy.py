from __future__ import annotations

import multiprocessing as mp
import time
from typing import List, Set, Tuple

from ..messages import ComsMessage, construct_message
from .strategy import ComsStrategy


class LocalComsStrategy(ComsStrategy):
    def __init__(self) -> None:
        self._listening: Set[LocalComsStrategy] = set()

        # needs to be shared bc read is in different proc than write
        self._messages: List[str] = mp.Manager().list()

    def read(self) -> ComsMessage:
        while True:
            if self._messages:
                return construct_message(self._messages.pop(0))
            time.sleep(0.2)

    def write(self, m: ComsMessage) -> None:
        for li in self._listening:
            li._messages.append(m.as_str)

    def listen_to(self, com: LocalComsStrategy) -> None:
        com._listening.add(self)


def get_linked_local_strats() -> Tuple[LocalComsStrategy, LocalComsStrategy]:
    """Helper for testing"""
    # NOTE: Do not export in __init__.py, just for tetsing
    a = LocalComsStrategy()
    b = LocalComsStrategy()
    a.listen_to(b)
    b.listen_to(a)
    return a, b
