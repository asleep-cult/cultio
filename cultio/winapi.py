import ctypes

kernel32 = ctypes.WinDLL('kernel32')

BOOL = ctypes.c_int
BOOLEAN = BYTE = ctypes.c_ubyte
PVOID = ctypes.c_void_p
HANDLE = PVOID
HINSTANCE = HANDLE
HMODULE = HINSTANCE
WORD = ctypes.c_ushort
LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG = ctypes.c_ulong
NTSTATUS = ctypes.c_ulong

u_long = ctypes.c_ulong
PULONG = ctypes.POINTER(ULONG)

LPCVOID = ctypes.c_void_p
LPVOID = ctypes.c_void_p
LPCWSTR = LPWSTR = ctypes.c_wchar_p

if ctypes.sizeof(ctypes.c_ulonglong) == ctypes.sizeof(ctypes.c_void_p):
    uintprt_t = ctypes.c_ulonglong
else:
    uintprt_t = ctypes.c_ulong

ULONG_PRT = uintprt_t
UINT_PTR = uintprt_t

SOCKET = UINT_PTR


class _OVERLAPPEDDUMMYSTRUCT(ctypes.Structure):
    _fields_ = [
        ('Offset', DWORD),
        ('OffsetHigh', DWORD),
    ]


class _OVERLAPPEDDUMMYUNION(ctypes.Union):
    _fields_ = [
        ('DUMMYSTRUCTNAME', _OVERLAPPEDDUMMYSTRUCT),
        ('Pointer', PVOID),
    ]


class OVERLAPPED(ctypes.Structure):
    _fields_ = [
        ('Internal', ULONG_PRT),
        ('InternalHigh', ULONG_PRT),
        ('DUMMYUNIONNAME', _OVERLAPPEDDUMMYUNION),
        ('hEvent', HANDLE),
    ]


WSAOVERLAPPED = OVERLAPPED
LPOVERLAPPED = LPWSAOVERLAPPED = ctypes.POINTER(OVERLAPPED)

LPSECURITY_ATTRIBUTES = PVOID
LPCSTR = PVOID


class OVERLAPPED_ENTRY(ctypes.Structure):
    _fields_ = [
        ('lpCompletionKey', ULONG_PRT),
        ('lpOverlapped', LPOVERLAPPED),
        ('Internal', ULONG_PRT),
        ('dwNumberOfBytesTransferred', DWORD),
    ]


LPOVERLAPPED_ENTRY = ctypes.POINTER(OVERLAPPED_ENTRY)


class SYSTEMTIME(ctypes.Structure):
    _fields_ = [
        ('wYear', WORD),
        ('wMonth', WORD),
        ('wDayOfWeek', WORD),
        ('wDay', WORD),
        ('wHour', WORD),
        ('wMinute', WORD),
        ('wSecond', WORD),
        ('wMilliseconds', WORD),
    ]


PSYSTEMTIME = LPSYSTEMTIME = ctypes.POINTER(SYSTEMTIME)


class _ReasonDetailed(ctypes.Structure):
    _fields_ = [
        ('LocalizedReasonModule', HMODULE),
        ('LocalizedReasonId', ULONG),
        ('ReasonStringCount', ULONG),
        ('ReasonStrings', ctypes.POINTER(LPWSTR)),
    ]


class _Reason(ctypes.Union):
    _fields_ = [
        ('Detailed', _ReasonDetailed),
        ('SimpleReasonString', LPWSTR),
    ]


class REASON_CONTEXT(ctypes.Structure):
    _fields_ = [
        ('Version', ULONG),
        ('Flags', DWORD),
        ('Reason', _Reason)
    ]


PREASON_CONTEXT = ctypes.POINTER(REASON_CONTEXT)

LARGE_INTEGER = ctypes.c_int64
FILETIME = LARGE_INTEGER
LPFILETIME = ctypes.POINTER(LARGE_INTEGER)

PTIMERAPCROUTINE = ctypes.CFUNCTYPE(None, LPVOID, DWORD, DWORD)

CreateEventA = kernel32.CreateEventA
CreateEventA.argtypes = [LPSECURITY_ATTRIBUTES, BOOL, BOOL, LPCSTR]
CreateEventA.restype = HANDLE

SetEvent = kernel32.SetEvent
SetEvent.argtypes = [HANDLE]
SetEvent.restype = BOOL

ResetEvent = kernel32.ResetEvent
ResetEvent.argtypes = [HANDLE]
SetEvent.restype = BOOL

CreateWaitableTimerExW = kernel32.CreateWaitableTimerExW
CreateWaitableTimerExW.argtypes = [
    LPSECURITY_ATTRIBUTES,
    LPCWSTR,
    DWORD,
    DWORD,
]
CreateWaitableTimerExW.restype = HANDLE

SetWaitableTimerEx = kernel32.SetWaitableTimerEx
SetWaitableTimerEx.argtypes = [
    HANDLE,
    LARGE_INTEGER,
    LONG,
    PTIMERAPCROUTINE,
    LPVOID,
    PREASON_CONTEXT,
    ULONG,
]
SetWaitableTimerEx.restype = BOOL

HandlerRoutine = ctypes.CFUNCTYPE(BOOL, DWORD)

SetConsoleCtrlHandler = kernel32.SetConsoleCtrlHandler
SetConsoleCtrlHandler.argtypes = [HandlerRoutine, BOOL]

WaitForSingleObjectEx = kernel32.WaitForSingleObjectEx
WaitForSingleObjectEx.argtypes = [HANDLE, DWORD, BOOL]
WaitForSingleObjectEx.restype = DWORD

WaitForMultipleObjectsEx = kernel32.WaitForMultipleObjectsEx
WaitForMultipleObjectsEx.argtypes = [
    DWORD,
    ctypes.POINTER(HANDLE),
    BOOL,
    DWORD,
    BOOL,
]
