import os
import sys
import platform

import cffi

machine = platform.machine()

if machine == 'AMD64':
    if sys.platform == 'win32':
        source = 'win_amd64_switch.c'
    elif sys.platform.startswith(('linux', 'freebsd', 'openbsd')):
        source = 'unix_amd64_switch.c'
    else:
        raise RuntimeError(f'cultio does not support {sys.platform!r}')
else:
    raise RuntimeError(f'cultio does not support {machine!r}')


dirname = os.path.dirname(__file__)

ffibuilder = cffi.FFI()
ffibuilder.cdef('void sswitch(void **, void **);')

with open(os.path.join(dirname, source)) as fp:
    ffibuilder.set_source('cultio._switch', fp.read())


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
