from ._timing_action import _TimingAction
from ._wait import _Wait
from .._utilities import _validate_between_range
import random

class _WaitRandom(_TimingAction):
    def __init__(self, minimum_duration, maximum_duration):
        self.minimum_duration = minimum_duration
        self.maximum_duration = maximum_duration
        _validate_between_range(
            minimum_duration = self.minimum_duration, maximum_duration = self.maximum_duration
        )
        if self.minimum_duration > self.maximum_duration:
            raise ValueError("Minimum duration cannot be greater than maximum duration.")

    def execute(self, stop_event = None):
        _Wait(
            random.uniform(self.minimum_duration, self.maximum_duration)).execute(stop_event = stop_event
        )