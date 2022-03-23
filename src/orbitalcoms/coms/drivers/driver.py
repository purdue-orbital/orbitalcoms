from __future__ import annotations

import logging
import traceback
from threading import Condition
from typing import TYPE_CHECKING, Set

from ..._utils import log
from ..errors import ComsDriverReadError, ComsDriverWriteError
from ..messages import construct_message
from ..subscribers import OneTimeComsSubscription
from .driverreadloop import ComsDriverReadLoop

if TYPE_CHECKING:
    from ..messages import ComsMessage, ParsableComType
    from ..strategies import ComsStrategy
    from ..subscribers import ComsSubscriptionLike

logger = log.make_logger(__name__, logging.ERROR)


class ComsDriver:
    """The ComsDriver is a controls communications of a statuion. It is
    responsible for starting and stopping the read loop which allows a
    user to continuously recieve messages, registering and removing
    ComsSubscritons which preform some action upon reciveing a message,
    and alerting a subsrciptions when a new message has been reciveived.
    """

    def __init__(self, strategy: ComsStrategy) -> None:
        """Initializes a ComsDrivers with a provided strategy.

        :param strategy: An object which describes how to read/write messages
        :type strategy: ComsStrategy
        """
        self.subscrbers: Set[ComsSubscriptionLike] = set()
        self._read_loop: ComsDriverReadLoop | None = None
        self._strategy = strategy

    def __del__(self) -> None:
        self.end_read_loop()

    @property
    def strategy(self) -> ComsStrategy:
        """Returns the ComsStrategy used by the ComsDriver
        without risk of overwritting reference.

        :return: The object that descibes how to read/write messages
        :rtype: ComsStrategy
        """
        return self._strategy

    def start_read_loop(self, block: bool = False) -> ComsDriverReadLoop:
        """Creates and starts a new thread that will receive and notify all
        subscribers to the ComsDriver when a new messages has been succefully
        recieved.

        :param block: State whether readloop should be run in a blocking manner
        :type block: bool
        :return: A thread handling the recieving a new messages
        :rtype: ComsDriverReadLoop
        """
        if self._read_loop:
            self.end_read_loop()
        self._read_loop = self._spawn_read_loop_thread()
        self._read_loop.start()
        if block:
            self._read_loop.join()
        return self._read_loop

    def end_read_loop(self, timeout: float | None = None) -> None:
        """Ends and deferences a the current readloop, effectively
        stopping the ComsDriver from recieving new messages.

        :param timeout: The amount of time in seconds to wait for the
            read loop to join. If None, wait indefinitely
        :type timeout: float | None
        """
        if self._read_loop:
            if self._read_loop.is_alive():
                self._read_loop.stop(timeout=timeout)
            self._read_loop = None

    def _spawn_read_loop_thread(self) -> ComsDriverReadLoop:
        """Protected method for instancing a ComsDriverReadLoop.

        :return: A thread capable of recieving new messages
        :rtype: ComsDriverReadLoop
        """
        return ComsDriverReadLoop(self._strategy, self._notify_subscribers, daemon=True)

    @property
    def is_reading(self) -> bool:
        """Boolean property that let's the caller know if the
        ComsDriver is currently accepting new messages.

        :return: If the read loop active
        :rtype: bool
        """
        return self._read_loop is not None and self._read_loop.is_alive()

    def read(self, timeout: float | None = None) -> ComsMessage:
        """A blocking funtion that will wait for and return the
        next ComsMessage that the readloop receives. This method
        takes an optional timeout parameter that will raise an exception
        if a message is not recieved within the designated time.

        :param timeout: Time in second to wait for a message. If none
            is provied wait indefinitely
        :type timeout: float | None
        :raises ComsDriverReadError: message not recieved within timeout
        :return: Recieved message
        :rtype: ComsMessage
        """
        cv = Condition()
        message: ComsMessage | None = None

        def _get_next(m: ComsMessage) -> None:
            nonlocal message
            with cv:
                message = m
                cv.notify()

        self.register_subscriber(OneTimeComsSubscription(_get_next))
        with cv:
            cv.wait_for(lambda: message is not None, timeout=timeout)
            if message is None:
                raise ComsDriverReadError("Failed to read next message")
        return message

    def write(self, m: ParsableComType, suppress_errors: bool = False) -> bool:
        """This method takes an object that can be parsed and used to
        construct a new ComsMessage. This message is then passed to a
        the ComsDriver communincation strategy to be sent to its counterpart.

        :param m: Something that can be parsed and constructed into
            a ComsMessage
        :type m: ParasableComType
        :param suppress_errors: If a ComsMessage cannot be constructed
            or the message cannot be sent, should an Exception be rasied
        :type suppress_errors: bool
        :raises ComsDriverWriteError: If a message could not be constructed or
            if the constructed message could not be sent
        :return: Wether the message was successfully sent
        :rtype: bool
        """
        try:
            self._strategy.write(construct_message(m))
            return True
        except Exception as e:
            if suppress_errors:
                return False
            raise ComsDriverWriteError(f"Failed to send message '{m}'") from e

    def register_subscriber(self, sub: ComsSubscriptionLike) -> None:
        """Takes a an object that will reacts to new messages. The subscriber is added to
        an internal set (meaning that order of subscribers updating cannot be guaranteed)
        and notified when a new messages is received.

        :param sub: An object that will react to new incoming messages
        :type sub: ComsSubscriptionLike
        """
        self.subscrbers.add(sub)

    def unregister_subscriber(self, sub: ComsSubscriptionLike) -> None:
        """Takes a reference to that ComsSubscriptionLike and removes the subscription
        so that it will not react to future messages. If the subscriber was already not
        subscribed to the ComsDriver, this method is a NOP.

        :param sub: An object that will react to new incoming messages
        :type sub: ComsSubscriptionLike
        """
        if sub in self.subscrbers:
            self.subscrbers.remove(sub)

    def _notify_subscribers(self, m: ComsMessage) -> None:
        """Takes a ComsMessage and iterates over the ComsDrivers subscriptions
        in no particular order. The ComsMessage and reference to the ComsDriver
        is passed to the subscibers so that they may be able to update their state,
        and state of the ComsDriver as needed.

        If a subsciber raises an exception while updating thier or the driver's
        state they will be automatically unregistered and will not react to
        future messages.

        :param m: A (likely newly recieved) ComsMessage
        :type m: ComsMessage
        """
        for s in self.subscrbers.copy():
            try:
                s.update(m, self)
            except Exception:
                logger.error(f"subscriber raised exception: {traceback.format_exc()}")
                if not s.expect_err:
                    self.unregister_subscriber(s)
