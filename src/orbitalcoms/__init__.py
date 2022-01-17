import sys

from .coms import (
    ComsDriver,
    ComsDriverReadError,
    ComsDriverWriteError,
    ComsMessage,
    ComsMessageParseError,
    ComsSubscription,
    LocalComsStrategy,
    OneTimeComsSubscription,
    SerialComsStrategy,
    SocketComsStrategy,
    construct_message,
)
from .stations import (
    GroundStation,
    LaunchStation,
    Station,
    create_serial_ground_station,
    create_serial_launch_station,
    create_socket_ground_station,
    create_socket_luanch_station,
)

if sys.version_info < (3, 7):
    sys.exit("Python 3.7 or greater must be used with orbitalcoms.")

__all__ = [
    "ComsDriver",
    "ComsDriverReadError",
    "ComsDriverWriteError",
    "ComsMessage",
    "ComsMessageParseError",
    "ComsSubscription",
    "LocalComsStrategy",
    "OneTimeComsSubscription",
    "SerialComsStrategy",
    "SocketComsStrategy",
    "construct_message",
    "GroundStation",
    "LaunchStation",
    "Station",
    "create_socket_luanch_station",
    "create_socket_ground_station",
    "create_serial_ground_station",
    "create_serial_launch_station",
]
