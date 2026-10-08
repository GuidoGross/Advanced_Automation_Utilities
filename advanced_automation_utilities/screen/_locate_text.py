from ._screen_action import _ScreenAction
from .._utilities import _validate_region, _validate_between_range
from ..backend.windows._screen import _run_ocr_on_region, _adjust_coordinates_for_region
import math

class _LocateText(_ScreenAction):
    def __init__(self, text, region = None, exact_match = False, monitor_index = 0):
        self.text = text
        self.region = region
        _validate_region(self.region)
        self.exact_match = exact_match
        self.monitor_index = monitor_index
        _validate_between_range(monitor_index = self.monitor_index)

    def execute(self):
        if not self.text.strip(): raise ValueError("Text cannot be empty.")
        result = _run_ocr_on_region(self.region, self.monitor_index)
        search_text = self.text if self.exact_match else self.text.lower()
        for line in result.lines:
            line_text = line.text if self.exact_match else line.text.lower()
            if self.exact_match and search_text != line_text: continue
            if not self.exact_match and search_text not in line_text: continue
            minimum_x = minimum_y = math.inf
            maximum_right = maximum_bottom = -math.inf
            found_any = False
            for word in line.words:
                word_text = word.text if self.exact_match else word.text.lower()
                if self.exact_match or (word_text in search_text) or (search_text in word_text):
                    bounding_rectangle = word.bounding_rect
                    minimum_x = min(minimum_x, bounding_rectangle.x)
                    minimum_y = min(minimum_y, bounding_rectangle.y)
                    maximum_right = max(maximum_right, bounding_rectangle.x + bounding_rectangle.width)
                    maximum_bottom = max(
                        maximum_bottom, bounding_rectangle.y + bounding_rectangle.height
                    )
                    found_any = True
            if found_any:
                x = minimum_x + (maximum_right - minimum_x) / 2
                y = minimum_y + (maximum_bottom - minimum_y) / 2
                return _adjust_coordinates_for_region(x, y, self.region, self.monitor_index)
        return None, None