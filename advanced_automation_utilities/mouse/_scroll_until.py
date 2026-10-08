from ._mouse_action import _MouseAction
from ._scroll import _Scroll
from .._utilities import _validate_between_range, _validate_options
from ..timing import Timing, TimingInfo
import threading
import math

class _ScrollUntil(_MouseAction):
    def __init__(
        self,
        condition_function,
        amount = 0,
        direction = "down",
        timeout = 0,
        poll_interval = 0.1,
        physics = None
    ):
        super().__init__(physics = physics)
        self.condition_function = condition_function
        self.amount = amount
        self.direction = direction.lower()
        self.timeout = timeout
        self.poll_interval = poll_interval
        _validate_between_range(
            scroll_amount = self.amount, wait_time = self.timeout, poll_interval = self.poll_interval
        )
        _validate_options(self.direction, ["up", "down", "left", "right"], "scroll direction")

    def execute(self, stop_event = None):
        stop_scroll = False
        timing = Timing()
        timing_info = TimingInfo()
        scrolled = 0
        limit = self.amount if self.amount > 0 else math.inf
        step = self.physics.scroll_step

        def scroller():
            nonlocal scrolled
            while not stop_scroll and scrolled < limit:
                current_step = step if (limit - scrolled) >= step else int(limit - scrolled)
                _Scroll(
                    amount = current_step, direction = self.direction, physics = self.physics
                ).execute()
                scrolled += current_step

        scroll_thread = threading.Thread(target = scroller, daemon = True)
        scroll_thread.start()
        start_time = timing_info.time
        condition_met = False
        try:
            while self.timeout == 0 or timing_info.time - start_time < self.timeout:
                if stop_event is not None and stop_event.is_set(): break
                if self.condition_function():
                    condition_met = True
                    break
                if not scroll_thread.is_alive(): break
                timing.wait(self.poll_interval)
        finally:
            stop_scroll = True
            scroll_thread.join()
        return condition_met