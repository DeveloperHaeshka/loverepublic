from . import (
    start,
    notsubbed,
    events,
    profile,
)
from aiogram import Router, Dispatcher


def setup(dp: Dispatcher, router: Router):
    """
    Register user handlers.

    :param Dispatcher dp: Dispatcher (root Router), needed for events
    :param Router router: User Router
    """
    
    events.register(dp)
    start.register(router)

    # all handlers afther `notsubbed` will work after user subscribed.
    notsubbed.register(router)

    profile.register(router)
