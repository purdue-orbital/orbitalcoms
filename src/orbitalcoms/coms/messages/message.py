from __future__ import annotations

import json
from typing import Any, Dict, Union

from attrs import asdict, define, field

from ..errors.errors import ComsMessageParseError


def _intbool_to_int(val: int | bool) -> int:
    """Convenience method to convert int or bool to int

    Boolean True converts to 1. Boolean False converts to 0
    Int is converted to itself.

    :param val: Value to convert to int
    :type val: int | bool
    :return: Converted value to int
    :rtype: int
    """
    if isinstance(val, (int, bool)):
        return int(val)
    raise TypeError("Value is not a valid type! (Expected int or bool)")


def _armed_intbool_to_int(val: int | bool | None) -> int | None:
    """Convenience method to convert int, bool, or None to int or None

    Boolean True converts to 1. Boolean False converts to 0.
    None is converted to None.
    Int is converted to itself.

    :param val: Value to convert to int
    :type val: int | bool | None
    :return: Converted value to int or None
    :rtype: int | None
    """
    if val is not None:
        return _intbool_to_int(val)
    return None


@define(frozen=True)
class ComsMessage:
    """Outline of a message to be sent via orbitalcoms

    ComsMessages utilizes attr's dataclasses to allow for simple
    type conversion and data validation. These messages are what
    are converted and sent across ComsDrivers to facilitate
    communication between Stations.

    All messages must contain the following fields:

    - ``ABORT``: State of the abort procedure
    - ``QDM``: State of the the QDM Procedure
    - ``STAB``: State of the stabilization system
    - ``LAUNCH``: State of the launch procedure

    Messages may additionally contain the following fields:

    - ``ARMED``: State of whether or not the mission is armed
    - ``DATA``: Additional information to attach to the message

    All fields are represented as integers with the notable
    exception of ``DATA`` which is a dict of strings to
    value of any type (though they should be seializable)
    """

    ABORT: int = field(converter=_intbool_to_int)
    QDM: int = field(converter=_intbool_to_int)
    STAB: int = field(converter=_intbool_to_int)
    LAUNCH: int = field(converter=_intbool_to_int)
    ARMED: int | None = field(default=None, converter=_armed_intbool_to_int)
    DATA: Dict[str, Any] | None = field(default=None)

    @DATA.validator
    def check_data(self, attribute: str, value: Any) -> None:
        """Ensure that data being attached to the ComsMessage is a dict or None

        :param attribute: Name of the atribute (i.e. "DATA")
        :type attribute: str
        :param value: Value to set to DATA
        :type value: Any
        """
        if not (isinstance(self.DATA, dict) or self.DATA is None):
            raise TypeError("DATA must be either a Dict or None")

    @classmethod
    def from_string(cls, s: str) -> ComsMessage:
        """Construct a ComsMessage from a JSON-like string

        :param s: A JSON-like string
        :type s: str
        :return: Constructed ComsMessage
        :rtype: ComsMessage
        """
        return cls(**json.loads(s))

    def __getitem__(self, _item: str) -> Any:
        """Access the atributes through square brackets

        Example:

        .. highlight:: python
        .. code-block:: python

            c = ComsMessage(
                ABORT = 0,
                QDM = 0,
                STAB = 1,
                LAUNCH = 0,
                ARMED = 1,
            )
            c["STAB"]  # Returns 1
            c["QDM"]   # Returns 0

        :param _item: Name of the attribute to retrieve
        :type _item: str
        :return: The value of the attribute
        :rtype: Any
        """
        return self.as_dict[_item]

    @property
    def as_dict(self) -> Dict[str, Any]:
        """Retrive the ComsMessage as a dictionary

        Attributes of the ComsMessage are keys in the dictionary

        :return: Dictionary representation of the ComsMessage
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @property
    def as_str(self) -> str:
        """Retrive the ComsMessage as a JSON-like string

        :return: String representation of the ComsMessage
        :rtype: Dict[str, Any]
        """
        return json.dumps(self.as_dict)


# Type alias used for convenience throughout codebase
ParsableComType = Union[ComsMessage, str, dict]


def construct_message(m: ParsableComType) -> ComsMessage:
    """Convenience method to construct and return ComsMessage

    :param m: Object from which to construct a ComsMessage
    :type m: ParsableComType
    :return: Constructed ComsMessage
    :rtype: ComsMessage
    """
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
