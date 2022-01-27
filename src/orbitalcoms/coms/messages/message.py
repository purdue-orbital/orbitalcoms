from __future__ import annotations
from xmlrpc.client import Boolean

#import dataclasses
from attrs import define, frozen, asdict, validators, field
import json
from dataclasses import dataclass
from typing import Any, Dict, Union

from ..errors.errors import ComsMessageParseError


#@dataclass(frozen=True)
@define(frozen=True)
class ComsMessage:
    """Message Specs to be sent by Coms"""

    ABORT: int = field()
    QDM: int = field()
    STAB: int = field()
    LAUNCH: int = field()
    ARMED: int | None = None
    DATA: Dict[str, Any] | None = None
    
    # TODO: ARMED and DATA are not validated.
    # TODO: I don't think any tests currently exist to test the following validators.

    @ABORT.validator
    def check(self, attribute, value):
        if not (type(self.ABORT) == Boolean or type(self.ABORT) == int):
            raise TypeError("ABORT must be either a Boolean or an int")
    
    @QDM.validator
    def check(self, attribute, value):
        if not (type(self.QDM) == Boolean or type(self.QDM) == int):
            raise TypeError("QDM must be either a Boolean or an int")
    
    @STAB.validator
    def check(self, attribute, value):
        if not (type(self.STAB) == Boolean or type(self.STAB) == int):
            raise TypeError("STAB must be either a Boolean or an int")
    
    @LAUNCH.validator
    def check(self, attribute, value):
        if not (type(self.LAUNCH) == Boolean or type(self.LAUNCH) == int):
            raise TypeError("LAUNCH must be either a Boolean or an int")
    
    @classmethod
    def from_string(cls, s: str) -> ComsMessage:
        return cls(**json.loads(s))

    def __getitem__(self, _item: str) -> Any:
        return self.as_dict[_item]

    @property
    def as_dict(self) -> Dict[str, Any]:
        #return dataclasses.asdict(self)
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
    except Exception as e:
        raise ComsMessageParseError(f"Failed to parse ComsMessage from {m}") from e
    raise TypeError(f"Cannot construct a Coms message from type: {type(m)}")
