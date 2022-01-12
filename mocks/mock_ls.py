import argparse
import random
import sys
import threading as th
import time
from typing import List

from orbitalcoms import (
    ComsMessage,
    LaunchStation,
    create_serial_launch_station,
    create_socket_luanch_station,
)


def main() -> int:
    args = get_args()

    if args.connection == "socket":
        print(f"HOST: {args.host} | PORT: {args.port}")
        ls = create_socket_luanch_station(args.host, args.port)
        print("Connect to Ground Station")
    elif args.connection == "serial":
        print(f"PORT: {args.port} | BAUDRATE: {args.baudrate}")
        ls = create_serial_launch_station(args.port, args.baudrate)
    else:
        print("Connection type not implimented")
        return 123

    q: List[ComsMessage] = []
    ls.bind_queue(q)
    time.sleep(1)

    sending_thread = th.Thread(target=send_radio_state, args=(ls,), daemon=True)
    sending_thread.start()

    no_errs = True
    while no_errs:
        while len(q):
            msg = q.pop(0)
            print(
                (
                    "===============================\n"
                    "Received New Message:\n"
                    "===============================\n"
                    f"ARMED:  {msg.ARMED}\n"
                    f"ABORT:  {msg.ABORT}\n"
                    f"QDM:    {msg.QDM}\n"
                    f"STAB:   {msg.STAB}\n"
                    f"LAUNCH: {msg.LAUNCH}\n"
                    "===============================\n"
                )
            )
        if not sending_thread.is_alive():
            no_errs = False
        time.sleep(args.delay if args.delay > 0 else 1)

    return 0


def send_radio_state(ls: LaunchStation) -> None:
    while True:
        if not ls.send(
            {
                "LAUNCH": ls.getLaunchFlag(),
                "QDM": ls.getQDMFlag(),
                "ABORT": ls.getAbortFlag(),
                "STAB": ls.getStabFlag(),
                "ARMED": ls.getArmedFlag(),
                "DATA": {
                    "origin": "balloon",
                    "GPS": {
                        "long": random.uniform(0, 1),
                        "lat": random.uniform(0, 1),
                        "alt": random.uniform(0, 1),
                    },
                    "gyro": {
                        "x": random.uniform(0, 1),
                        "y": random.uniform(0, 1),
                        "z": random.uniform(0, 1),
                    },
                    "temp": random.uniform(0, 1),
                    "acc": {
                        "x": random.uniform(0, 1),
                        "y": random.uniform(0, 1),
                        "z": random.uniform(0, 1),
                    },
                },
            }
        ):
            raise Exception("Sending thread failed to send radio state")
        time.sleep(2)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--delay",
        "-d",
        help="Time delay between checking queue for state change",
        default=1,
        type=int,
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

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
