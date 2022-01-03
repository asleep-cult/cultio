import os
import threading

from .future import Future
from .routine import SchedulerRoutine


class _WorkerThread(threading.Thread):
    def __init__(self, *, name=None):
        super().__init__(name=name)


class ThreadScheduler:
    def __init__(self, *, max_threads=None):
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError(
                'ThreadScheduler can only be created in the main thread'
            )

        if max_threads is not None:
            self.max_threads = max_threads
        else:
            self.max_threads = min(32, (os.cpu_count() or 1) + 4)

    def routine(self, func, *, name=None):
        return SchedulerRoutine(self, func, name=name)

    def future(self):
        return Future(self)
