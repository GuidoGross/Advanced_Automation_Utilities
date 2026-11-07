import os

def _ensure_windows():
    if os.name != "nt":
        raise NotImplementedError(
            "Advanced Automation Utilities is currently only supported on Windows."
        )

_ensure_windows()

import ctypes

_user32 = ctypes.WinDLL("user32", use_last_error = True)
_dpi_initialized = False

def _ensure_dpi_aware():
    global _dpi_initialized
    if not _dpi_initialized:
        try: _user32.SetProcessDPIAware()
        except Exception: pass
        _dpi_initialized = True