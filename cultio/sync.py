import functools
import threading


class Promise:
    __slots__ = (
        'scheduler',
        '_event',
        '_set',
        '_routines',
        '_result',
        '_exception',
    )

    def __init__(self, scheduler):
        thread = threading.current_thread()
        if thread.ident not in scheduler.thread_ids:
            raise RuntimeError('Cannot instantiate Promise in this thread')

        self.scheduler = scheduler

        self._routines = []

        self._set = False
        self._result = None
        self._exception = None

    def is_set(self):
        return self._set

    def result(self):
        if not self.is_set():
            raise RuntimeWarning('cannot retrieve result from unset promise')

        return self._result

    def exception(self):
        if not self.is_set():
            raise RuntimeWarning('cannot retrieve exception from unset promise')

        return self._exception

    def set_result(self, result):
        if self.is_set():
            return False

        self._result = result
        return self._spawn_routines()

    def set_exception(self, exception):
        if self.is_set():
            return False

        if isinstance(exception, type):
            exception = exception()

        if not isinstance(exception, BaseException):
            raise TypeError('exception must be a BaseException')

        self._exception = exception
        return self._spawn_routines()

    def callback_routine(self, func, *, name=None):
        routine = self.scheduler.routine(functools.partial(func, self), name=name)

        if not self.is_set():
            self._routines.append(routine)
        else:
            routine.spawn()

        return routine

    def _spawn_routines(self):
        self._set = True

        for routine in self._routines:
            routine.spawn()

        self._routines = None
        return True

    def future(self):
        return Future(self)


class Future:
    __slots__ = (
        'scheduler',
        '_routine',
        '_promise',
        '_event',
        '_interrupt'
    )

    def __init__(self, promise: Promise):
        self.scheduler = promise.scheduler
        self._routine = promise.scheduler.current_routine()

        self._promise = promise
        self._event = None
        self._interrupt = None

    def _get_event(self):
        if self._event is not None:
            return self._event

        self._event = threading.Event()
        self._promise.callback_routine(lambda promise: self._event.set())
        return self._event

    def _interrupt_event(self, exc):
        self._interrupt = exc
        self._event.set()

    def is_set(self):
        return self._promise.is_set()

    def result(self):
        return self._promise.result()

    def exception(self):
        return self._promise.exception()

    def wait(self, *, timeout=None):
        """Waits for the future's result to be set and returns it.

        Arguments:
            timeout (float): The maximum amount of time to wait in seconds,
                TimeoutError will be raised if this value is exceeded.
        """
        routine = self.scheduler.current_routine()
        if routine is not self._routine:
            raise RuntimeError('This routine cannot wait on this promise')

        if not self.is_set():
            with routine._set_future(self):
                set = self._get_event().wait(timeout)

                if self._interrupt is not None:
                    raise self._interrupt

                if not set:
                    raise TimeoutError('Timed out while waiting for result')

        exception = self.exception()
        if exception is not None:
            raise exception

        return self.result()
