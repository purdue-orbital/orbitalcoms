from __future__ import annotations

import serial

from ..messages import ComsMessage, construct_message
from .strategy import ComsStrategy


class SerialComsStrategy(ComsStrategy):
    """Informs how to communicate over a serial port"""

    __ENCODING = "utf-8"

    def __init__(self, serial: serial.Serial) -> None:
        """Create a new ``SerialComsStrategy`` for a provided socket

        :param serial: serial connection to read and write to
        :type serial: serial.Serial
        """
        self.ser = serial

    @classmethod
    def from_args(cls, port: str, baudrate: int) -> SerialComsStrategy:
        """Construct and wrap a serial connection in a ``SerialComsStrategy``

        :param port: Serial port on which to communitcate
        :type port: str
        :param buadrate: buadrate with which to communitcate
        :type baudrate: int
        :returns: The statrategy to communicate over the new serial connection
        :rtype: SerialComsStrategy
        """
        return cls(serial.Serial(port=port, baudrate=baudrate))

    def read(self) -> ComsMessage:
        """Read bytes from the wrapped serial connection and attempt
        to construct a message

        :returns: Newly read message
        :rtype: ComsMessage
        """
        msg = ""
        while True:
            c = self.ser.read().decode(encoding=self.__ENCODING, errors="ignore")
            if c == "&":
                return construct_message(msg)
            else:
                msg += c

    def write(self, m: ComsMessage) -> None:
        """Turn a ComsMessage into bytes, format them and send over the wrapped
        serial connection

        :param m: A message to write to the wrapped socket
        :type m: ComsMessage
        """
        self.ser.write(self._preprocess_write_msg(m))
        if self.ser.in_waiting:
            self.ser.flush()

    @classmethod
    def _preprocess_write_msg(cls, m: ComsMessage) -> bytes:
        """Convience function to turn Coms message into formatted bytes

        :param m: A message to format
        :type m: ComsMessage
        :returns: A formated bytes representation the message
        :rtype: bytes
        """
        return f"{m.as_str}&".encode(encoding=cls.__ENCODING)
