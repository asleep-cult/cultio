import cffi
import faulthandler
import sys
import time
import typing

path = sys.path.pop(0)
from cultio._switch import ffi, lib
sys.path.insert(0, path)

faulthandler.enable()


if sys.platform == 'win32':
    RESERVE = 232
else:
    RESERVE = 48

ffi = typing.cast(cffi.FFI, ffi)
stack = ffi.new('void *[8192]')
cstack = ffi.new('void *[1]')


@ffi.callback('void(void)')
def inside_switch():
    print(
        'hello. the cpython virtual machine was running main() '
        'but main() decided it was time for a temporary retirement. '
        'in the meantime i\'ll be executing instructions on my own stack.'
    )

    time.sleep(2)

    print('hello again. this is getting boring... i\'m foint to wakeup main()')
    lib.sswitch(stack, cstack)


def main():
    addr = stack + 4096

    print(f'main(): stack={stack}')
    print(f'        high={addr}')
    print(f'        returnaddr={inside_switch}')

    stack[4096] = inside_switch
    segment = addr - (RESERVE // 8)

    print(1)
    lib.sswitch(cstack, segment)
    print(2)


main()
