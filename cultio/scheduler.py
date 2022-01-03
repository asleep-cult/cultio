import enum
import os
import queue
import signal
import threading
import warnings

from .concurrent import Promise
from .interrupts import InterruptError
from .pyapi import PyThreadState_SetAsyncExc
from .routine import SchedulerRoutine


class _QueueControl(enum.Enum):
    SHUTDOWN = enum.auto()


class _WorkerThread(threading.Thread):
    def __init__(self, *, name=None):
        super().__init__(name=name)
        self._queue = queue.Queue()
        self._routine = None

    def interrupt(self, interrupt):
        if (
            self._routine is not None
            and not self._routine.is_intignored(interrupt)
        ):
            if self._routine.is_intenqueued(interrupt):
                return

            handler = self._routine.get_interrupt(interrupt)
            if handler is not None:
                routine = self._routine.scheduler.routine(handler)
                routine.spawn()
            else:
                if interrupt == signal.SIGINT:
                    exc = KeyboardInterrupt
                else:
                    exc = InterruptError(interrupt)

                # If the routine is currently waiting on a future, then we
                # wake it up and set the future's interrupt. Otherwise we
                # deliver an exception to the thread asynchronously.
                future = self._routine._future
                if future is not None:
                    future._interrupt = exc
                    future._set_event()
                else:
                    PyThreadState_SetAsyncExc(self.native_id, exc)

    def run(self):
        running = True
        while running:
            item = self._queue.get()
            if item is _QueueControl.SHUTDOWN:
                if not self._queue.empty():
                    warnings.warn('Shutting down worker with non-empty queue')

                running = False
            else:
                self._routine = item
                try:
                    result = self._routine.func()
                except BaseException as exc:
                    self._routine._promise.set_exception(exc)
                else:
                    self._routine._promise.set_result(result)


class ThreadScheduler:
    def __init__(self, *, max_threads=None):
        main_thread = threading.main_thread()
        if threading.current_thread() is not main_thread:
            raise RuntimeError(
                'ThreadScheduler can only be created in the main thread'
            )

        if max_threads is not None:
            self.max_threads = max_threads
        else:
            self.max_threads = min(32, (os.cpu_count() or 1) + 4)

        self.threads = []
        self.threads.append(main_thread)

    def routine(self, func, *, name=None):
        return SchedulerRoutine(self, func, name=name)

    def promise(self):
        return Promise(self)
