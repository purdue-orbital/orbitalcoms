import json

import serial

from ..messages import ComsMessage, ParsableComType, construct_message
from .basedriver import BaseComsDriver


class SerialComsDriver(BaseComsDriver):
    def __init__(self, port: str, baudrate: int) -> None:
        self.__port = port
        self.__baudrate = baudrate
        self.ser = serial.Serial(port, baudrate)

    def _read(self) -> ComsMessage:
        msg = ""
        while True:
            c = self.ser.read().decode(errors="ignore")
            if c == "&":
                try:
                    return ComsMessage.from_string(msg)
                except Exception:
                    print(f"Invalid Messge Recieved: {msg}")
                finally:
                    msg = ""
            else:
                msg += c

    def _write(self, msg: ParsableComType) -> None:
        m = construct_message(msg)
        self.ser.write(f"{json.dumps(m.as_dict)}&".encode())
        self.ser.flush()

    @property
    def port(self) -> str:
        return self.__port

    @property
    def baudrate(self) -> int:
        return self.__baudrate
