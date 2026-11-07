from ._windows_backend_utilities import _ensure_windows

_ensure_windows()

from ..._kill_switch_event import trigger_kill_switch
import ctypes
from ctypes import wintypes
import threading

_KEY_UP = 0x0002
_SHIFT_VIRTUAL_KEY = 0x10
_CONTROL_VIRTUAL_KEY = 0x11
_ALT_VIRTUAL_KEY = 0x12
_UNICODE = 0x0004
_KEY_PRESSED = 0x8000
_INJECTED = 0x10
_WINDOW_MESSAGE_KEY_DOWN = 0x0100
_WINDOW_MESSAGE_SYSTEM_KEY_DOWN = 0x0104
_WINDOW_MESSAGE_KEY_UP = 0x0101
_WINDOW_MESSAGE_SYSTEM_KEY_UP = 0x0105
_WINDOWS_HOOK_KEYBOARD_LOW_LEVEL = 13
_VIRTUAL_KEY_CODES = {
    "backspace":         0x08, "tab":               0x09, "clear":             0x0C,
    "enter":             0x0D, "shift":             0x10, "ctrl":              0x11,
    "alt":               0x12, "pause":             0x13, "caps_lock":         0x14,
    "esc":               0x1B, "space":             0x20, "page_up":           0x21,
    "page_down":         0x22, "end":               0x23, "home":              0x24,
    "left_arrow":        0x25, "up_arrow":          0x26, "right_arrow":       0x27,
    "down_arrow":        0x28, "select":            0x29, "print":             0x2A,
    "execute":           0x2B, "print_screen":      0x2C, "insert":            0x2D,
    "delete":            0x2E, "help":              0x2F, "0":                 0x30,
    "1":                 0x31, "2":                 0x32, "3":                 0x33,
    "4":                 0x34, "5":                 0x35, "6":                 0x36,
    "7":                 0x37, "8":                 0x38, "9":                 0x39,
    "a":                 0x41, "b":                 0x42, "c":                 0x43,
    "d":                 0x44, "e":                 0x45, "f":                 0x46,
    "g":                 0x47, "h":                 0x48, "i":                 0x49,
    "j":                 0x4A, "k":                 0x4B, "l":                 0x4C,
    "m":                 0x4D, "n":                 0x4E, "o":                 0x4F,
    "p":                 0x50, "q":                 0x51, "r":                 0x52,
    "s":                 0x53, "t":                 0x54, "u":                 0x55,
    "v":                 0x56, "w":                 0x57, "x":                 0x58,
    "y":                 0x59, "z":                 0x5A, "windows":           0x5B,
    "menu":              0x5D, "sleep":             0x5F, "numpad_0":          0x60,
    "numpad_1":          0x61, "numpad_2":          0x62, "numpad_3":          0x63,
    "numpad_4":          0x64, "numpad_5":          0x65, "numpad_6":          0x66,
    "numpad_7":          0x67, "numpad_8":          0x68, "numpad_9":          0x69,
    "multiply_key":      0x6A, "add_key":           0x6B, "separator_key":     0x6C,
    "subtract_key":      0x6D, "decimal_key":       0x6E, "divide_key":        0x6F,
    "f1":                0x70, "f2":                0x71, "f3":                0x72,
    "f4":                0x73, "f5":                0x74, "f6":                0x75,
    "f7":                0x76, "f8":                0x77, "f9":                0x78,
    "f10":               0x79, "f11":               0x7A, "f12":               0x7B,
    "num_lock":          0x90, "scroll_lock":       0x91, "browser_back":      0xA6,
    "browser_forward":   0xA7, "browser_refresh":   0xA8, "browser_stop":      0xA9,
    "browser_search":    0xAA, "browser_favorites": 0xAB, "browser_home":      0xAC,
    "volume_mute":       0xAD, "volume_down":       0xAE, "volume_up":         0xAF,
    "media_next":        0xB0, "media_prev":        0xB1, "media_stop":        0xB2,
    "media_play_pause":  0xB3, "zoom":              0xFB
}

_blocked_keys = set()
_key_states = {}
_hook_id = None
_hook_function = None
_hook_thread = None
_hook_ready_event = threading.Event()
_hook_error = 0
_kill_switch_enabled = False
_kill_switch_key = 0
_kill_switch_modifiers = []
_user32 = ctypes.WinDLL("user32", use_last_error = True)

