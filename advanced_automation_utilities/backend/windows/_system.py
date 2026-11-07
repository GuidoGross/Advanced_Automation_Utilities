from ._windows_backend_utilities import _ensure_windows, _ensure_dpi_aware

_ensure_windows()

from ...exceptions import WindowNotFoundError
from ctypes import wintypes
import ctypes
import time
import os
lazy import psutil
lazy import subprocess
lazy import shutil

_ENUM_WINDOWS_CALLBACK = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
_CLIPBOARD_OPEN_TIMEOUT = 0.5
_CLIPBOARD_RETRY_INTERVAL = 0.01
_CF_UNICODETEXT = 13
_GMEM_MOVEABLE = 0x0002
_WM_CLOSE = 0x0010
_HWND_TOP = 0
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002

_user32 = ctypes.WinDLL("user32", use_last_error = True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error = True)
_powrprof = ctypes.WinDLL("powrprof", use_last_error = True)
_user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID
]
_user32.CreateWindowExW.restype = wintypes.HWND
_user32.DestroyWindow.argtypes = [wintypes.HWND]
_user32.DestroyWindow.restype = wintypes.BOOL
_user32.OpenClipboard.argtypes = [wintypes.HWND]
_user32.OpenClipboard.restype = wintypes.BOOL
_user32.CloseClipboard.argtypes = []
_user32.CloseClipboard.restype = wintypes.BOOL
_user32.EmptyClipboard.argtypes = []
_user32.EmptyClipboard.restype = wintypes.BOOL
_user32.GetClipboardData.argtypes = [wintypes.UINT]
_user32.GetClipboardData.restype = wintypes.HANDLE
_user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
_user32.SetClipboardData.restype = wintypes.HANDLE
_user32.EnumWindows.argtypes = [_ENUM_WINDOWS_CALLBACK, wintypes.LPARAM]
_user32.EnumWindows.restype = wintypes.BOOL
_user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
_user32.GetWindowTextLengthW.restype = ctypes.c_int
_user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
_user32.GetWindowTextW.restype = ctypes.c_int
_user32.IsWindowVisible.argtypes = [wintypes.HWND]
_user32.IsWindowVisible.restype = wintypes.BOOL
_user32.GetForegroundWindow.argtypes = []
_user32.GetForegroundWindow.restype = wintypes.HWND
_user32.SetForegroundWindow.argtypes = [wintypes.HWND]
_user32.SetForegroundWindow.restype = wintypes.BOOL
_user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT
]
_user32.SetWindowPos.restype = wintypes.BOOL
_user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
_user32.PostMessageW.restype = wintypes.BOOL
_kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
_kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
_kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
_kernel32.GlobalLock.restype = wintypes.LPVOID
_kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
_kernel32.GlobalUnlock.restype = wintypes.BOOL
_kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
_kernel32.GlobalFree.restype = wintypes.HGLOBAL

def _open_clipboard(owner_window):
    deadline = time.perf_counter() + _CLIPBOARD_OPEN_TIMEOUT
    while True:
        if _user32.OpenClipboard(owner_window): return
        if time.perf_counter() >= deadline:
            raise OSError("Could not open the Windows clipboard.")
        time.sleep(_CLIPBOARD_RETRY_INTERVAL)

def _get_clipboard_text():
    _open_clipboard(None)
    try:
        clipboard_handle = _user32.GetClipboardData(_CF_UNICODETEXT)
        if not clipboard_handle:
            return ""
        locked_memory = _kernel32.GlobalLock(clipboard_handle)
        if not locked_memory: raise OSError("Could not read text from the Windows clipboard.")
        try: return ctypes.wstring_at(locked_memory)
        finally: _kernel32.GlobalUnlock(clipboard_handle)
    finally: _user32.CloseClipboard()

