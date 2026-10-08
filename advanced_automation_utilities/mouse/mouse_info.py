from advanced_automation_utilities.screen import ScreenInfo
from ..backend.windows._mouse import _get_cursor_position
from .._typing import ColorFormat
from typing import Optional, Union

class MouseInfo:
    """
    **Description:**

    Provides real-time information about the mouse state.
    """
    @property
    def coordinates(self) -> tuple[int, int]:
        """
        **`MouseInfo().coordinates`:** Gets the current (X, Y) coordinates of the pointer.

        **Description:**

        Reads the system's pointer position and returns it as a tuple. This is an instantaneous, non-blocking hardware read.

        **Returns:**

        **`tuple[int, int]`:** Format: (x, y).

        **Example:**

        ```python
        x, y = MouseInfo().coordinates
        ```
        """
        return _get_cursor_position()

    @property
    def x(self) -> int:
        """
        **`MouseInfo().x`:** Gets the current X coordinate of the pointer.

        **Description:**

        Reads the system's pointer position and extracts only the horizontal axis value.

        **Returns:**

        **`int`**

        **Example:**

        ```python
        x = MouseInfo().x
        ```
        """
        return self.coordinates[0]

    @property
    def y(self) -> int:
        """
        **`MouseInfo().y`:** Gets the current Y coordinate of the pointer.

        **Description:**

        Reads the system's pointer position and extracts only the vertical axis value.

        **Returns:**

        **`int`**

        **Example:**

        ```python
        y = MouseInfo().y
        ```
        """
        return self.coordinates[1]

    def pixel_color(self, format: ColorFormat = "rgb") -> tuple[int, int, int] | str:
        """
        **`MouseInfo().pixel_color()`:** Gets the RGB or hexadecimal color of the pixel currently under the pointer.

        **Description:**

        Takes a micro-screenshot of the exact pixel the mouse is hovering over and extracts its color.

        **Arguments:**

        - **`format` (`str`):** Valid options: "rgb", "hexadecimal". Matching is case-insensitive.

        **Returns:**

        **`tuple[int, int, int]` | `str`**

        **Example:**

        ```python
        pixel_color = MouseInfo().pixel_color(format = "rgb")
        ```
        """
        return ScreenInfo().pixel_color(self.x, self.y, format = format)

    def pixel_matches_color(
        self, expected_color: Union[tuple[int, int, int], str], tolerance: float = 1
    ) -> bool:
        """
        **`MouseInfo().pixel_matches_color()`:** Checks if the pixel currently under the pointer matches a specific color.

        **Description:**

        Takes a micro-screenshot of the exact pixel the mouse is hovering over and compares it with the expected color. If a tolerance is provided, the function will return True if all RGB channels are within the tolerance range.

        **Arguments:**

        - **`expected_color` (`Union[tuple[int, int, int], str]`):** Format: (R, G, B) or "#RRGGBB".
        - **`tolerance` (`float`):** Must be ≥ 0 and ≤ 1.

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        matches = MouseInfo().pixel_matches_color(expected_color = "#FFFFFF", tolerance = 1)
        ```
        """
        return ScreenInfo().pixel_matches_color(
            x = self.x, y = self.y, expected_color = expected_color, tolerance = tolerance
        )

    def on_screen(
        self, region: Optional[tuple[int, int, int, int]] = None, monitor_index: int = 0
    ) -> bool:
        """
        **`MouseInfo().on_screen()`:** Checks if the pointer is currently within the bounds of a screen or region.

        **Description:**

        Verifies if the current mouse coordinates fall inside the designated screen or region. Useful for multi-monitor setups.

        **Arguments:**

        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`monitor_index` (`int`)**

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        is_pointer_on_screen = MouseInfo().on_screen(monitor_index = 0)
        ```

        ### **Keyboard Utilities (keyboard)**

        **Low-level keyboard interaction and information retrieval:**
        """
        return ScreenInfo().on_screen(self.x, self.y, region = region, monitor_index = monitor_index)