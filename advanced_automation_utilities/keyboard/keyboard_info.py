from ..backend.windows._keyboard import _get_virtual_key_code, _is_pressed

class KeyboardInfo:
    """
    **`KeyboardInfo`:** Reads the current physical state of keyboard keys.

    **Description:**

    Provides real-time information about the keyboard state.
    """
    def is_pressed(self, key: str) -> bool:
        """
        **`KeyboardInfo().is_pressed()`:** Returns True if the specified key is currently physically held down.

        **Description:**

        Reads the hardware state asynchronously, capturing even keys pressed outside the script.

        **Arguments:**

        - **`key` (`str`)**

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        is_shift_down = KeyboardInfo().is_pressed(key = "shift")
        ```
        """
        if not _get_virtual_key_code(key):
            raise KeyError(f"The \"{key}\" key is not valid or supported.")
        return _is_pressed(key)