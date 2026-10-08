from ._keyboard_action import _KeyboardAction
from ._hold_key import _HoldKey
from ._release_key import _ReleaseKey
from .._utilities import _apply_variation
from ..backend.windows._keyboard import _get_virtual_key_code
from ..timing import Timing

class _Hotkey(_KeyboardAction):
    def __init__(self, *keys, physics = None):
        super().__init__(physics = physics)
        self.keys = keys
        for key in self.keys:
            if not _get_virtual_key_code(key):
                raise KeyError(f"The \"{key}\" key is not valid or supported.")

    def execute(self):
        timing = Timing()
        keys_held = []
        try:
            for i, key in enumerate(self.keys):
                _HoldKey(key, self.physics).execute()
                keys_held.append(key)
                if i < len(self.keys) - 1:
                    delay = self.physics.hotkey_delay
                    if self.physics.hotkey_delay_variation > 0:
                        delay = _apply_variation(delay, self.physics.hotkey_delay_variation)
                    delay = max(0, delay)
                    timing.wait(delay)
            duration = self.physics.press_duration
            if self.physics.press_duration_variation > 0:
                duration = _apply_variation(duration, self.physics.press_duration_variation)
            duration = max(0, duration)
            timing.wait(duration)
        finally:
            for key in reversed(keys_held): _ReleaseKey(key, self.physics).execute()