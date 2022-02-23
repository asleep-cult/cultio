import ctypes
import faulthandler
import sys
import time

faulthandler.enable()


if sys.platform == 'win32':
    lib = ctypes.cdll.LoadLibrary('./win_amd64_switch.o')
    lib.switch.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p)]

    RESERVE = 232
else:
    lib = ctypes.cdll.LoadLibrary('./unix_amd64_switch.o')
    lib.switch.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p)]

    RESERVE = 48


stack = (ctypes.c_void_p * 8192)()
cstack = ctypes.c_void_p()


@ctypes.CFUNCTYPE(None)
def inside_switch():
    retaddr = ctypes.c_int64.from_address(cstack.value + RESERVE).value

    print(f'inside_switch(): stack={hex(cstack.value)}')
    print(f'                 returnaddr={hex(retaddr)}')

    print(
        'hello. the cpython virtual machine was running main() '
        'but main() decided it was time for a temporary retirement. '
        'in the meantime i\'ll be executing instructions on my own stack.'
    )

    time.sleep(2)

    print('hello again. this is getting boring... i\'m foint to wakeup main()')
    lib.switch(stack, ctypes.byref(cstack))


def main():
    addr = ctypes.addressof(stack) + (4096 * 8)

    print(f'main(): stack={hex(ctypes.addressof(stack))}')
    print(f'        high={hex(addr)}')
    print(f'        returnaddr={hex(ctypes.addressof(inside_switch))}')

    stack[4096] = ctypes.cast(inside_switch, ctypes.c_void_p)
    segment = ctypes.cast(addr - RESERVE, ctypes.c_void_p)

    print(1)
    lib.switch(ctypes.byref(cstack), ctypes.byref(segment))
    print(2)


main()
