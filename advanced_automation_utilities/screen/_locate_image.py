from ._screen_action import _ScreenAction
from .._utilities import _validate_region, _validate_file_exists, _validate_between_range
from ..backend.windows._screen import _locate_image

class _LocateImage(_ScreenAction):
    def __init__(self, image_path, confidence = 0.9, limit = 0, region = None, monitor_index = 0):
        self.image_path = image_path
        _validate_file_exists(self.image_path, "Image file")
        self.confidence = confidence
        _validate_between_range(0, 1, confidence = self.confidence)
        self.limit = limit
        _validate_between_range(0, limit = self.limit)
        self.region = region
        if self.region is not None: _validate_region(self.region)
        self.monitor_index = monitor_index
        _validate_between_range(monitor_index = self.monitor_index)

    def execute(self):
        return _locate_image(
            self.image_path, self.confidence, self.limit, self.region, self.monitor_index
        )