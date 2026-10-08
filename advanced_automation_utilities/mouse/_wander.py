from ._mouse_action import _MouseAction
from ._move import _Move
from .mouse_info import MouseInfo
from .._utilities import _validate_region, _validate_between_range, _apply_variation
from ..timing import Timing, TimingInfo
from ..screen import ScreenInfo
import math
import random

class _Wander(_MouseAction):
    _MINIMUM_SPEED_EPSILON = 1e-15
    _CANDIDATES_PER_STEP = 8
    _GAUSSIAN_SIGMA_DIVISOR = 3

    def __init__(
        self,
        duration,
        region = None,
        maximum_steps = None,
        physics = None
    ):
        super().__init__(physics = physics)
        self.duration = duration
        self.region = region
        self.maximum_steps = maximum_steps
        _validate_region(self.region)
        _validate_between_range(duration = self.duration, maximum_steps = self.maximum_steps)

    def execute(self, stop_event = None):
        timing = Timing()
        timing_info = TimingInfo()
        screen_info = ScreenInfo()
        duration = max(0, self.duration)
        if duration == 0: return
        start_time = timing_info.time
        if self.region is None:
            left, top, right, bottom = screen_info.work_area
            self.region = (left, top + int((bottom - top) * 0.1), right, bottom)
        region_width = self.region[2] - self.region[0]
        region_height = self.region[3] - self.region[1]
        screen_size = math.hypot(region_width, region_height)
        steps_taken = 0
        while True:
            current_time = timing_info.time
            remaining = duration - (current_time - start_time)
            if remaining <= 0: break
            if stop_event is not None and stop_event.is_set(): break
            if self.maximum_steps is not None and steps_taken >= self.maximum_steps: break
            distance_ratio = self.physics.wander_distance_ratio
            if self.physics.wander_distance_ratio_variation > 0:
                distance_ratio = _apply_variation(
                    distance_ratio, self.physics.wander_distance_ratio_variation
                )
            distance = distance_ratio * screen_size
            distance = max(0, distance)
            move_duration = 0
            if self.physics.duration > 0:
                move_duration = self.physics.duration * (1 + self.physics.duration_variation)
            elif self.physics.speed > 0:
                minimum_speed = self.physics.speed * (1 - self.physics.speed_variation)
                minimum_speed = max(self._MINIMUM_SPEED_EPSILON, minimum_speed)
                maximum_base_duration = self.physics.base_duration * (1 + self.physics.base_duration_variation)
                move_duration = maximum_base_duration + (distance / minimum_speed)
            if self.maximum_steps is not None:
                remaining_steps = self.maximum_steps - steps_taken
                time_per_step = remaining / remaining_steps
                delay = max(0, time_per_step - move_duration)
            else:
                delay = self.physics.wander_delay
                if self.physics.wander_delay_variation > 0:
                    delay = _apply_variation(delay, self.physics.wander_delay_variation)
                delay = max(0, delay)
            if move_duration + delay > remaining:
                if stop_event is not None: stop_event.wait(remaining)
                else: timing.wait(remaining)
                break
            target_x, target_y = self._get_next_target(distance)
            _Move(target_x, target_y, physics = self.physics).execute()
            steps_taken += 1
            if stop_event is not None:
                if stop_event.wait(delay): break
            else: timing.wait(delay)

    def _get_next_target(self, distance):
        mouse_info = MouseInfo()
        current_x, current_y = mouse_info.coordinates
        left, top, right, bottom = self.region
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2
        maximum_distance = math.hypot((right - left) / 2, (bottom - top) / 2)
        padding_x = min(distance * self.physics.inconsistency, (right - left) / 2)
        padding_y = min(distance * self.physics.inconsistency, (bottom - top) / 2)
        candidates = []
        for _ in range(self._CANDIDATES_PER_STEP):
            angle = random.uniform(0, 2 * math.pi)
            candidate_x = current_x + distance * math.cos(angle)
            candidate_y = current_y + distance * math.sin(angle)
            candidate_x = max(left + padding_x, min(right - 1 - padding_x, candidate_x))
            candidate_y = max(top + padding_y, min(bottom - 1 - padding_y, candidate_y))
            distance_to_center = math.hypot(candidate_x - center_x, candidate_y - center_y)
            sigma = maximum_distance / self._GAUSSIAN_SIGMA_DIVISOR
            weight = math.exp(-0.5 * (distance_to_center / sigma) ** 2)
            candidates.append(((candidate_x, candidate_y), weight))
        choices = [candidate[0] for candidate in candidates]
        weights = [candidate[1] for candidate in candidates]
        target = random.choices(choices, weights = weights, k = 1)[0]
        return target[0], target[1]