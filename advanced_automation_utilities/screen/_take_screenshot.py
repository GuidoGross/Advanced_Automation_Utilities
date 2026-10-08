from ._screen_action import _ScreenAction
from .._utilities import _validate_region, _validate_between_range
from ..backend.windows._screen import _take_screenshot
import mss.base

class _TakeScreenshot(_ScreenAction):
    def __init__(self, region = None, monitor_index = 0, save_path = None):
        self.region = region
        if self.region is not None:
            _validate_region(self.region)
        self.monitor_index = monitor_index
        _validate_between_range(monitor_index = self.monitor_index)
        self.save_path = save_path
        if self.save_path is not None and not isinstance(self.save_path, str):
            raise ValueError("Save path must be a string.")

    def execute(self):
        return _take_screenshot(self.region, self.monitor_index, self.save_path)