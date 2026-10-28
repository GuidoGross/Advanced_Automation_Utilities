from ._timing_action import _TimingAction
from .._utilities import _validate_between_range
from .._kill_switch_event import KILL_SWITCH_EVENT
import time

class _Wait(_TimingAction):
    def __init__(self, duration):
        _validate_between_range(duration = duration)
        self.duration = duration

    def execute(self, stop_event = None):
        deadline = time.perf_counter() + self.duration
        event = stop_event if stop_event is not None else KILL_SWITCH_EVENT
        while (remaining := deadline - time.perf_counter()) > 0:
            if event.wait(timeout = remaining): return