from ._screen_action import _ScreenAction
from .._utilities import _validate_region, _validate_between_range
from ..backend.windows._screen import _run_ocr_on_region

class _ReadText(_ScreenAction):
    def __init__(self, region = None, monitor_index = 0):
        self.region = region
        _validate_region(self.region)
        self.monitor_index = monitor_index
        _validate_between_range(monitor_index = self.monitor_index)

    def execute(self):
        result = _run_ocr_on_region(self.region, self.monitor_index)
        return result.text