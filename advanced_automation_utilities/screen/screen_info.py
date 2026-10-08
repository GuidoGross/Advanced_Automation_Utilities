from .._utilities import _validate_options, _validate_between_range, _validate_region
from ..backend.windows._screen import _get_screen_resolution, _get_pixel_color, _get_work_area
from .._typing import ColorFormat
from typing import Union, Optional
import mss

class ScreenInfo:
    """
    **Description:**

    Provides real-time information about the screen properties and state.
    """
    @property
    def resolution(self) -> tuple[int, int]:
        """
        **`ScreenInfo().resolution`:** Gets the resolution of the primary screen.

        **Description:**

        Returns the resolution of the primary screen as a tuple.

        **Returns:**

        **`tuple[int, int]`:** Format: (width, height).

        **Example:**

        ```python
        width, height = ScreenInfo().resolution
        ```
        """
        return _get_screen_resolution()

    @property
    def width(self) -> int:
        """
        **`ScreenInfo().width`:** Gets the width of the primary screen.

        **Description:**

        Returns only the width of the primary screen as an integer.

        **Returns:**

        **`int`**

        **Example:**

        ```python
        width = ScreenInfo().width
        ```
        """
        return self.resolution[0]

    @property
    def height(self) -> int:
        """
        **`ScreenInfo().height`:** Gets the height of the primary screen.

        **Description:**

        Returns only the height of the primary screen as an integer.

        **Returns:**

        **`int`**

        **Example:**

        ```python
        height = ScreenInfo().height
        ```
        """
        return self.resolution[1]

    def pixel_color(
        self, x: int, y: int, format: ColorFormat = "rgb"
    ) -> Union[tuple[int, int, int], str]:
        """
        **`ScreenInfo().pixel_color()`:** Gets the RGB or hexadecimal color of a specific pixel coordinate.

        **Description:**

        Returns the color of the pixel at the specified coordinates on RGB or hexadecimal format.

        **Arguments:**

        - **`x` (`int`)**
        - **`y` (`int`)**
        - **`format` (`str`):** Valid options: "rgb", "hexadecimal". Matching is case-insensitive.

        **Returns:**

        **`Union[tuple[int, int, int], str]`:** Format: (R, G, B) for "rgb" or "#RRGGBB" for "hexadecimal".

        **Example:**

        ```python
        pixel_color = ScreenInfo().pixel_color(x = 250, y = 500, format = "hexadecimal")
        ```

        ### **Timing Utilities (timing)**

        **Delays, chronometers, and condition-based execution flow:**
        """
        _validate_options(format.lower(), ["rgb", "hexadecimal"], "color format")
        rgb_color = _get_pixel_color(x, y)
        hexadecimal_color = "#{:02x}{:02x}{:02x}".format(rgb_color[0], rgb_color[1], rgb_color[2])
        match format.lower():
            case "rgb": return rgb_color
            case "hexadecimal": return hexadecimal_color

    def pixel_matches_color(
        self, x: int, y: int, expected_color: Union[tuple[int, int, int], str], tolerance: float = 1
    ) -> bool:
        """
        **`ScreenInfo().pixel_matches_color()`:** Checks if a pixel matches a specific color with a given tolerance.

        **Description:**

        Compares the color of the pixel at the specified coordinates with the expected color. If a tolerance is provided, the function will return True if all RGB channels are within the tolerance range.

        **Arguments:**

        - **`x` (`int`)**
        - **`y` (`int`)**
        - **`expected_color` (`Union[tuple[int, int, int], str]`):** Format: (R, G, B) or "#RRGGBB".
        - **`tolerance` (`float`):** Must be ≥ 0 and ≤ 1.

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        matches = ScreenInfo().pixel_matches_color(
            x = 250, y = 500, expected_color = "#FFFFFF", tolerance = 1
        )
        ```
        """
        _validate_between_range(0, 1, tolerance = tolerance)
        if isinstance(expected_color, str):
            expected_color = expected_color.lstrip("#")
            expected_color = tuple(int(expected_color[i:i + 2], 16) for i in (0, 2, 4))
        actual_color = self.pixel_color(x, y, format = "rgb")
        tolerance_value = (1 - tolerance) * 255
        matches = all(
            abs(actual - expected) <= tolerance_value
            for actual, expected in zip(actual_color, expected_color)
        )
        return matches

    def on_screen(
        self, x: int, y: int, region: Optional[tuple[int, int, int, int]] = None, monitor_index: int = 0
    ) -> bool:
        """
        **`ScreenInfo().on_screen()`:** Checks if the given coordinates are within the bounds of a screen or region.

        **Description:**

        Verifies if the specified (x, y) coordinates fall inside the designated screen or region.

        **Arguments:**

        - **`x` (`int`)**
        - **`y` (`int`)**
        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`monitor_index` (`int`)**

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        is_visible = ScreenInfo().on_screen(x = 250, y = 500, monitor_index = 0)
        ```
        """
        if region is not None:
            _validate_region(region)
        _validate_between_range(monitor_index = monitor_index)
        with mss.mss() as screen_capture_tool:
            monitor = screen_capture_tool.monitors[monitor_index]
            if region is not None:
                left = monitor["left"] + region[0]
                top = monitor["top"] + region[1]
                width = region[2] - region[0]
                height = region[3] - region[1]
            else:
                left = monitor["left"]
                top = monitor["top"]
                width = monitor["width"]
                height = monitor["height"]

        return left <= x < left + width and top <= y < top + height

    @property
    def work_area(self) -> tuple[int, int, int, int]:
        """
        **`ScreenInfo().work_area`:** Gets the primary screen's work area, excluding the taskbar.

        **Description:**

        Returns the boundaries of the primary screen's usable work area. This excludes the Windows taskbar and any other docked desktop toolbars, providing the exact coordinates of the space available for applications and windows.

        **Returns:**

        **`tuple[int, int, int, int]`:** Format: (left, top, right, bottom).

        **Example:**

        ```python
        left, top, right, bottom = ScreenInfo().work_area
        ```
        """
        return _get_work_area()