class _MouseInput(ctypes.Structure):
    _fields_ = (
        ("delta_x", wintypes.LONG),
        ("delta_y", wintypes.LONG),
        ("mouse_data", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("extra_information", ctypes.POINTER(ctypes.c_ulong))
    )

class _KeyboardInput(ctypes.Structure):
    _fields_ = (
        ("virtual_key_code", wintypes.WORD),
        ("scan_code", wintypes.WORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("extra_information", ctypes.POINTER(ctypes.c_ulong))
    )

class _HardwareInput(ctypes.Structure):
    _fields_ = (
        ("message", wintypes.DWORD),
        ("word_parameter_low", wintypes.WORD),
        ("word_parameter_high", wintypes.WORD)
    )

class _Input(ctypes.Structure):
    class _InputUnion(ctypes.Union):
        _fields_ = (
            ("keyboard_input", _KeyboardInput),
            ("mouse_input", _MouseInput),
            ("hardware_input", _HardwareInput)
        )
    _anonymous_ = ("_input_union",)
    _fields_ = (("type", wintypes.DWORD), ("_input_union", _InputUnion))

class _KeyboardHookStruct(ctypes.Structure):
    _fields_ = [
        ("virtual_key_code", wintypes.DWORD),
        ("scan_code", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("extra_information", ctypes.POINTER(ctypes.c_ulong))
    ]

def _send_key(key, key_released = False):
    virtual_key_result = _get_virtual_key_code(key)
    if not virtual_key_result: return
    virtual_key_code, modifiers = virtual_key_result
    inputs = []
    flags = _KEY_UP if key_released else 0
    if key_released:
        inputs.append(
            _Input(
                type = 1,
                keyboard_input = _KeyboardInput(virtual_key_code = virtual_key_code, flags = flags)
            )
        )
    for bit, modifier_virtual_key in ((1, _SHIFT_VIRTUAL_KEY), (2, _CONTROL_VIRTUAL_KEY), (4, _ALT_VIRTUAL_KEY)):
        if modifiers & bit:
            inputs.append(
                _Input(
                    type = 1,
                    keyboard_input = _KeyboardInput(
                        virtual_key_code = modifier_virtual_key, flags = flags
                    )
                )
            )
    if not key_released:
        inputs.append(
            _Input(
                type = 1, keyboard_input = _KeyboardInput(
                    virtual_key_code = virtual_key_code, flags = flags
                )
            )
        )
    input_array_type = _Input * len(inputs)
    input_array = input_array_type(*inputs)
    if _user32.SendInput(len(inputs), ctypes.byref(input_array), ctypes.sizeof(_Input)) != len(inputs):
        raise ctypes.WinError(ctypes.get_last_error())

def _send_unicode(text):
    for character in text:
        surrogate = character.encode("utf-16-le")
        for index in range(0, len(surrogate), 2):
            code = int.from_bytes(surrogate[index: index + 2], "little")
            input_down = _Input(
                type = 1,
                keyboard_input = _KeyboardInput(
                    virtual_key_code = 0, scan_code = code, flags = _UNICODE, time = 0
                )
            )
            if _user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(input_down)) == 0:
                raise ctypes.WinError(ctypes.get_last_error())
            input_up = _Input(
                type = 1,
                keyboard_input = _KeyboardInput(
                    virtual_key_code = 0, scan_code = code, flags = _UNICODE | _KEY_UP, time = 0
                )
            )
            if _user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(input_up)) == 0:
                raise ctypes.WinError(ctypes.get_last_error())

def _is_pressed(key):
    virtual_key_result = _get_virtual_key_code(key)
    if not virtual_key_result: return False
    virtual_key_code, _ = virtual_key_result
    if _key_states.get(virtual_key_code, False): return True
    return (_user32.GetAsyncKeyState(virtual_key_code) & _KEY_PRESSED) != 0

def _block_key(key):
    virtual_key_result = _get_virtual_key_code(key)
    if virtual_key_result:
        virtual_key_code, _ = virtual_key_result
        _blocked_keys.add(virtual_key_code)
        _ensure_hook()

def _unblock_key(key):
    virtual_key_result = _get_virtual_key_code(key)
    if virtual_key_result:
        virtual_key_code, _ = virtual_key_result
        if virtual_key_code in _blocked_keys: _blocked_keys.remove(virtual_key_code)
    _unhook_if_idle()

def _enable_kill_switch(keys):
    global _kill_switch_enabled, _kill_switch_key, _kill_switch_modifiers
    if not keys: return
    main_result = _get_virtual_key_code(keys[-1])
    if not main_result: return
    main_key, _ = main_result
    modifiers = []
    for modifier in keys[:-1]:
        modifier_result = _get_virtual_key_code(modifier)
        if modifier_result: modifiers.append(modifier_result[0])
    _kill_switch_key = main_key
    _kill_switch_modifiers = modifiers
    _kill_switch_enabled = True
    _ensure_hook()

def _disable_kill_switch():
    global _kill_switch_enabled
    _kill_switch_enabled = False
    _unhook_if_idle()

def _get_virtual_key_code(key):
    key_lower = key.lower()
    if key_lower in _VIRTUAL_KEY_CODES: return _VIRTUAL_KEY_CODES[key_lower], 0
    if len(key) == 1:
        virtual_key = _user32.VkKeyScanW(ord(key))
        if virtual_key == -1: return None
        return virtual_key & 0xFF, virtual_key >> 8
    return None

def _ensure_hook():
    global _hook_thread
    if _hook_thread is None or not _hook_thread.is_alive():
        _hook_ready_event.clear()
        _hook_thread = threading.Thread(target = _hook_worker, daemon = True)
        _hook_thread.start()
        _hook_ready_event.wait()
        if not _hook_id: raise OSError(_hook_error, "Failed to install low-level keyboard hook.")

_HookProcedure = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
_user32.SetWindowsHookExW.argtypes = [ctypes.c_int, _HookProcedure, wintypes.HINSTANCE, wintypes.DWORD]
_user32.SetWindowsHookExW.restype = wintypes.HHOOK
_user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
_user32.CallNextHookEx.restype = wintypes.LPARAM
_user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
_user32.UnhookWindowsHookEx.restype = wintypes.BOOL
_user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
_user32.PostThreadMessageW.restype = wintypes.BOOL

def _hook_worker():
    global _hook_id, _hook_function, _hook_error
    def _low_level_keyboard_handler(hook_code, window_message, hook_data):
        if hook_code >= 0:
            hook_struct = ctypes.cast(hook_data, ctypes.POINTER(_KeyboardHookStruct)).contents
            virtual_key = hook_struct.virtual_key_code
            flags = hook_struct.flags
            is_injected = (flags & _INJECTED) != 0
            if window_message in (_WINDOW_MESSAGE_KEY_DOWN, _WINDOW_MESSAGE_SYSTEM_KEY_DOWN):
                _key_states[virtual_key] = True
                if _kill_switch_enabled and virtual_key == _kill_switch_key:
                    all_modifiers_pressed = True
                    for modifier in _kill_switch_modifiers:
                        if not _key_states.get(modifier, False) and not (_user32.GetAsyncKeyState(modifier) & _KEY_PRESSED):
                            all_modifiers_pressed = False
                            break
                    if all_modifiers_pressed:
                        trigger_kill_switch()
                        return 1
            elif window_message in (_WINDOW_MESSAGE_KEY_UP, _WINDOW_MESSAGE_SYSTEM_KEY_UP):
                _key_states[virtual_key] = False
            if virtual_key in _blocked_keys and not is_injected: return 1
        return _user32.CallNextHookEx(_hook_id, hook_code, window_message, hook_data)
    _hook_function = _HookProcedure(_low_level_keyboard_handler)
    _hook_id = _user32.SetWindowsHookExW(_WINDOWS_HOOK_KEYBOARD_LOW_LEVEL, _hook_function, None, 0)
    if not _hook_id: _hook_error = ctypes.get_last_error()
    _hook_ready_event.set()
    if not _hook_id: return
    message = wintypes.MSG()
    while _user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
        _user32.TranslateMessage(ctypes.byref(message))
        _user32.DispatchMessageW(ctypes.byref(message))

def _unhook_if_idle():
    global _hook_id, _hook_function, _hook_thread
    if not _blocked_keys and not _kill_switch_enabled and _hook_id:
        _user32.UnhookWindowsHookEx(_hook_id)
        if _hook_thread and _hook_thread.is_alive():
            _user32.PostThreadMessageW(_hook_thread.native_id, 0x0012, 0, 0)
            _hook_thread.join(timeout = 0.5)
            _hook_thread = None
        _hook_id = None
        _hook_function = None
        _key_states.clear()