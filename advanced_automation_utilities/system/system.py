from ._set_clipboard_text import _SetClipboardText
from ._open_process import _OpenProcess
from ._kill_process import _KillProcess
from ._focus_window import _FocusWindow
from ._resize_window import _ResizeWindow
from ._move_window import _MoveWindow
from ._close_window import _CloseWindow
from ._lock_screen import _LockScreen
from ._sign_out import _SignOut
from ._sleep import _Sleep
from ._hibernate import _Hibernate
from ._shutdown import _Shutdown
from ._restart import _Restart
from ._enable_kill_switch import _EnableKillSwitch
from ._disable_kill_switch import _DisableKillSwitch
from .._queueable_controller import _QueueableController
from typing import Self

class System(_QueueableController):
    """
    **Description:**

    High-level operating system actions and process management. This module provides a robust interface to manage the Windows clipboard, window states, process termination, and power options like sleeping, hibernating, and system reboots.
    """
    def __init__(self) -> None:
        """
        **Description:**

        Initializes the System controller.

        **Returns:**

        **`None`**
        """
        super().__init__()

    def set_clipboard_text(self, text: str) -> Self:
        """
        **`System().set_clipboard_text()`:** Sets the text content of the Windows clipboard.

        **Description:**

        Sets the text content of the Windows clipboard. This is extremely useful for automating copy-paste workflows or seamlessly transferring data from your script to other applications.

        **Arguments:**

        - **`text` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().set_clipboard_text(text = "Text to paste later.")
        ```
        """
        return self._execute_or_queue(_SetClipboardText(text = text))

    def open_process(self, process_path: str) -> Self:
        """
        **`System().open_process()`:** Opens a process or file.

        **Description:**

        Uses `os.startfile` internally to launch applications or open files with their default program.

        **Arguments:**

        - **`executable_path` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().open_process(process_path = "notepad.exe")
        ```
        """
        return self._execute_or_queue(_OpenProcess(process_path = process_path))

    def kill_process(self, process: str, force: bool = True) -> Self:
        """
        **`System().kill_process()`:** Terminates an active process by its name.

        **Description:**

        Terminates an active process by its name. This provides a robust way to clean up applications after an automation task finishes, or to forcefully close unresponsive programs.

        **Arguments:**

        - **`process` (`str`)**
        - **`force` (`bool`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().kill_process(process = "notepad.exe", force = True)
        ```
        """
        return self._execute_or_queue(_KillProcess(process = process, force = force))

    def focus_window(self, window_title: str) -> Self:
        """
        **`System().focus_window()`:** Brings a specific window to the foreground by its title.

        **Description:**

        Brings a specific window to the foreground by its title. This is essential for ensuring that subsequent mouse clicks and keyboard strokes are sent to the correct application, avoiding accidental interactions with background apps.

        **Arguments:**

        - **`window_title` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().focus_window(window_title = "Untitled - Notepad")
        ```
        """
        return self._execute_or_queue(_FocusWindow(window_title = window_title))

    def resize_window(self, window_title: str, width: int, height: int) -> Self:
        """
        **`System().resize_window()`:** Resizes a specific window to the specified dimensions by its title.

        **Description:**

        Resizes a specific window to the specified dimensions by its title. This is extremely useful for automating GUI applications or ensuring that a window occupies the exact screen space required for subsequent automation steps.

        **Arguments:**

        - **`window_title` (`str`)**
        - **`width` (`int`):** Must be > 0.
        - **`height` (`int`):** Must be > 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().resize_window(window_title = "Untitled - Notepad", width = 800, height = 600)
        ```
        """
        return self._execute_or_queue(
            _ResizeWindow(window_title = window_title, width = width, height = height)
        )

    def move_window(self, window_title: str, x: int, y: int) -> Self:
        """
        **`System().move_window()`:** Moves a specific window to the specified coordinates by its title.

        **Description:**

        Moves a specific window to the specified coordinates by its title. Similar to `resize_window()`, this helps guarantee that your automation target is perfectly positioned before executing coordinate-based mouse interactions.

        **Arguments:**

        - **`window_title` (`str`)**
        - **`x` (`int`)**
        - **`y` (`int`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().move_window(window_title = "Untitled - Notepad", x = 250, y = 500)
        ```
        """
        return self._execute_or_queue(_MoveWindow(window_title = window_title, x = x, y = y))

    def close_window(self, window_title: str) -> Self:
        """
        **`System().close_window()`:** Gently closes a specific window by its title.

        **Description:**

        Sends a graceful WM_CLOSE signal to a specific window by its title.

        **Arguments:**

        - **`window_title` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().close_window(window_title = "Untitled - Notepad")
        ```
        """
        return self._execute_or_queue(_CloseWindow(window_title = window_title))

    def lock_screen(self) -> Self:
        """
        **`System().lock_screen()`:** Locks the Windows session (Win+L).

        **Description:**

        Locks the Windows session (equivalent to pressing Win+L). This is ideal for scripts that handle sensitive information and need to secure the computer immediately after the automated task finishes.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().lock_screen()
        ```
        """
        return self._execute_or_queue(_LockScreen())

    def sign_out(self) -> Self:
        """
        **`System().sign_out()`:** Signs out the current Windows user.

        **Description:**

        Signs out the current Windows user. This gently closes all running applications and returns to the Windows login screen, making it useful for gracefully ending a day's worth of automated tasks.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().sign_out()
        ```
        """
        return self._execute_or_queue(_SignOut())

    def sleep(self) -> Self:
        """
        **`System().sleep()`:** Puts the computer into sleep mode.

        **Description:**

        Puts the computer into sleep mode (suspend to RAM). This is a great way to save energy when an automation task finishes running overnight without completely turning off the machine.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().sleep()
        ```
        """
        return self._execute_or_queue(_Sleep())

    def hibernate(self) -> Self:
        """
        **`System().hibernate()`:** Puts the computer into hibernation mode.

        **Description:**

        Puts the computer into hibernation mode (suspend to disk). This completely powers off the machine while saving the exact state of all open applications, allowing you to seamlessly resume your work later.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().hibernate()
        ```
        """
        return self._execute_or_queue(_Hibernate())

    def shutdown(self, delay: int = 0) -> Self:
        """
        **`System().shutdown()`:** Turns off the computer.

        **Description:**

        Turns off the computer, optionally waiting for a specified delay before powering down. This is perfect for cleanly shutting down a remote or unattended machine after a long-running automation process finishes.

        **Arguments:**

        - **`delay` (`int`):** Seconds. Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().shutdown(delay = 60)
        ```
        """
        return self._execute_or_queue(_Shutdown(delay = delay))

    def restart(self, delay: int = 0) -> Self:
        """
        **`System().restart()`:** Restarts the computer.

        **Description:**

        Restarts the computer, optionally waiting for a specified delay before rebooting. This is useful for applying system updates or resetting the environment before starting a fresh automation cycle.

        **Arguments:**

        - **`delay` (`int`):** Seconds. Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().restart(delay = 60)
        ```
        """
        return self._execute_or_queue(_Restart(delay = delay))

    def enable_kill_switch(self, *keys: str) -> Self:
        """
        **`System().enable_kill_switch()`:** Enables a global kill switch to abort execution instantly.

        **Description:**

        Injects a high-priority hardware hook to listen for the abort shortcut.

        **Arguments:**

        - **`*keys` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().enable_kill_switch("ctrl", "shift", "alt", "k")
        ```

        **Important:**

        When triggered, an asynchronous `KillSwitchTriggered` exception is raised in all automation threads, completely aborting execution safely.
        """
        if not keys: keys = ("ctrl", "shift", "alt", "k")
        return self._execute_or_queue(_EnableKillSwitch(*keys))

    def disable_kill_switch(self) -> Self:
        """
        **`System().disable_kill_switch()`:** Disables the global kill switch.

        **Description:**

        Safely unregisters the hook to disable the kill switch.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        System().disable_kill_switch()
        ```
        """
        return self._execute_or_queue(_DisableKillSwitch())