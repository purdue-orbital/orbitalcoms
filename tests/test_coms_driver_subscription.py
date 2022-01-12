from orbitalcoms.coms.drivers import BaseComsDriver
from orbitalcoms.coms.strategies import LocalComsStrategy
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.subscribers.subscription import (
    ComsSubscription,
    OneTimeComsSubscription,
)


def test_coms_subscription():
    local_driver = BaseComsDriver(LocalComsStrategy())
    count = 0

    def count_up(m: ComsMessage):
        nonlocal count
        count += m.ABORT + m.QDM + m.LAUNCH + m.STAB

    cs = ComsSubscription(count_up)
    local_driver.register_subscriber(cs)
    local_driver._notify_subscribers(ComsMessage(1, 1, 0, 0))
    local_driver._notify_subscribers(ComsMessage(0, 0, 0, 1))
    local_driver._notify_subscribers(ComsMessage(1, 1, 1, 0))

    assert count == 6
    assert cs in local_driver.subscrbers

    local_driver.unregister_subscriber(cs)
    local_driver._notify_subscribers(ComsMessage(1, 1, 1, 0))
    assert count == 6
    assert cs not in local_driver.subscrbers


def test_onetime_coms_subscription():
    local_driver = BaseComsDriver(LocalComsStrategy())
    count = 0

    def count_up(m: ComsMessage):
        nonlocal count
        count += m.ABORT + m.QDM + m.LAUNCH + m.STAB

    ocs = OneTimeComsSubscription(count_up)
    local_driver.register_subscriber(ocs)
    local_driver._notify_subscribers(ComsMessage(1, 1, 0, 0))
    local_driver._notify_subscribers(ComsMessage(0, 0, 0, 1))
    local_driver._notify_subscribers(ComsMessage(1, 1, 1, 0))

    assert count == 2
    assert ocs not in local_driver.subscrbers


def test_subscriptions_with_errs():
    local_driver = BaseComsDriver(LocalComsStrategy())

    def raise_err(_: ComsMessage):
        raise Exception("Yikes, an error happend")

    cs = ComsSubscription(raise_err)
    cs_expect_err = ComsSubscription(raise_err, expect_err=True)

    local_driver.register_subscriber(cs)
    local_driver.register_subscriber(cs_expect_err)
    local_driver._notify_subscribers(ComsMessage(0, 0, 0, 1))
    local_driver._notify_subscribers(ComsMessage(0, 0, 0, 1))
    local_driver._notify_subscribers(ComsMessage(0, 0, 0, 1))

    assert cs not in local_driver.subscrbers
    assert cs_expect_err in local_driver.subscrbers

    local_driver.unregister_subscriber(cs_expect_err)
    assert cs_expect_err not in local_driver.subscrbers


def test_unregister_never_registered_subscriber():
    local_driver = BaseComsDriver(LocalComsStrategy())
    cs = ComsSubscription(lambda _: ...)

    # Make sure this does not error
    local_driver.unregister_subscriber(cs)
