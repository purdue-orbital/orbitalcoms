"""Convience functions for creating stations with with completed
dependency injection
"""

from ..coms.drivers import ComsDriver
from ..coms.strategies import SerialComsStrategy, SocketComsStrategy
from .groundstation import GroundStation
from .launchstation import LaunchStation


def create_socket_launch_station(
    host: str = "127.0.1.1", port: int = 5000
) -> LaunchStation:
    """Convinence function for creating a Launch Station
    that communicates using a socket connection

    :param host: The IP address of the host
    :type host: str
    :param port: port to connect to
    :type port: int
    :returns: Launch station communicating on a socket
    :rtype: LaunchStation
    """
    return LaunchStation(
        ComsDriver(SocketComsStrategy.accept_connection_at(host, port))
    )


def create_socket_ground_station(
    host: str = "127.0.1.1", port: int = 5000
) -> GroundStation:
    """Convinence function for creating a Ground Station
    that communicates using a socket connection

    :param host: The IP address of the host
    :type host: str
    :param port: port to connect to
    :type port: int
    :returns: Ground station communicating on a socket
    :rtype: GroundStation
    """
    return GroundStation(ComsDriver(SocketComsStrategy.connect_to(host, port)))


def create_serial_launch_station(port: str, baudrate: int) -> LaunchStation:
    """Convinence function for creating a Launch Station
    that communicates using a serial port

    :param port: Port to use for serial connection
    :type port: str
    :param baudrate: Baudrate for the connection
    :type baudrate: int
    :returns: Launch station communicating on given port
    :rtype: LaunchStation
    """
    return LaunchStation(ComsDriver(SerialComsStrategy.from_args(port, baudrate)))


def create_serial_ground_station(port: str, baudrate: int) -> GroundStation:
    """Convinence function for creating a Ground Station
    that communicates using a serial port

    :param port: Port to use for serial connection
    :type port: str
    :param baudrate: Baudrate for the connection
    :type baudrate: int
    :returns: Ground station communicating on given port
    :rtype: GroundStation
    """
    return GroundStation(ComsDriver(SerialComsStrategy.from_args(port, baudrate)))
