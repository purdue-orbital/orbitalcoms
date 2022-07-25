import argparse
from typing import cast

from typing_extensions import Protocol

import orbitalcoms._app.headless as headless
import orbitalcoms._app.tkgui as tkgui
from orbitalcoms.coms.drivers import ComsDriver
from orbitalcoms.coms.strategies import SerialComsStrategy, SocketComsStrategy
from orbitalcoms.stations.groundstation import GroundStation


class BaseArgs(Protocol):
    """Base args that apply to launching orbitalcoms"""

    frontend: str
    interval_send: int
    connection: str


class SocketArgs(BaseArgs, Protocol):
    """Arguments needed for launching orbitalcoms
    with the socket strategy
    """

    host: str
    port: int


class SerialArgs(BaseArgs, Protocol):
    """Arguments needed for launching orbitalcoms
    with the serial strategy
    """

    port: str
    baudrate: int


def main() -> None:
    """Main funcion for launcheing the application"""

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

    with GroundStation(coms) as gs:
        gs.set_send_interval(args.interval_send)
        if args.frontend == "dev":
            tkgui.run_app(gs)
        elif args.frontend == "headless":
            headless.run_app(gs)
        else:
            raise ValueError("Failed to find selected frontend")


def get_args() -> BaseArgs:
    """Collect command line arguments

    :return: An object with the cli arguments needed to run orbitalcoms
    :rtype: BaseArgs
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frontend",
        "-f",
        help="The frontend used for to dispaling ground sation information",
        default="dev",
        type=str,
    )
    parser.add_argument(
        "--interval-send",
        "-i",
        help="number of seconds before auto-resending the latest message",
        default=0,
        type=int,
    )
    subparsers = parser.add_subparsers(
        title="Connection",
        dest="connection",
        description="Determines the communications strategy used by the ground station",
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
        help="Serial port to use",
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
