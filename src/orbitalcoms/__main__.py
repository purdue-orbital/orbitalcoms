import argparse
from typing import cast

from typing_extensions import Protocol

import orbitalcoms._app.tkgui as tkgui
from orbitalcoms.coms.drivers import ComsDriver
from orbitalcoms.coms.strategies import SerialComsStrategy, SocketComsStrategy
from orbitalcoms.stations.groundstation import GroundStation


class BaseArgs(Protocol):
    frontend: str
    connection: str


class SocketArgs(BaseArgs, Protocol):
    host: str
    port: int


class SerialArgs(BaseArgs, Protocol):
    port: str
    baudrate: int


def main() -> None:
    args = get_args()
    if args.connection == "socket":
        args = cast(SocketArgs, args)
        coms = ComsDriver(SocketComsStrategy.connect_to(host=args.host, port=args.port))
    elif args.connection == "serial":
        args = cast(SerialArgs, args)
        coms = ComsDriver(
            SerialComsStrategy.from_args(port=args.port, baudrate=args.baudrate)
        )
    else:
        raise ValueError("Could not determine how to manage communication")

    if args.frontend == "dev":
        tkgui.run_app(GroundStation(coms))
    else:
        raise ValueError("Failed to find selected frontend")


def get_args() -> BaseArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frontend",
        "-f",
        help="The forntend used for to dispaling groundsationinformation",
        default="dev",
        type=str,
    )
    subparsers = parser.add_subparsers(
        title="Connection",
        dest="connection",
        description="Determines the comunications strategy used by the Mock Launch Station",
        required=True,
        help="Available connection types",
    )

    # SOCKET ARGS
    socket = subparsers.add_parser("socket")
    socket.add_argument(
        "--host",
        "-o",
        help="IP address to host connection",
        default="127.0.1.1",
        type=str,
    )
    socket.add_argument(
        "--port", "-p", help="Port to allow connections", default=5000, type=int
    )

    # SERIAL ARGS
    serial = subparsers.add_parser("serial")
    serial.add_argument(
        "--port",
        "-p",
        help="Serial port to send data to",
        default="/dev/ttyUSB0",
        type=str,
    )
    serial.add_argument(
        "--baudrate",
        "-b",
        help="Baudrate with which to send data",
        default=9600,
        type=int,
    )

    return cast(BaseArgs, parser.parse_args())


if __name__ == "__main__":
    main()
