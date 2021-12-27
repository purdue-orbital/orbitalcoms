from __future__ import annotations

import socket

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
            server.listen(1)
            conn, _ = server.accept()
        return cls(conn)

    @classmethod
    def connect_to(cls, host: str = "", port: int = 5000) -> SocketComsDriver:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return cls(sock)
