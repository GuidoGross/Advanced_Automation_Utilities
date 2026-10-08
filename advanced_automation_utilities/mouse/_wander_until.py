from ._mouse_action import _MouseAction
from ._wander import _Wander
from .._utilities import _validate_between_range, _validate_region
from ..timing import Timing, TimingInfo
import threading
import math

class _WanderUntil(_MouseAction):
    def __init__(
        self,
        condition_function,
        region = None,
        maximum_steps = None,
        timeout = 0,
        poll_interval = 0.1,
        physics = None
    ):
        super().__init__(physics = physics)
        self.condition_function = condition_function
        self.region = region
        self.maximum_steps = maximum_steps
        self.timeout = timeout
        self.poll_interval = poll_interval
        _validate_region(self.region)
        _validate_between_range(timeout = self.timeout, poll_interval = self.poll_interval)
        if self.maximum_steps is not None: _validate_between_range(maximum_steps = self.maximum_steps)

    def execute(self, stop_event = None):
        inner_stop_event = threading.Event()
        timing = Timing()
        timing_info = TimingInfo()

        def wanderer():
            wander_duration = self.timeout if self.timeout > 0 else math.inf
            _Wander(
                duration = wander_duration,
                region = self.region,
                maximum_steps = self.maximum_steps,
                physics = self.physics
            ).execute(stop_event = inner_stop_event)

        wander_thread = threading.Thread(target = wanderer, daemon = True)
        wander_thread.start()
        start_time = timing_info.time
        condition_met = False
        try:
            while self.timeout == 0 or timing_info.time - start_time < self.timeout:
                if stop_event is not None and stop_event.is_set(): break
                if self.condition_function():
                    condition_met = True
                    break
                if not wander_thread.is_alive(): break
                timing.wait(self.poll_interval)
        finally:
            inner_stop_event.set()
            wander_thread.join()
        return condition_met