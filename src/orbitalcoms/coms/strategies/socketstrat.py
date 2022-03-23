from __future__ import annotations

import socket

from ..errors.errors import ComsDriverReadError, ComsDriverWriteError
from ..messages.message import ComsMessage, construct_message
from .strategy import ComsStrategy


class SocketComsStrategy(ComsStrategy):
    """Informs how to communicate over a socket"""

    __HEADER = 64
    __ENCODING = "utf-8"

    def __init__(self, socket: socket.socket) -> None:
        """Create a new ``SocketComsStrategy`` for a provided socket

        :param socket: Socket to read and write to
        :type socket: socket.socket
        """
        self.sock = socket

    @classmethod
    def accept_connection_at(
        cls, host: str = "", port: int = 5000
    ) -> SocketComsStrategy:
        """Create a socket and wait for a connection to communicate over

        :param host: IP address to accept a connection at
        :type host: str
        :param port: port to accept a connection at
        :type port: int
        :returns: A strategy to communicate over the newly made socket
        :rtype: SocketComsStrategy
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind((host, port))
            server.listen(0)
            conn, _ = server.accept()
        return cls(conn)

    @classmethod
    def connect_to(cls, host: str = "", port: int = 5000) -> SocketComsStrategy:
        """Create a socket and attempt to connect to peer to communicate with

        :param host: IP address to connect to
        :type host: str
        :param port: port to connect to
        :type port: int
        :returns: A strategy to communicate over the newly made socket
        :rtype: SocketComsStrategy
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return cls(sock)

    def read(self) -> ComsMessage:
        """Read bytes from the wrapped socket and attempt to construct a message

        :returns: Newly read message
        :rtype: ComsMessage
        """
        head = self.sock.recv(self.__HEADER).decode(encoding=self.__ENCODING)
        if not head:
            # FIXME: Need a more appropriate error here
            raise ComsDriverReadError(f"Invalid header received: '{head}'")
        return construct_message(
            self.sock.recv(int(head)).decode(encoding=self.__ENCODING)
        )

    def write(self, m: ComsMessage) -> None:
        """Turn a ComsMessage into bytes, construct a valid header and send over socket

        :param m: A message to write to the wrapped socket
        :type m: ComsMessage
        """
        msg = m.as_str.encode(encoding=self.__ENCODING)
        header = str(len(msg)).encode(self.__ENCODING)
        if len(header) > self.__HEADER:
            raise ComsDriverWriteError("Message too long to generate header")
        header += b" " * (self.__HEADER - len(header))
        self.sock.send(header)
        self.sock.send(msg)
