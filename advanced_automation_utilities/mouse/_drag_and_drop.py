from ._mouse_action import _MouseAction
from ._move import _Move
from ._hold_click import _HoldClick
from ._release_click import _ReleaseClick
from .._utilities import _validate_options
from ..timing import Timing

class _DragAndDrop(_MouseAction):
    def __init__(self, start_x, start_y, end_x, end_y, button = "left", physics = None):
        super().__init__(physics = physics)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.button = button
        _validate_options(self.button, ["left", "right", "middle"], "mouse button")

    def execute(self):
        timing = Timing()
        _Move(x = self.start_x, y = self.start_y, physics = self.physics).execute()
        _HoldClick(
            x = self.start_x, y = self.start_y, button = self.button, physics = self.physics
        ).execute()
        try:
            timing.wait(0.2)
            _Move(x = self.end_x, y = self.end_y, physics = self.physics).execute()
            timing.wait(0.2)
        finally:
            _ReleaseClick(
                x = self.end_x, y = self.end_y, button = self.button, physics = self.physics
            ).execute()