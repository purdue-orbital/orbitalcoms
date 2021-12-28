from __future__ import annotations

from time import sleep
from typing import List, Set, Tuple

from ..messages import ComsMessage, ParsableComType, construct_message
from .basedriver import BaseComsDriver


class LocalComsDriver(BaseComsDriver):
    """
    Defined implimentation of BaseComsDriver for testing locally
    """

    def __init__(self) -> None:
        super().__init__()
        self._messages: List[str] = []
        self._listening: Set[LocalComsDriver] = set()

    def _read(self) -> ComsMessage:
        while True:
            if self._messages:
                return construct_message(self._messages.pop(0))

    def _write(self, m: ParsableComType) -> None:
        for li in self._listening:
            li._messages.append(construct_message(m).as_str)

    def listen_to(self, com: LocalComsDriver) -> None:
        com._listening.add(self)

    @staticmethod
    def link_local_coms(a: LocalComsDriver, b: LocalComsDriver) -> None:
        a.listen_to(b)
        b.listen_to(a)

    @classmethod
    def create_linked_coms(cls) -> Tuple[LocalComsDriver, LocalComsDriver]:
        a = cls()
        b = cls()
        cls.link_local_coms(a, b)
        return a, b
