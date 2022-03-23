from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import Protocol

if TYPE_CHECKING:
    from ..drivers import ComsDriver
    from ..messages import ComsMessage


class ComsSubscriptionLike(Protocol):
    """An agent that will react when ComsDriver recievs a message

    A ComsSubscriptionLike is a protocol that outlines how what a
    subscriber to a ComsDriver should look like. They are composed
    of two parts:

    - An ``updaate`` method that describes what should be done with the incoming
      message or the data it contains.
    - An ``expect_err`` property which let's the ComsDriver know whether or not the
      ``update`` is allowed to raise exceptions. If not the ComsSubsriberLike is
      automatically un-subscribed from the ComsDriver.

    A user can write their own Subscribers as long as the have the same
    shape as the ComsSubscriptionLike
    """

    expect_err: bool

    @abstractmethod
    def update(self, message: ComsMessage, driver: ComsDriver) -> Any:
        ...


class ComsSubscription(ComsSubscriptionLike):
    """Wrapper class to turn a generic function into a ComsSubscriberLike"""

    def __init__(
        self,
        on_update: Callable[[ComsMessage], Any],
        expect_err: bool = False,
    ) -> None:
        """Wrapper class to turn a generic function into a ComsSubscriberLike

        :param on_update: Function to call when a message is recived
        :type on_update: Callable[[ComsMessage], Any]
        :param expect_err: Whether on or not the wrapped function is allowed to raie exceptions
        :type expect_err: bool
        """
        self.on_update = on_update
        self.expect_err = expect_err

    def update(self, message: ComsMessage, _: ComsDriver) -> None:
        """Calls the wrapped function when a message is received and passes
        it as a parameter

        :param message: Received message
        :type message: ComsMessage
        :param _: [UNUSED] ComsDriver instance that recieved the message
        :type _: ComsDriver
        """
        self.on_update(message)


class OneTimeComsSubscription(ComsSubscription):
    """Wrap a function to be called only after next recieved message

    Subclass of ComsSubscription that will automativally unsubscribe
    itself after a message is recieved
    """

    def update(self, message: ComsMessage, driver: ComsDriver) -> None:
        """Calls the wrapped function and then imediatly unsubscribes

        Overrides ComsSubscription.update

        :param message: Received message
        :type message: ComsMessage
        :param driver: ComsDriver instance that recieved the message
        :type driver: ComsDriver
        """
        super().update(message, driver)
        driver.unregister_subscriber(self)
