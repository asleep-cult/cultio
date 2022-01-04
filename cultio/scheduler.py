import contextlib
import enum
import logging
import os
import queue
import threading

from .routine import SchedulerRoutine
from .sync import Promise


logger = logging.getLogger(__name__)


class _QueueControl(enum.Enum):
    SHUTDOWN = enum.auto()


class _WorkerThread(threading.Thread):
    def __init__(self, *, name=None):
        super().__init__(name=name)

        self._queue = queue.Queue()
        self._routine = None

    @contextlib.contextmanager
    def _set_routine(self, routine):
        if self._routine is not None:
            raise RuntimeError('thread attempted to set multiple futures')

        self._routine = routine
        routine._running.set()
        yield
        self._routine = None

    def get_routine(self):
        if self._routine is None:
            raise RuntimeError('thread has no routine')

        return self._routine

    def interrupt(self, interrupt):
        routine = self._routine
        if routine is None or routine.is_ignored(interrupt):
            if self._routine.is_intenqueued(interrupt):
                ...
            else:
                try:
                    routine.raise_interrupt(interrupt)
                except RuntimeError:
                    logger.warning(
                        'Failed to raise interrupt due to race condition', exc_info=True
                    )

    def run(self):
        running = True
        while running:
            item = self._queue.get()
            if item is _QueueControl.SHUTDOWN:
                running = False
            else:
                if self._routine is not None:
                    raise RuntimeError('thread attempted to run multiple routines')

                with self._set_routine(item):
                    try:
                        result = item.func()
                    except BaseException as exc:
                        item._promise.set_exception(exc)
                    else:
                        item._promise.set_result(result)

        if not self._queue.empty():
            logger.warning('Shutting down worker with non-empty queue')


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

        self.thread_ids = set()
        self.thread_ids.add(main_thread.ident)

    def current_routine(self):
        thread = threading.current_thread()
        if thread.ident not in self.thread_ids:
            raise RuntimeError('Cannot get routine in this thread')

        assert isinstance(thread, _WorkerThread)
        return thread.get_routine()

    def routine(self, func, *, name=None):
        return SchedulerRoutine(self, func, name=name)

    def promise(self):
        return Promise(self)
