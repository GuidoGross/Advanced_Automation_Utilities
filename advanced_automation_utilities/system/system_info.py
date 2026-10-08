from ..backend.windows._system import _get_clipboard_text, _get_active_window_title, _is_process_running

class SystemInfo:
    """
    **Description:**

    Provides real-time information about the operating system and hardware.
    """
    @property
    def clipboard_text(self) -> str:
        """
        **`SystemInfo().clipboard_text`:** Gets the current text content of the Windows clipboard.

        **Description:**

        Gets the current text content of the Windows clipboard. This allows your scripts to seamlessly read and process text that the user or other applications have recently copied.

        **Returns:**

        **`str`**

        **Example:**

        ```python
        text = SystemInfo().clipboard_text
        ```
        """
        return _get_clipboard_text()

    @property
    def active_window_title(self) -> str:
        """
        **`SystemInfo().active_window_title`:** Gets the title of the currently focused/active window.

        **Description:**

        Gets the title of the currently focused/active window. This allows your scripts to interact with the active window or to determine which application the user is currently using.

        **Returns:**

        **`str`**

        **Example:**

        ```python
        title = SystemInfo().active_window_title
        ```
        """
        return _get_active_window_title()

    def is_process_running(self, process: str) -> bool:
        """
        **`SystemInfo().is_process_running()`:** Checks if a specific process is currently running.

        **Description:**

        Checks if a specific process is currently running. This allows your scripts to determine if an application is active or not.

        **Arguments:**

        - **`process` (`str`)**

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        is_running = SystemInfo().is_process_running(process = "notepad.exe")
        ```
        """
        return _is_process_running(process)