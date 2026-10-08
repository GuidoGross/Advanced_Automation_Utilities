from ._locate_image import _LocateImage
from ._read_text import _ReadText
from ._locate_text import _LocateText
from ._take_screenshot import _TakeScreenshot
from typing import Optional, Union
import mss.base

class Screen:
    """
    **Description:**

    Advanced computer vision leveraging OpenCV and native Windows OCR. Read text from specific regions, locate UI elements via template matching, and interact with pixel-perfect accuracy across multi-monitor setups without requiring external cloud services.
    """
    def take_screenshot(
        self,
        region: Optional[tuple[int, int, int, int]] = None,
        monitor_index: int = 0,
        save_path: Optional[str] = None
    ) -> mss.base.ScreenShot:
        """
        **`Screen().take_screenshot()`:** Takes a screenshot of the screen or a specific region.

        **Description:**

        Takes a blazing-fast screenshot using `mss`. Optionally saves it to a file.

        **Arguments:**

        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`monitor_index` (`int`)**
        - **`save_path` (`Optional[str]`):** Must be a valid file path.

        **Returns:**

        **`mss.base.ScreenShot`**

        **Example:**

        ```python
        screenshot = Screen().take_screenshot(
            region = (250, 250, 500, 500),
            monitor_index = 0,
            save_path = "screenshot.png"
        )
        ```
        """
        return _TakeScreenshot(
            region = region, monitor_index = monitor_index, save_path = save_path
        ).execute()

    def locate_image(
        self,
        image_path: str,
        confidence: float = 0.9,
        limit: int = 1,
        region: Optional[tuple[int, int, int, int]] = None,
        monitor_index: int = 0
    ) -> Union[tuple[Optional[int], Optional[int]], list[tuple[int, int]]]:
        """
        **`Screen().locate_image()`:** Searches for a template image on the screen and returns its central coordinates.

        **Description:**

        Takes a fast screenshot and uses OpenCV Template Matching (`TM_CCOEFF_NORMED`) to find the image in the specified region.

        **Arguments:**

        - **`image_path` (`str`):** Must be a valid file path.
        - **`confidence` (`float`):** Must be ≥ 0 and ≤ 1.
        - **`limit` (`int`):** Must be ≥ 0.
        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`monitor_index` (`int`)**

        **Returns:**

        **`Union[tuple[Optional[int], Optional[int]], list[tuple[int, int]]]`:** Format: (x, y) or a list of them.

        **Example:**

        ```python
        x, y = Screen().locate_image(
            image_path = "button.png",
            confidence = 0.9,
            limit = 1,
            region = (250, 250, 500, 500),
            monitor_index = 0
        )
        ```
        """
        return _LocateImage(
            image_path = image_path,
            confidence = confidence,
            limit = limit,
            region = region,
            monitor_index = monitor_index
        ).execute()

    def read_text(
        self, region: Optional[tuple[int, int, int, int]] = None, monitor_index: int = 0
    ) -> str:
        """
        **`Screen().read_text()`:** Uses OCR to extract all readable text from the screen or a specific region.

        **Description:**

        Leverages the blazing-fast native Windows OCR API to extract all readable text from the screen or a specific region.

        **Arguments:**

        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`monitor_index` (`int`)**

        **Returns:**

        **`str`**

        **Example:**

        ```python
        text = Screen().read_text(region = (250, 250, 500, 500), monitor_index = 0)
        ```
        """
        return _ReadText(region = region, monitor_index = monitor_index).execute()

    def locate_text(
        self,
        text: str,
        region: Optional[tuple[int, int, int, int]] = None,
        exact_match: bool = False,
        monitor_index: int = 0
    ) -> tuple[Optional[int], Optional[int]]:
        """
        **`Screen().locate_text()`:** Uses OCR to find specific text on the screen and returns its central coordinates.

        **Description:**

        Leverages the blazing-fast native Windows OCR API to find the location of specific text within the specified region.

        **Arguments:**

        - **`text` (`str`)**
        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`exact_match` (`bool`)**
        - **`monitor_index` (`int`)**

        **Returns:**

        **`tuple[Optional[int], Optional[int]]`**

        **Example:**

        ```python
        x, y = Screen().locate_text(
            text = "Submit",
            region = (250, 250, 500, 500),
            exact_match = True,
            monitor_index = 0
        )
        ```
        """
        return _LocateText(
            text = text,
            region = region,
            exact_match = exact_match,
            monitor_index = monitor_index
        ).execute()