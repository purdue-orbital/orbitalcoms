import socket

from .basedriver import BaseComsDriver
from ..messages import ComsMessage, construct_message, ParsableComType


class SocketComsDriver(BaseComsDriver):
    def __init__(self) -> None:
        super().__init__()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def accept_connection(self):
        self._sock.listen(1)
        con, addr = self._sock.accept()

    def connect_to(self):
        ...
