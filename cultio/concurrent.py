import functools
import threading


class Promise:
    """An event with a value or exception bound to it. This class represents
    the return value of asynchronous operations.
    """
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
        if thread not in scheduler.threads:
            raise RuntimeError('Cannot instantiate Promise in this thread')

        self.scheduler = scheduler

        self._routines = []

        self._set = False
        self._result = None
        self._exception = None

    def is_set(self):
        """Returns True if the promise's result has been set."""
        return self._set

    def result(self):
        """Returns the promise's result or raises RuntimError if it's not set."""
        if not self.is_set():
            raise RuntimeWarning('cannot retrieve result from unset promise')

        return self._result

    def exception(self):
        """Returns the promise's exception or raises RuntimError if it's not set."""
        if not self.is_set():
            raise RuntimeWarning('cannot retrieve result from unset promise')

        return self._exception

    def set_result(self, result):
        """Sets the promises result and spawns the callback routines."""
        if not self.is_set():
            self._result = result
            self._set = True

            for routine in self._routines:
                routine.spawn()

            del self._routines

    def set_exception(self, exception):
        """Sets the promise's result as an exception and spawns the callback routines."""
        if isinstance(exception, type):
            exception = exception()

        if not isinstance(exception, BaseException):
            raise TypeError('exception must be a BaseException')

        if not self.is_set():
            self._exception = exception
            self._set = True

            for routine in self._routines:
                routine.spawn()

            del self._routines

    def callback_routine(self, func, *, name=None):
        """Creates a routine that will be spawned when the promise's result is set."""
        routine = self.scheduler.routine(functools.partial(func, self), name=name)

        if not self.is_set():
            self._routines.append(routine)
        else:
            routine.spawn()

        return routine

    def future(self):
        return Future(self)


class Future:
    __slots__ = (
        '_promise',
        '_event',
        '_interrupt'
    )

    def __init__(self, promise):
        self._promise = promise
        self._event = threading.Event()
        self._interrupt = None

        self.callback_routine(lambda promise: self._set_event())

    def _set_event(self):
        self._event.set()

    def is_set(self):
        """Returns True if the future's result has been set."""
        return self._promise.is_set()

    def interrupted(self):
        """Returns True if the future was interrupted."""
        return self._interrupt is not None

    def result(self):
        """Returns the future's result or raises RuntimError if it's not set."""
        return self._promise.result()

    def exception(self):
        """Returns the future's exception or raises RuntimError if it's not set."""
        return self._promise.exception()

    def wait(self, *, timeout=None):
        """Waits for the future's result to be set and returns it.

        Arguments:
            timeout (float): The maximum amount of time to wait in seconds,
                TimeoutError will be raised if the timeout is exceeded.
        """
        thread = threading.current_thread()
        if thread not in self._promise.scheduler.threads:
            raise RuntimeError('Cannot wait for Future in this thread')

        if not self.is_set():
            assert thread._routine is not None
            assert thread._routine._future is None, 'cannot wait for multiple futures'

            thread._routine._future = self

            try:
                result = self._event.wait(timeout)
            finally:
                thread._routine._future = None

            if self.interrupted():
                raise self._interrupt

            if not result:
                raise TimeoutError('Timed out while waiting for result')

        exception = self.exception()
        if exception is not None:
            raise exception

        return self.result()

    def callback_routine(self, func, *, name=None):
        """Creates a routine that will be spawned when the future's result is set."""
        return self._promise.callback_routine(func, name=name)
