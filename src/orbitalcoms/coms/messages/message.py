from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Any, Dict, Union

from ..errors.errors import ComsMessageParseError


@dataclass(frozen=True)
class ComsMessage:
    """Message Specs to be sent by Coms"""

    ABORT: int
    QDM: int
    STAB: int
    LAUNCH: int
    ARMED: int | None = None
    DATA: Dict[str, Any] | None = None

    @classmethod
    def from_string(cls, s: str) -> ComsMessage:
        return cls(**json.loads(s))

    def __getitem__(self, _item: str) -> Any:
        return self.as_dict[_item]

    @property
    def as_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @property
    def as_str(self) -> str:
        return json.dumps(self.as_dict)


ParsableComType = Union[ComsMessage, str, dict]


def construct_message(m: ParsableComType) -> ComsMessage:
    try:
        if isinstance(m, ComsMessage):
            return m
        if isinstance(m, str):
            return ComsMessage.from_string(m)
        if isinstance(m, dict):
            return ComsMessage.from_string(json.dumps(m))
    except Exception as e:
        raise ComsMessageParseError(f"Failed to parse ComsMessage from {m}") from e
    raise TypeError(f"Cannot construct a Coms message from type: {type(m)}")
