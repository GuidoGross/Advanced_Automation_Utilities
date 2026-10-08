from ._mouse_action import _MouseAction
from ._move import _Move
from .._utilities import _validate_options, _apply_variation
from ..timing import Timing

class _BaseClick(_MouseAction):
    def __init__(self, x = None, y = None, button = "left", physics = None):
        super().__init__(physics = physics)
        self.x = x
        self.y = y
        self.button = button.lower() if isinstance(button, str) else button
        _validate_options(self.button, ["left", "right", "middle"], "mouse button")

    def _move_if_needed(self):
        if self.x is not None and self.y is not None:
            _Move(self.x, self.y, self.physics).execute()
            click_delay = self.physics.click_delay
            if self.physics.click_delay_variation > 0:
                click_delay = _apply_variation(click_delay, self.physics.click_delay_variation)
                click_delay = max(0, click_delay)
            Timing().wait(click_delay)