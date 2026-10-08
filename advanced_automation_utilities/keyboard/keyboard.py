from .keyboard_physics import KeyboardPhysics
from ._hold_key import _HoldKey
from ._release_key import _ReleaseKey
from ._press_key import _PressKey
from ._hotkey import _Hotkey
from ._block_key import _BlockKey
from ._unblock_key import _UnblockKey
from ._write import _Write
from .._queueable_controller import _QueueableController
from typing import Optional, Self

class Keyboard(_QueueableController):
    """
    **Description:**

    Low-level keyboard interaction and hardware state retrieval. Simulates human typing with configurable physics, handles complex hotkey combinations, and can selectively block physical hardware inputs to prevent interference during critical automation tasks.
    """
    def __init__(self, physics: Optional[KeyboardPhysics] = None) -> None:
        """
        **Description:**

        Initializes the Keyboard controller.

        **Arguments:**

        - **`physics` (`Optional[KeyboardPhysics]`)**

        **Returns:**

        **`None`**
        """
        super().__init__()
        self.physics = physics or KeyboardPhysics()

    def hold_key(self, key: str) -> Self:
        """
        **`Keyboard().hold_key()`:** Holds a key down.

        **Description:**

        Sends a physical DOWN signal for the key without releasing it.

        **Arguments:**

        - **`key` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Keyboard().hold_key(key = "shift")
        ```

        **Warning:**

        Make sure to call `release_key()` to prevent the key from getting physically stuck.
        """
        return self._execute_or_queue(_HoldKey(key = key, physics = self.physics))

    def release_key(self, key: str) -> Self:
        """
        **`Keyboard().release_key()`:** Releases a previously held key.

        **Description:**

        Sends the physical UP signal for the key.

        **Arguments:**

        - **`key` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Keyboard().release_key(key = "shift")
        ```
        """
        return self._execute_or_queue(_ReleaseKey(key = key, physics = self.physics))

    def press_key(self, key: str) -> Self:
        """
        **`Keyboard().press_key()`:** Presses and releases a single key.

        **Description:**

        Sends a physical DOWN signal followed instantly by an UP signal for the specified key.

        **Arguments:**

        - **`key` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Keyboard().press_key(key = "a")
        ```
        """
        return self._execute_or_queue(_PressKey(key = key, physics = self.physics))

    def hotkey(self, *keys: str) -> Self:
        """
        **`Keyboard().hotkey()`:** Holds down a combination of keys and releases them in reverse order.

        **Description:**

        Sequentially holds all provided keys with a tiny human delay between each, waits for a moment, and then releases them in reverse to ensure the OS registers the shortcut properly.

        **Arguments:**

        - **`*keys` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Keyboard().hotkey("ctrl", "shift", "esc")
        ```
        """
        return self._execute_or_queue(_Hotkey(*keys, physics = self.physics))

    def block_key(self, key: str) -> Self:
        """
        **`Keyboard().block_key()`:** Blocks all physical input from a specific key.

        **Description:**

        Uses a low-level C hook to intercept and discard any hardware events from this key. Useful for preventing user interference during automation.

        **Arguments:**

        - **`key` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Keyboard().block_key(key = "esc")
        ```

        **Tip:**

        This blocks PHYSICAL input. The script can still simulate presses for this key perfectly fine.
        """
        return self._execute_or_queue(_BlockKey(key = key))

    def unblock_key(self, key: str) -> Self:
        """
        **`Keyboard().unblock_key()`:** Unblocks a previously blocked key.

        **Description:**

        Restores physical input functionality for the key.

        **Arguments:**

        - **`key` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Keyboard().unblock_key(key = "esc")
        ```
        """
        return self._execute_or_queue(_UnblockKey(key = key))

    def write(self, text: str) -> Self:
        """
        **`Keyboard().write()`:** Types a string character by character with advanced, human-like typing error simulations and delays, based on the configured physics.

        **Description:**

        Rather than instantly pasting text, this method allows the user to simulate a human typing on a keyboard. It can even make random typos, realize the mistake a few characters later, hit backspace to fix it, and resume typing.

        **Arguments:**

        - **`text` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Keyboard().write(text = "Hello, world!")
        ```
        """
        return self._execute_or_queue(_Write(text = text, physics = self.physics))