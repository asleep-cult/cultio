import ctypes
import sys

PyThreadState_SetAsyncExc = ctypes.pythonapi.PyThreadState_SetAsyncExc
PyThreadState_SetAsyncExc.argtypes = [ctypes.c_ulong, ctypes.py_object]
PyThreadState_SetAsyncExc.restype = ctypes.c_int

if sys.platform == 'win32':
    _PyOS_SigintEvent = ctypes.pythonapi._PyOS_SigintEvent
    _PyOS_SigintEvent.restype = ctypes.c_void_p
