from __future__ import annotations

import socket

from ..errors import ComsDriverReadError, ComsDriverWriteError
from ..messages import ComsMessage, ParsableComType, construct_message
from .basedriver import BaseComsDriver


class SocketComsDriver(BaseComsDriver):
    __HEADER = 64

    def __init__(self, sock: socket.socket) -> None:
        super().__init__()
        self._sock = sock

    @classmethod
    def accept_connection_at(cls, host: str = "", port: int = 5000) -> SocketComsDriver:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((host, port))
            server.listen(0)
            conn, _ = server.accept()
        return cls(conn)

    @classmethod
    def connect_to(cls, host: str = "", port: int = 5000) -> SocketComsDriver:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return cls(sock)

    def _read(self) -> ComsMessage:
        head = self._sock.recv(self.__HEADER).decode()
        if not head:
            raise ComsDriverReadError(f"Invalid header recieved: '{head}'")
        try:
            msg = self._sock.recv(int(head)).decode()
            return ComsMessage.from_string(msg)
        except Exception as e:
            raise ComsDriverReadError(f"Invalid message recieved: '{msg}'") from e

    def _write(self, m: ParsableComType) -> None:
        msg = construct_message(m).as_str.encode()
        header = str(len(msg)).encode()
        if len(header) > self.__HEADER:
            raise ComsDriverWriteError("Message too long to generate header")
        header += b" " * (self.__HEADER - len(header))
        self._sock.send(header)
        self._sock.send(msg)
