from __future__ import annotations

import socket

from ..errors.errors import ComsDriverReadError, ComsDriverWriteError
from ..messages.message import ComsMessage, construct_message
from .strategy import ComsStrategy


class SocketComsStrategy(ComsStrategy):
    __HEADER = 64
    __ENCODING = "utf-8"

    def __init__(self, socket: socket.socket) -> None:
        self.sock = socket

    @classmethod
    def accept_connection_at(
        cls, host: str = "", port: int = 5000
    ) -> SocketComsStrategy:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((host, port))
            server.listen(0)
            conn, _ = server.accept()
        return cls(conn)

    @classmethod
    def connect_to(cls, host: str = "", port: int = 5000) -> SocketComsStrategy:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return cls(sock)

    def read(self) -> ComsMessage:
        head = self.sock.recv(self.__HEADER).decode(encoding=self.__ENCODING)
        if not head:
            raise ComsDriverReadError(f"Invalid header received: '{head}'")
        return construct_message(
            self.sock.recv(int(head)).decode(encoding=self.__ENCODING)
        )

    def write(self, m: ComsMessage) -> None:
        msg = m.as_str.encode(encoding=self.__ENCODING)
        header = str(len(msg)).encode(self.__ENCODING)
        if len(header) > self.__HEADER:
            raise ComsDriverWriteError("Message too long to generate header")
        header += b" " * (self.__HEADER - len(header))
        self.sock.send(header)
        self.sock.send(msg)
