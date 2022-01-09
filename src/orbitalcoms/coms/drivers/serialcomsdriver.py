import serial

from ..messages import ComsMessage, construct_message
from .basedriver import BaseComsDriver


class SerialComsDriver(BaseComsDriver):
    __ENCODING = "utf-8"

    def __init__(self, port: str, baudrate: int) -> None:
        super().__init__()
        self.__port = port
        self.__baudrate = baudrate
        self.ser = serial.Serial(port, baudrate)

    def _read(self) -> ComsMessage:
        msg = ""
        while True:
            c = self.ser.read().decode(encoding=self.__ENCODING, errors="ignore")
            if c == "&":
                return construct_message(msg)
            else:
                msg += c

    def _write(self, m: ComsMessage) -> None:
        self.ser.write(self._preprocess_write_msg(m))
        if self.ser.in_waiting:
            self.ser.flush()

    @classmethod
    def _preprocess_write_msg(cls, m: ComsMessage) -> bytes:
        return f"{m.as_str}&".encode(encoding=cls.__ENCODING)

    @property
    def port(self) -> str:
        return self.__port

    @property
    def baudrate(self) -> int:
        return self.__baudrate
