from ._windows_backend_utilities import _ensure_windows, _ensure_dpi_aware

_ensure_windows()

import ctypes
from ctypes import wintypes

_LEFT_BUTTON_DOWN = 0x0002
_LEFT_BUTTON_UP = 0x0004
_RIGHT_BUTTON_DOWN = 0x0008
_RIGHT_BUTTON_UP = 0x0010
_MIDDLE_BUTTON_DOWN = 0x0020
_MIDDLE_BUTTON_UP = 0x0040
_WHEEL = 0x0800
_HORIZONTAL_WHEEL = 0x1000

_user32 = ctypes.WinDLL("user32", use_last_error = True)

class _Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class _MouseInput(ctypes.Structure):
    _fields_ = (
        ("delta_x", wintypes.LONG),
        ("delta_y", wintypes.LONG),
        ("mouse_data", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("extra_information", ctypes.POINTER(ctypes.c_ulong))
    )

class _Input(ctypes.Structure):
    class _InputUnion(ctypes.Union):
        _fields_ = (("mouse_input", _MouseInput),)
    _anonymous_ = ("_input_union",)
    _fields_ = (("type", wintypes.DWORD), ("_input_union", _InputUnion))

def _get_cursor_position():
    _ensure_dpi_aware()
    point = _Point()
    _user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

def _set_cursor_position(x, y):
    _ensure_dpi_aware()
    if not _user32.SetCursorPos(int(x), int(y)): raise ctypes.WinError(ctypes.get_last_error())

def _send_mouse_input(flags, mouse_data = 0):
    input_item = _Input(
        type = 0,
        mouse_input = _MouseInput(
            delta_x = 0,
            delta_y = 0,
            mouse_data = mouse_data,
            flags = flags,
            time = 0,
            extra_information = None
        )
    )
    if _user32.SendInput(1, ctypes.byref(input_item), ctypes.sizeof(_Input)) == 0:
        raise ctypes.WinError(ctypes.get_last_error())

_MOUSE_DOWN_FLAGS = {
    "left": _LEFT_BUTTON_DOWN,
    "right": _RIGHT_BUTTON_DOWN,
    "middle": _MIDDLE_BUTTON_DOWN,
}

_MOUSE_UP_FLAGS = {
    "left": _LEFT_BUTTON_UP,
    "right": _RIGHT_BUTTON_UP,
    "middle": _MIDDLE_BUTTON_UP,
}

_SCROLL_FLAGS = {
    "up": (_WHEEL, 1),
    "down": (_WHEEL, -1),
    "right": (_HORIZONTAL_WHEEL, 1),
    "left": (_HORIZONTAL_WHEEL, -1),
}

def _mouse_down(button):
    _send_mouse_input(_MOUSE_DOWN_FLAGS[button])

def _mouse_up(button):
    _send_mouse_input(_MOUSE_UP_FLAGS[button])

def _scroll(amount, direction):
    flag, sign = _SCROLL_FLAGS[direction]
    _send_mouse_input(flag, mouse_data = int(amount) * sign)