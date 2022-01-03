import enum
import signal


class InterruptError(Exception):
    def __init__(self, interrupt):
        self.interrupt = interrupt

    def __str__(self):
        signame = signal.strsignal(self.interrupt)
        if signame is None:
            signame = '<unknown interrupt>'

        return f'An interrupt was raised: {signame}'


class InterruptType(enum.IntEnum):
    INTIGNORE = enum.auto()
    INTRAISE = enum.auto()


INTIGNORE = InterruptType.INTIGNORE
INTRAISE = InterruptType.INTRAISE

NSIG = signal.NSIG

SIGABRT = signal.SIGABRT
SIGFPE = signal.SIGFPE
SIGILL = signal.SIGILL
SIGINT = signal.SIGINT
SIGSEGV = signal.SIGSEGV
SIGTERM = signal.SIGTERM


if hasattr(signal, 'SIGBREAK'):
    SIGBREAK = signal.SIGBREAK

if hasattr(signal, 'SIGALARM'):
    SIGALARM = signal.SIGALARM

if hasattr(signal, 'SIGBUS'):
    SIGBUS = signal.SIGBUS

if hasattr(signal, 'SIGCHLD'):
    SIGCHLD = signal.SIGCHLD

if hasattr(signal, 'SIGCONT'):
    SIGCONT = signal.SIGCONT

if hasattr(signal, 'SIGHUP'):
    SIGHUP = signal.SIGHUP

if hasattr(signal, 'SIGKILL'):
    SIGKILL = signal.SIGKILL

if hasattr(signal, 'SIGPIPE'):
    SIGPIPE = signal.SIGPIPE

if hasattr(signal, 'SIGUSR1'):
    SIGUSR1 = signal.SIGUSR1

if hasattr(signal, 'SIGUSR2'):
    SIGUSR1 = signal.SIGUSR2

if hasattr(signal, 'SIGUSR3'):
    SIGUSR1 = signal.SIGUSR3

if hasattr(signal, 'SIGWINCH'):
    SIGWINCH = signal.SIGWINCH
