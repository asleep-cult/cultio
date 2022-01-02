import signal
from collections.abc import Callable

from . import interrupts


class SchedulerRoutine:
    __slots__ = (
        'scheduler',
        'func',
        'name',
        '_interrupts',
    )

    def __init__(self, scheduler, func, *, name=None):
        if name is None:
            name = func.__name__

        self.scheduler = scheduler
        self.func = func
        self.name = name

        self._interrupts = {}

    def __repr__(self):
        return f'<SchedulerRoutine {self.name!r}>'

    def set_interrupt(self, interrupt, handler):
        if interrupt not in signal.valid_signals():
            raise ValueError(f'Invalid interrupt: {interrupt!r}')

        if not isinstance(handler, (interrupts.InterruptBehavior, Callable)):
            raise TypeError(
                'Interrupt must be INTIGNORE, INTRAISE or a callable'
            )

        self._interrupts[interrupt] = handler