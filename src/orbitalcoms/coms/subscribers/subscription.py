from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from typing_extensions import Protocol

if TYPE_CHECKING:
    from ..drivers import ComsDriver
    from ..messages import ComsMessage


class ComsSubscriberLike(Protocol):
    expect_err: bool

    def update(self, message: ComsMessage, driver: ComsDriver) -> Any:
        ...


class ComsSubscription(ComsSubscriberLike):
    def __init__(
        self, on_update: Callable[[ComsMessage], Any], expect_err: bool = False
    ) -> None:
        self.on_update = on_update
        self.expect_err = expect_err

    def update(self, message: ComsMessage, _: ComsDriver) -> None:
        self.on_update(message)


class OneTimeComsSubscription(ComsSubscription):
    def update(self, message: ComsMessage, driver: ComsDriver) -> None:
        super().update(message, driver)
        driver.unregister_subscriber(self)
