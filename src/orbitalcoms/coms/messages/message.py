from __future__ import annotations

import json
from typing import Any, Dict, Union

# import dataclasses
from attrs import asdict, define, field

from ..errors.errors import ComsMessageParseError


def _intbool_to_int(val: int | bool) -> int:
    # not sure why it doesn't work when under the ComsMessage class
    if isinstance(val, (int, bool)):
        return int(val)
    raise TypeError("Value is not a valid type! (Expected int or bool)")


def _armed_intbool_to_int(val: int | bool | None) -> int | None:
    if val is not None:
        return _intbool_to_int(val)
    return None


# @dataclass(frozen=True)
@define(frozen=True)
class ComsMessage:
    """Message Specs to be sent by Coms"""

    ABORT: int = field(converter=_intbool_to_int)
    QDM: int = field(converter=_intbool_to_int)
    STAB: int = field(converter=_intbool_to_int)
    LAUNCH: int = field(converter=_intbool_to_int)
    ARMED: int | None = field(default=None, converter=_armed_intbool_to_int)
    DATA: Dict[str, Any] | None = field(default=None)

    @DATA.validator
    def check_data(self, attribute: str, value: Any) -> None:
        if not (type(self.DATA) == dict or self.DATA is None):
            raise TypeError("DATA must be either a Dict or None")

    @classmethod
    def from_string(cls, s: str) -> ComsMessage:
        return cls(**json.loads(s))

    def __getitem__(self, _item: str) -> Any:
        return self.as_dict[_item]

    @property
    def as_dict(self) -> Dict[str, Any]:
        # return dataclasses.asdict(self)
        return asdict(self)

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
    except TypeError:
        raise
    except Exception as e:
        raise ComsMessageParseError(f"Failed to parse ComsMessage from {m}") from e
    raise TypeError(f"Cannot construct a Coms message from type: {type(m)}")
