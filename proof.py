import cffi
import faulthandler
import sys
import time
import typing

from cultio._switch import ffi, lib

faulthandler.enable()

if sys.platform == 'win32':
    RESERVE = 168 + (8 * 11)
else:
    RESERVE = 0x30

ffi = typing.cast(cffi.FFI, ffi)

stack = ffi.new('void *[8192]')
cstack = ffi.new('void **')


@ffi.callback('void(void)')
def inside_switch():
    print(
        'hello. the cpython virtual machine was running main() '
        'but main() decided it was time for a temporary retirement. '
        'in the meantime i\'ll be executing instructions on my own stack.'
    )

    time.sleep(2)

    print('hello again. this is getting boring... i\'m going to wakeup main()')

    ptr = ffi.new('void **')
    # print(ffi.addressof(ptr))

    lib.sswitch(ptr, cstack)


def main():
    addr = stack + 8190

    print(f'main(): stack={stack}')
    print(f'        high={addr}')
    print(f'        returnaddr={inside_switch}')

    if sys.platform == 'win32':
        stack[8190] = inside_switch
        stack[8189] = ffi.cast('void *', 0)
        stack[8188] = addr
        stack[8187] = stack
    else:
        stack[8190] = inside_switch

    segment = addr - (RESERVE // 8)
    print(segment)

    print(1)
    lib.sswitch(cstack, ffi.new('void **', segment))
    print(2)


main()
