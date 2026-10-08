from ._keyboard_action import _KeyboardAction
from .._utilities import _apply_variation
from ..backend.windows._keyboard import _get_virtual_key_code, _send_key
from ..timing import Timing

class _HoldKey(_KeyboardAction):
    def __init__(self, key, physics = None):
        super().__init__(physics = physics)
        self.key = key
        if not _get_virtual_key_code(self.key):
            raise KeyError(f"The \"{self.key}\" key is not valid or supported.")

    def execute(self):
        timing = Timing()
        delay = self.physics.press_delay
        if self.physics.press_delay_variation > 0:
            delay = _apply_variation(delay, self.physics.press_delay_variation)
            delay = max(0, delay)
        timing.wait(delay)
        _send_key(self.key, key_released = False)
        duration = self.physics.press_duration
        if self.physics.press_duration_variation > 0:
            duration = _apply_variation(duration, self.physics.press_duration_variation)
            duration = max(0, duration)
        if self.physics.auto_repeat and duration > 0.5:
            timing.wait(0.5)
            remaining_duration = duration - 0.5
            repeat_interval = 0.033
            while remaining_duration > 0:
                if remaining_duration < repeat_interval:
                    timing.wait(remaining_duration)
                    break
                _send_key(self.key, key_released = False)
                timing.wait(repeat_interval)
                remaining_duration -= repeat_interval
        else: timing.wait(duration)