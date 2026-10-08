from ._mouse_action import _MouseAction
from .._utilities import _validate_between_range, _validate_options, _apply_variation
from ..timing import Timing
from ..backend.windows._mouse import _scroll

class _Scroll(_MouseAction):
    def __init__(self, amount, direction = "down", physics = None):
        super().__init__(physics = physics)
        self.amount = amount
        self.direction = direction.lower()
        _validate_between_range(scroll_amount = self.amount)
        _validate_options(self.direction, ["up", "down", "left", "right"], "scroll direction")

    def execute(self):
        timing = Timing()
        if self.amount == 0: return
        if self.physics.scroll_speed == 0 and self.physics.scroll_duration == 0:
            _scroll(self.amount, self.direction)
            return
        step = self.physics.scroll_step
        if self.physics.scroll_duration > 0:
            current_duration = self.physics.scroll_duration
            if self.physics.scroll_duration_variation > 0:
                current_duration = _apply_variation(
                    current_duration, self.physics.scroll_duration_variation
                )
            current_duration = max(1e-15, current_duration)
            base_pause = (current_duration * step) / self.amount
        else:
            current_speed = self.physics.scroll_speed
            if self.physics.scroll_speed_variation > 0:
                current_speed = _apply_variation(current_speed, self.physics.scroll_speed_variation)
            current_speed = max(1e-15, current_speed)
            base_pause = step / current_speed
        remaining = self.amount
        while remaining > 0:
            current_step = step if remaining >= step else remaining
            _scroll(current_step, self.direction)
            pause = base_pause
            if self.physics.scroll_pause_variation > 0:
                pause = _apply_variation(pause, self.physics.scroll_pause_variation)
                pause = max(0, pause)
            timing.wait(pause)
            remaining -= current_step