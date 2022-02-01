from __future__ import annotations

import json
from typing import Any, Dict, Union
from xmlrpc.client import Boolean

# import dataclasses
from attrs import asdict, define, field

from ..errors.errors import ComsMessageParseError


# @dataclass(frozen=True)
@define(frozen=True)
class ComsMessage:
    """Message Specs to be sent by Coms"""

    ABORT: int = field()
    QDM: int = field()
    STAB: int = field()
    LAUNCH: int = field()
    ARMED: int | None = field(default=None)
    DATA: Dict[str, Any] | None = field(default=None)

    # TODO: resolve booleans to int, rather than simply accepting them

    @ABORT.validator
    def check_abort(self, attribute: str, value: Any) -> None:
        if not (type(self.ABORT) == Boolean or type(self.ABORT) == int):
            raise TypeError("ABORT must be either a Boolean or an int")
        # if (type(self.ABORT) == Boolean):
        #    self.ABORT = 1

    @QDM.validator
    def check_qdm(self, attribute: str, value: Any) -> None:
        if not (type(self.QDM) == Boolean or type(self.QDM) == int):
            raise TypeError("QDM must be either a Boolean or an int")
        # if (type(self.QDM) == Boolean):
        #    self.QDM = 1

    @STAB.validator
    def check_stab(self, attribute: str, value: Any) -> None:
        if not (type(self.STAB) == Boolean or type(self.STAB) == int):
            raise TypeError("STAB must be either a Boolean or an int")
        # if (type(self.STAB) == Boolean):
        #    self.STAB = 1

    @LAUNCH.validator
    def check_launch(self, attribute: str, value: Any) -> None:
        if not (type(self.LAUNCH) == Boolean or type(self.LAUNCH) == int):
            raise TypeError("LAUNCH must be either a Boolean or an int")
        # if (type(self.LAUNCH) == Boolean):
        #    self.LAUNCH = 1

    @ARMED.validator
    def check_armed(self, attribute: str, value: Any) -> None:
        if not (
            type(self.ARMED) == Boolean or type(self.ARMED) == int or self.ARMED is None
        ):
            raise TypeError("ARMED must be either a Boolean, an int, or None")
        # if (type(self.ARMED) == Boolean):
        #    self.ARMED = 1

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
