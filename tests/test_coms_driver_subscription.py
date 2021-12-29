from orbitalcoms.coms.drivers.localcomsdriver import LocalComsDriver
from orbitalcoms.coms.messages.message import ComsMessage
from orbitalcoms.coms.subscribers.subscription import (
    ComsSubscription,
    OneTimeComsSubscription,
)


def test_coms_subscription():
    ld = LocalComsDriver()
    count = 0

    def count_up(m: ComsMessage):
        nonlocal count
        count += m.ABORT + m.QDM + m.LAUNCH + m.STAB

    cs = ComsSubscription(count_up)
    ld.register_subscriber(cs)
    ld._notify_subscribers(ComsMessage(1, 1, 0, 0))
    ld._notify_subscribers(ComsMessage(0, 0, 0, 1))
    ld._notify_subscribers(ComsMessage(1, 1, 1, 0))

    assert count == 6
    assert cs in ld.subscrbers

    ld.unregister_subscriber(cs)
    ld._notify_subscribers(ComsMessage(1, 1, 1, 0))
    assert count == 6
    assert cs not in ld.subscrbers


def test_onetime_coms_subscription():
    ld = LocalComsDriver()
    count = 0

    def count_up(m: ComsMessage):
        nonlocal count
        count += m.ABORT + m.QDM + m.LAUNCH + m.STAB

    ocs = OneTimeComsSubscription(count_up)
    ld.register_subscriber(ocs)
    ld._notify_subscribers(ComsMessage(1, 1, 0, 0))
    ld._notify_subscribers(ComsMessage(0, 0, 0, 1))
    ld._notify_subscribers(ComsMessage(1, 1, 1, 0))

    assert count == 2
    assert ocs not in ld.subscrbers


def test_subscriptions_with_errs():
    ld = LocalComsDriver()

    def raise_err(_: ComsMessage):
        raise Exception("Yikes, an error happend")

    cs = ComsSubscription(raise_err)
    cs_expect_err = ComsSubscription(raise_err, expect_err=True)

    ld.register_subscriber(cs)
    ld.register_subscriber(cs_expect_err)
    ld._notify_subscribers(ComsMessage(0, 0, 0, 1))
    ld._notify_subscribers(ComsMessage(0, 0, 0, 1))
    ld._notify_subscribers(ComsMessage(0, 0, 0, 1))

    assert cs not in ld.subscrbers
    assert cs_expect_err in ld.subscrbers

    ld.unregister_subscriber(cs_expect_err)
    assert cs_expect_err not in ld.subscrbers


def test_unregister_never_registered_subscriber():
    ld = LocalComsDriver()
    cs = ComsSubscription(lambda _: ...)

    # Make sure this does not error
    ld.unregister_subscriber(cs)
