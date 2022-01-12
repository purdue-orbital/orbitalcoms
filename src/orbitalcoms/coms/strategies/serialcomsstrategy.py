from __future__ import annotations

import serial

from ..drivers.basedriver import ComsStrategy
from ..messages import ComsMessage, construct_message


class SerialComsStrategy(ComsStrategy):
    __ENCODING = "utf-8"

    def __init__(self, serial: serial.Serial) -> None:
        self.ser = serial

    @classmethod
    def from_args(cls, port: str, baudrate: int) -> SerialComsStrategy:
        return cls(serial.Serial(port=port, baudrate=baudrate))

    def read(self) -> ComsMessage:
        msg = ""
        while True:
            c = self.ser.read().decode(encoding=self.__ENCODING, errors="ignore")
            if c == "&":
                return construct_message(msg)
            else:
                msg += c

    def write(self, m: ComsMessage) -> None:
        self.ser.write(self._preprocess_write_msg(m))
        if self.ser.in_waiting:
            self.ser.flush()

    @classmethod
    def _preprocess_write_msg(cls, m: ComsMessage) -> bytes:
        return f"{m.as_str}&".encode(encoding=cls.__ENCODING)
