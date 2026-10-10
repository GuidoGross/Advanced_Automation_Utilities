from ...exceptions import WindowNotFoundError
import os
import ctypes
lazy import pyperclip
lazy import pygetwindow
lazy import psutil
lazy import subprocess

def _get_clipboard_text(): return pyperclip.paste()

def _set_clipboard_text(text): pyperclip.copy(text)

def _get_active_window_title():
    active_window = pygetwindow.getActiveWindow()
    return active_window.title if active_window else ""

def _is_process_running(process):
    lower_case_process = process.lower()
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] and process.info["name"].lower() == lower_case_process: return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass
    return False

def _open_process(executable_path): os.startfile(executable_path)

def _kill_process(process_name, force):
    lower_case_process = process_name.lower()
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] and process.info["name"].lower() == lower_case_process:
                if force: process.kill()
                else: process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): pass

def _focus_window(title):
    for window in pygetwindow.getWindowsWithTitle(title):
        if window.title == title:
            window.activate()
            return
    raise WindowNotFoundError(f"Window with title \"{title}\" not found.")

def _resize_window(title, width, height):
    for window in pygetwindow.getWindowsWithTitle(title):
        if window.title == title:
            window.resizeTo(int(width), int(height))
            return
    raise WindowNotFoundError(f"Window with title \"{title}\" not found.")

def _move_window(title, x, y):
    for window in pygetwindow.getWindowsWithTitle(title):
        if window.title == title:
            window.moveTo(int(x), int(y))
            return
    raise WindowNotFoundError(f"Window with title \"{title}\" not found.")

def _close_window(title):
    for window in pygetwindow.getWindowsWithTitle(title):
        if window.title == title:
            window.close()
            return
    raise WindowNotFoundError(f"Window with title \"{title}\" not found.")

def _lock_screen(): ctypes.windll.user32.LockWorkStation()

def _sign_out(): subprocess.run(["shutdown", "/l"], creationflags = subprocess.CREATE_NO_WINDOW)

def _sleep(): ctypes.windll.powrprof.SetSuspendState(False, True, False)

def _hibernate(): subprocess.run(["shutdown", "/h"], creationflags = subprocess.CREATE_NO_WINDOW)

def _shutdown(delay = 0):
    subprocess.run(["shutdown", "/s", "/t", str(delay)], creationflags = subprocess.CREATE_NO_WINDOW)

def _restart(delay = 0):
    subprocess.run(["shutdown", "/r", "/t", str(delay)], creationflags = subprocess.CREATE_NO_WINDOW)