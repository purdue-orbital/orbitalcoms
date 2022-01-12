from __future__ import annotations

import multiprocessing as mp
import time
from typing import List, Set, Tuple

from ..messages import ComsMessage, construct_message
from .basedriver import BaseComsDriver, ComsStrategy


class LocalComsDriver(BaseComsDriver):
    """
    Defined implimentation of BaseComsDriver for testing locally
    """

    def __init__(self, strategy: ComsStrategy | None = None) -> None:
        if strategy:
            super().__init__(strategy)
        else:
            super().__init__(LocalComsStrategy())

    @classmethod
    def create_linked_coms(cls) -> Tuple[LocalComsDriver, LocalComsDriver]:
        # TODO: Remove
        a = LocalComsStrategy()
        b = LocalComsStrategy()
        link_local_coms(a, b)
        return LocalComsDriver(a), LocalComsDriver(b)


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


def link_local_coms(a: LocalComsStrategy, b: LocalComsStrategy) -> None:
    a.listen_to(b)
    b.listen_to(a)
