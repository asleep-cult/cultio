import contextlib
import signal
import threading

from . import interrupts
from .pyapi import PyThreadState_SetAsyncExc


class SchedulerRoutine:
    __slots__ = (
        'scheduler',
        'func',
        'name',
        '_interrupts',
        '_future',
        '_promise',
        '_spawned',
        '_thread',
        '_running'
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
        self._running = threading.Event()
        self._thread = None

    def __repr__(self):
        return f'<SchedulerRoutine {self.name!r}>'

    @contextlib.contextmanager
    def _set_future(self, future):
        if self._future is not None:
            raise RuntimeError('routine attempted to set multiple futures')

        self._future = future
        yield
        self._future = None

    def future(self):
        return self._promise.future()

    def get_inthandler(self, interrupt):
        if interrupt not in signal.valid_signals():
            raise ValueError(f'Invalid interrupt: {interrupt!r}')

        return self._interrupts.get(interrupt)

    def set_inthandler(self, interrupt, handler):
        if interrupt not in signal.valid_signals():
            raise ValueError(f'Invalid interrupt: {interrupt!r}')

        if not isinstance(handler, interrupts.InterruptType):
            raise TypeError('Interrupt must be INTIGNORE, INTENQUEUE')

        self._interrupts[interrupt] = handler

    def raise_interrupt(self, interrupt):
        if not self.is_spawned():
            raise RuntimeError('Interrupts can only be raised on spawned routines')

        if self._promise.is_set():
            raise RuntimeError('Interrupts cannot be raised on finished routines')

        self._running.wait()

        if interrupt == signal.SIGINT:
            exc = KeyboardInterrupt
        else:
            exc = interrupts.InterruptError(interrupt)

        if self._future is not None:
            self._future._interrupt_event(exc)
        else:
            PyThreadState_SetAsyncExc(self._thread.native_id, exc)

    def is_intignored(self, interrupt):
        return self.get_interrupt(interrupt) == interrupts.INTIGNORE

    def is_intenqueued(self, interrupt):
        return self.get_interrupt(interrupt) == interrupts.INTENQUEUE

    def is_spawned(self):
        return self._thread is not None

    def spawn(self):
        if self.is_spawned():
            raise RuntimeError('routine already spawned')
        else:
            self._spawned = True
