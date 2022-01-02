import functools
import math
import sys


class _BaseResultWaiter:
    __slots__ = (
        'scheduler',
        '_event',
        '_set',
        '_routines',
        '_result',
        '_exception',
    )

    def __init__(self, scheduler):
        self.scheduler = scheduler

        self._event = self._create_evnet()

        self._set = False
        self._routines = []

        self._result = None
        self._exception = None

    def _create_evnet(self):
        raise NotImplementedError

    def _poll_event(self, *, timeout=None):
        raise NotImplementedError

    def _set_event(self):
        raise NotImplementedError

    def is_set(self):
        return self._set

    def callback_routine(self, func, *, name=None):
        if self.is_set():
            raise RuntimeError('Cannot register a callback routine to already-set waiter')

        routine = self.scheduler.routine(functools.partial(func, self), name=name)
        self._routines.append(routine)

        return routine

    def wait(self, *, timeout=None):
        if not self.is_set():
            self._poll_event(timeout=timeout)

        if self._exception is not None:
            raise self._exception

        return self._result

    def set_result(self, result):
        if self.is_set():
            raise RuntimeError('Cannot set result of already-set waiter')

        self._result = result
        self._set_event()

        for routine in self._routines:
            routine.spawn()

    def set_exception(self, exception):
        if self.is_set():
            raise RuntimeError('Cannot set exception of already-set waiter')

        self._exception = exception
        self.__set_event()

        for routine in self._routines:
            routine.spawn()


if sys.platform == 'win32':
    import ctypes

    from . import pyapi
    from . import winapi

    class WindowsResultWaiter(_BaseResultWaiter):
        def _create_evnet(self):
            return winapi.CreateEventA(None, False, False, None)

        def _poll_event(self, *, timeout=None):
            if timeout is None:
                timeout = winapi.INFINITE
            else:
                timeout = math.floor(timeout * 1000)

            events = (winapi.HANDLE * 2)()
            events[0] = pyapi._PyOS_SigintEvent()
            events[1] = self._event

            events = ctypes.cast(events, ctypes.POINTER(winapi.HANDLE))
            result = winapi.WaitForMultipleObjectsEx(2, events, False, timeout, False)

            if result == winapi.WaitForResult.WAIT_IO_COMPLECTION:
                raise InterruptedError('Interrupted while waiting for result')

            if result == winapi.WaitForResult.WAIT_TIMEOUT:
                raise TimeoutError('Timed out while waiting for result')

            if result == winapi.WaitForResult.WAIT_FAILED:
                raise OSError

        def _set_event(self):
            winapi.SetEvent(self._event)

    ResultWaiter = WindowsResultWaiter
