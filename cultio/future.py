import functools
import math
import sys
import threading


class Future:
    """An event with a value or exception bound to it. This class represents
    the return value of asynchronous operations.
    """
    __slots__ = (
        'scheduler',
        '_event',
        '_routines',
        '_result',
        '_exception',
    )

    def __init__(self, scheduler):
        self.scheduler = scheduler

        self._event = self.create_event()

        self._routines = []
        self._result = None
        self._exception = None

    def create_event(self):
        return Event(self.scheduler)

    def is_set(self):
        """Returns True if the future's result has been set."""
        return self._event.is_set()

    def callback_routine(self, func, *, name=None):
        """Creates a routine that will be spawned when the future's result is set."""
        routine = self.scheduler.routine(functools.partial(func, self), name=name)

        if not self.is_set():
            self._routines.append(routine)
        else:
            routine.spawn()

        return routine

    def wait(self, *, timeout=None):
        """Waits for the future's result to be set and returns it.

        Arguments:
            timeout (float): The maximum amount of time to wait in seconds,
                TimeoutError will be raised if the timeout is exceeded.
        """
        if not self.is_set():
            self._event.wait(timeout=timeout)

        if self._exception is not None:
            raise self._exception

        return self._result

    def set_result(self, result):
        """Sets the futures result and spawns the callback routines."""
        if not self.is_set():
            self._result = result
            self._event.set()

            for routine in self._routines:
                routine.spawn()

            del self._routines

    def set_exception(self, exception):
        """Sets the futures result as an exception and spawns the callback routines."""
        if isinstance(exception, type):
            exception = exception()

        if not isinstance(exception, BaseException):
            raise TypeError('exception must be a BaseException')

        if not self.is_set():
            self._exception = exception
            self._event.set()

            for routine in self._routines:
                routine.spawn()

            del self._routines


class _BaseEvent:
    __slots__ = ('scheduler',)

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def __repr__(self):
        return '<{} [{}]>'.format(
            self.__class__.__name__, 'set' if self.is_set() else 'unset'
        )

    def is_set(self):
        """Returns True if the event has been set."""
        raise NotImplementedError

    def wait(self, *, timeout=None):
        """Blocks the calling thread until set is called.

        Arguments:
            timeout (float): The maximum amount of time to wait in seconds,
                TimeoutError will be raised if the timeout is exceeded.
        """
        raise NotImplementedError

    def set(self):
        """Sets the event and wakes up the waiting threads."""
        raise NotImplementedError


if sys.platform == 'win32':
    from . import pyapi
    from . import winapi

    class WindowsEvent(_BaseEvent):
        __slots__ = ('_flag', '_hevent')

        def __init__(self, scheduler):
            super().__init__(scheduler)
            self._flag = False
            self._hevent = winapi.CreateEventA(None, False, False, None)

        def is_set(self):
            return self._flag

        def wait(self, *, timeout=None):
            if timeout is None:
                timeout = winapi.INFINITE
            else:
                timeout = math.floor(timeout * 1000)

            events = (winapi.HANDLE * 2)(pyapi._PyOS_SigintEvent(), self._hevent)
            result = winapi.WaitForMultipleObjectsEx(2, events, False, timeout, False)

            if result == winapi.WaitForResult.WAIT_IO_COMPLECTION:
                raise InterruptedError('Interrupted while waiting for result')

            if result == winapi.WaitForResult.WAIT_TIMEOUT:
                raise TimeoutError('Timed out while waiting for result')

            if result == winapi.WaitForResult.WAIT_FAILED:
                raise OSError

        def set(self):
            winapi.SetEvent(self._hevent)

    Event = WindowsEvent
else:
    class UnixEvent(_BaseEvent):
        __slots__ = ('_flag', '_tevent',)

        def __init__(self, scheduler):
            super().__init__(scheduler)
            self._flag = False
            self._tevent = threading.Event()

        def is_set(self):
            return self._flag

        def wait(self, *, timeout=None):
            if not self._tevent.wait(timeout=timeout):
                raise TimeoutError('Timed out while waiting for result')

        def set(self):
            self._tevent.set()

    Event = UnixEvent
