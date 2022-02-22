import ctypes
import faulthandler
import sys

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


@ctypes.CFUNCTYPE(None)
def inside_switch():
    print('hello')
    print(sys._getframe().f_back)


def main():
    addr = ctypes.addressof(stack) + (4096 * 8)

    print(f'main(): stack={hex(ctypes.addressof(stack))}')
    print(f'        high={hex(addr)}')
    print(f'        returnaddr={hex(ctypes.addressof(inside_switch))}')

    stack[4096] = ctypes.addressof(inside_switch)
    segment = ctypes.cast(addr - RESERVE, ctypes.c_void_p)

    pointer = ctypes.c_void_p()
    print(1)
    lib.switch(ctypes.byref(pointer), ctypes.byref(segment))
    print(2)


main()
