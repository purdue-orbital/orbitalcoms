from __future__ import annotations
from typing import cast

import serial

from ..messages import ComsMessage, construct_message
from .basedriver import BaseComsDriver, ComsStrategy


class SerialComsDriver(BaseComsDriver):
    def __init__(self, port: str, baudrate: int) -> None:
        super().__init__(SerialComsStartegy.from_args(port, baudrate))

    @property
    def port(self) -> str:
        # TODO: Remove
        return str(cast(SerialComsStartegy, self.strategy).ser.port)

    @property
    def baudrate(self) -> int:
        # TODO: Remove
        return int(cast(SerialComsStartegy, self.strategy).ser.baudrate)

    @staticmethod
    def _preprocess_write_msg(m: ComsMessage) -> bytes:
        # TODO: Remove
        return SerialComsStartegy._preprocess_write_msg(m)


class SerialComsStartegy(ComsStrategy):
    __ENCODING = "utf-8"

    def __init__(self, serial: serial.Serial) -> None:
        self.ser = serial

    @classmethod
    def from_args(cls, port: str, baudrate: int) -> SerialComsStartegy:
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
