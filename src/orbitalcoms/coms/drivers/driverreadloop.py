from __future__ import annotations

import logging
import multiprocessing as mp
import traceback
from multiprocessing.connection import Connection
from threading import Event, Thread
from typing import TYPE_CHECKING, Any, Callable, Tuple

from ..._utils import log

if TYPE_CHECKING:
    from ..messages import ComsMessage
    from ..strategies.strategy import ComsStrategy

logger = log.make_logger(__name__, logging.ERROR)


class ComsDriverReadLoop(Thread):
    """The ComsDriverReadLoop is a thread that can be spawned by a
    ComsDriver that is responsible for listening for and reacting
    to new messages. This allows a ComsDriver to read and write
    ComsMessages without either proccess blocking eachother.

    It is able to  do this by taking a reference to a ComsStrategy which
    will inform it *how* to read raw input and construct a ComsMessage
    from it, and method to call telling it how to react to new ComsMessages.
    """

    def __init__(
        self,
        coms_strat: ComsStrategy,
        recv_callback: Callable[[ComsMessage], Any],
        name: str | None = None,
        daemon: bool | None = None,
    ) -> None:
        """Constructor for a new ComsDriverReadLoop. Overides Thread.__init__

        :param coms_strat: A strategy that informs how to read incoming data
        :type coms_strat: ComsStrategy
        :param recv_callback: A function detailing what to do with recived input
        :type recv_callback: Callable[[ComsMessage], Any]
        :param name: The name of the thread
        :type name: str | None
        :param daemon: Wether or not to run the thread as a daemon
        :type daemon: bool | None
        """

        super().__init__(name=name, daemon=daemon)
        self._stop_event = Event()
        self._coms_strat = coms_strat
        self._recv_callback = recv_callback

    def run(self) -> None:
        """The main process of the thread.

        Overides Thread.run
        """
        proc, conn = self._spawn_get_msg_proc()
        proc.start()

        while not self._stop_event.is_set():
            if not proc.is_alive():
                received = conn.recv()
                if isinstance(received, Exception):
                    logger.error(f"received exception: {received}")
                else:
                    self._recv_callback(received)
                proc, conn = self._spawn_get_msg_proc()
                proc.start()
            proc.join(timeout=1)

        if proc.is_alive():
            proc.terminate()

    def _spawn_get_msg_proc(self) -> Tuple[mp.Process, Connection]:
        """Method to create resources needed to wait for  and read next message.

        Because reading the next ComsMessage is can be implimented as a blocking
        process, we need to move reading data into a seperate process to allow
        it run indefeintly without blocking execution but still allowing a way
        to stop kill its termination (via SIGTERM / SIGKILL).

        This method will create the process and a connection to by which a ComsMessage
        can be read and constructed, and a Connection by which messages/errors can be
        shared with the main process

        :return: A process to read a message and connection to communicate with
            main process
        :rtype: Tuple[multiprocessing.Process, multiprocessing.connection.Connection]
        """
        a, b = mp.Pipe()

        return (
            mp.Process(target=_get_msg, args=(self._coms_strat, a), daemon=True),
            b,
        )

    def stop(self, timeout: float | None = None) -> None:
        """A method to set events to safly end thread and
        clean up any/all used resources

        :param timeout: Amount of time in seconds to block calling
            thread before returning with None meaning an infinte time
        :type timeout: float  | None
        """
        self._stop_event.set()
        self.join(timeout=timeout)


def _get_msg(strat: ComsStrategy, conn: Connection) -> None:
    """Function run to get receive next message

    Due to the fact that strategies often have blocking read methods,
    this is a top level funtion that will be run in a sperate
    process that can be ended with a SIGTERM/SIGKILL.

    NOTE: This function must be top level to work with
    multiprocessing spawn start on windows and macos

    :param strat: A strategy that informs how to read incoming data
    :type strat: ComsStrategy
    :param conn: A connection by which to send data back
        to the main process
    :type conn: multiprocessing.connection.Connection
    """
    try:
        conn.send(strat.read())
    except Exception as e:
        logger.error(
            f"While reading next ComsMessage got exception {traceback.format_exc()}"
        )
        conn.send(e)
