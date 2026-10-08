from ._timing_action import _TimingAction
from .._utilities import _validate_between_range
from .._kill_switch_event import KILL_SWITCH_EVENT

class _Wait(_TimingAction):
    def __init__(self, duration):
        _validate_between_range(duration = duration)
        self.duration = duration

    def execute(self, stop_event = None):
        if stop_event is not None: stop_event.wait(timeout = self.duration)
        else: KILL_SWITCH_EVENT.wait(timeout = self.duration)