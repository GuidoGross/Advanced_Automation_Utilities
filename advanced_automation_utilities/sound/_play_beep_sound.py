from ._sound_action import _SoundAction
from .._utilities import _validate_between_range
from ..backend.windows._sound import _play_beep_sound
import math

class _PlayBeepSound(_SoundAction):
    def __init__(self, frequency, duration):
        self.frequency = frequency
        self.duration = duration
        _validate_between_range(37, 32767, frequency = self.frequency)
        _validate_between_range(1e-15, math.inf, duration = self.duration)

    def execute(self): _play_beep_sound(self.frequency, self.duration)