def _set_clipboard_text(text):
    owner_window = _user32.CreateWindowExW(0, "STATIC", "", 0, 0, 0, 0, 0, None, None, None, None)
    if not owner_window:
        raise OSError("Could not create a clipboard owner window.")
    clipboard_open = False
    memory_handle = None
    try:
        _open_clipboard(owner_window)
        clipboard_open = True
        if not _user32.EmptyClipboard(): raise OSError("Could not empty the Windows clipboard.")
        text = str(text)
        if text:
            text_buffer = ctypes.create_unicode_buffer(text)
            memory_handle = _kernel32.GlobalAlloc(_GMEM_MOVEABLE, ctypes.sizeof(text_buffer))
            if not memory_handle: raise OSError("Could not allocate clipboard text memory.")
            locked_memory = _kernel32.GlobalLock(memory_handle)
            if not locked_memory: raise OSError("Could not lock clipboard text memory.")
            try:
                ctypes.memmove(locked_memory, ctypes.addressof(text_buffer), ctypes.sizeof(text_buffer))
            finally: _kernel32.GlobalUnlock(memory_handle)
            if not _user32.SetClipboardData(_CF_UNICODETEXT, memory_handle):
                raise OSError("Could not set text in the Windows clipboard.")
            memory_handle = None
    finally:
        if clipboard_open: _user32.CloseClipboard()
        if memory_handle: _kernel32.GlobalFree(memory_handle)
        _user32.DestroyWindow(owner_window)

def _is_process_running(process):
    lower_case_process = process.lower()
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] and process.info["name"].lower() == lower_case_process: return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
    return False

def _open_file(file_path):
    resolved_path = shutil.which(file_path) or os.path.abspath(file_path)
    extension = os.path.splitext(resolved_path)[1].lower()
    if os.path.isfile(resolved_path) and extension in {".exe", ".com"}:
        subprocess.Popen([resolved_path], cwd = os.path.dirname(resolved_path))
    elif os.path.isfile(resolved_path) and extension in {".bat", ".cmd"}:
        subprocess.Popen(["cmd.exe", "/d", "/c", resolved_path], cwd = os.path.dirname(resolved_path))
    else: os.startfile(file_path)

def _kill_process(process_name, force):
    lower_case_process = process_name.lower()
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] and process.info["name"].lower() == lower_case_process:
                process.kill() if force else process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass

def _get_window_title(window_handle):
    title_length = _user32.GetWindowTextLengthW(window_handle)
    title_buffer = ctypes.create_unicode_buffer(title_length + 1)
    _user32.GetWindowTextW(window_handle, title_buffer, title_length + 1)
    return title_buffer.value

def _get_active_window_title():
    active_window = _user32.GetForegroundWindow()
    return _get_window_title(active_window) if active_window else ""

def _find_window(title):
    matching_windows = []

    def add_matching_window(window_handle, _):
        if _user32.IsWindowVisible(window_handle) and _get_window_title(window_handle) == title:
            matching_windows.append(window_handle)
        return True

    if not _user32.EnumWindows(_ENUM_WINDOWS_CALLBACK(add_matching_window), 0):
        raise OSError("Could not enumerate Windows windows.")
    if not matching_windows:
        raise WindowNotFoundError(f"Window with title \"{title}\" not found.")
    return matching_windows[0]

def _focus_window(title):
    window_handle = _find_window(title)
    if not _user32.SetForegroundWindow(window_handle):
        raise OSError(f"Could not focus the window with title \"{title}\".")

def _resize_window(title, width, height):
    _ensure_dpi_aware()
    window_handle = _find_window(title)
    if not _user32.SetWindowPos(window_handle, _HWND_TOP, 0, 0, int(width), int(height), _SWP_NOMOVE):
        raise OSError(f"Could not resize the window with title \"{title}\".")

def _move_window(title, x, y):
    _ensure_dpi_aware()
    window_handle = _find_window(title)
    if not _user32.SetWindowPos(window_handle, _HWND_TOP, int(x), int(y), 0, 0, _SWP_NOSIZE):
        raise OSError(f"Could not move the window with title \"{title}\".")

def _close_window(title):
    window_handle = _find_window(title)
    if not _user32.PostMessageW(window_handle, _WM_CLOSE, 0, 0):
        raise OSError(f"Could not close the window with title \"{title}\".")

def _lock_screen():
    _user32.LockWorkStation()

def _sign_out():
    subprocess.run(["shutdown", "/l"], creationflags = subprocess.CREATE_NO_WINDOW)

def _sleep():
    _powrprof.SetSuspendState(False, True, False)

def _hibernate():
    subprocess.run(["shutdown", "/h"], creationflags = subprocess.CREATE_NO_WINDOW)

def _shutdown(delay = 0):
    subprocess.run(["shutdown", "/s", "/t", str(delay)], creationflags = subprocess.CREATE_NO_WINDOW)

def _restart(delay = 0):
    subprocess.run(["shutdown", "/r", "/t", str(delay)], creationflags = subprocess.CREATE_NO_WINDOW)