import signal
from collections.abc import Callable

from . import interrupts


class SchedulerRoutine:
    __slots__ = (
        'scheduler',
        'func',
        'name',
        '_interrupts',
        '_future',
        '_promise',
        '_spawned',
    )

    def __init__(self, scheduler, func, *, name=None):
        if name is None:
            name = getattr(func, '__name__', '<unknown>')

        self.scheduler = scheduler
        self.func = func
        self.name = name

        self._interrupts = {}
        self._future = None

        self._promise = self.scheduler.promise()
        self._spawned = False

    def __repr__(self):
        return f'<SchedulerRoutine {self.name!r}>'

    def get_interrupt(self, interrupt):
        if interrupt not in signal.valid_signals():
            raise ValueError(f'Invalid interrupt: {interrupt!r}')

        return self._interrupts.get(interrupt)

    def set_interrupt(self, interrupt, handler):
        if interrupt not in signal.valid_signals():
            raise ValueError(f'Invalid interrupt: {interrupt!r}')

        if not isinstance(handler, (interrupts.InterruptType, Callable)):
            raise TypeError(
                'Interrupt must be INTIGNORE, INTENQUEUE or a callable'
            )

        self._interrupts[interrupt] = handler

    def is_intignored(self, interrupt):
        return self.get_interrupt(interrupt) is interrupts.INTIGNORE

    def is_intenqueued(self, interrupt):
        return self.get_interrupt(interrupt) is interrupts.INTENQUEUE

    def is_spawned(self):
        return self._spawned

    def spawn(self):
        if self.is_spawned():
            raise RuntimeError('routine already spawned')
        else:
            self._spawned = True
