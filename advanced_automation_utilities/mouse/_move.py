from ._mouse_action import _MouseAction
from .mouse_info import MouseInfo
from .._utilities import _apply_variation
from ..backend.windows._mouse import _set_cursor_position
import math
import random
import time

class _Move(_MouseAction):
    _REFERENCE_SPEED = 500
    _OVERSHOOT_DISTANCE_MULTIPLIER = 0.05
    _OVERSHOOT_ANGLE_DEVIATION = math.pi / 4
    _SPEED_THRESHOLD_FOR_THREE_PHASES = 2500
    _SPEED_THRESHOLD_FOR_TWO_PHASES = 1250
    _MINIMUM_PAUSE_DURATION_SECONDS = 0.025
    _MAXIMUM_PAUSE_DURATION_SECONDS = 0.1
    _MINIMUM_TIME_FRACTION_FOR_TWO_PHASES = 0.4
    _MAXIMUM_TIME_FRACTION_FOR_TWO_PHASES = 0.6
    _MINIMUM_TIME_FRACTION_FOR_THREE_PHASES = 0.2
    _MAXIMUM_TIME_FRACTION_FOR_THREE_PHASES = 0.4
    _TWO_PHASES_FIRST_TARGET_FRACTION = 2 / 3
    _PHASE_TARGET_FRACTION_VARIATION = 0.1
    _THREE_PHASES_FIRST_TARGET_FRACTION = 0.5
    _THREE_PHASES_SECOND_TARGET_FRACTION = 0.75
    _STEPS_PER_SECOND = 120
    _MAXIMUM_PIXELS_PER_STEP = 5
    _MINIMUM_STEPS = 60
    _BASE_TREMOR_PROBABILITY = 0.25
    _MAXIMUM_EASE_DISTORTION = 0.1
    _BEZIER_CURVE_SEGMENTS = 4
    _SEGMENT_LENGTH_VARIATION_MULTIPLIER = 0.5
    _MINIMUM_FINAL_SEGMENT_LENGTH = 0.05
    _MINIMUM_TREMOR_MAGNITUDE = 1
    _MAXIMUM_TREMOR_MAGNITUDE = 5
    _TREMOR_ANGLE_DEVIATION = 30
    _MAXIMUM_TREMOR_ANGLE_LIMIT = 90

    def __init__(self, x, y, physics = None):
        super().__init__(physics = physics)
        self.x = x
        self.y = y

    def execute(self):
        original_target_x, original_target_y = self.x, self.y
        initial_x, initial_y = MouseInfo().coordinates
        if math.hypot(original_target_x - initial_x, original_target_y - initial_y) <= self.physics.target_radius:
            return
        distance = math.hypot(self.x - initial_x, self.y - initial_y)
        speed, duration = self._calculate_speed_and_duration(distance)
        self._apply_target_radius()
        if duration <= 0:
            _set_cursor_position(self.x, self.y)
            return
        if self.physics.inconsistency <= 0:
            self._execute_movement_phase(
                initial_x, initial_y, self.x, self.y, duration, speed
            )
            return
        speed = distance / duration
        initial_movement_duration = duration * (1 - self.physics.readjustment_duration_ratio)
        readjust_duration = duration * self.physics.readjustment_duration_ratio
        phase_1_x, phase_1_y, error_x, error_y = self._calculate_overshoot(initial_x, initial_y, speed)
        self._execute_movement_phase(
            initial_x, initial_y, phase_1_x, phase_1_y, initial_movement_duration, speed
        )
        if readjust_duration > 0:
            self._execute_readjustment_phases(
                error_x, error_y, speed, readjust_duration, original_target_x, original_target_y
            )

    def _calculate_speed_and_duration(self, distance):
        speed = self.physics.speed
        duration = self.physics.duration
        if duration <= 0 and speed > 0:
            if self.physics.speed_variation > 0:
                speed = max(1e-15, _apply_variation(speed, self.physics.speed_variation))
            base_duration = self.physics.base_duration
            if self.physics.base_duration_variation > 0:
                base_duration = max(
                    0, _apply_variation(base_duration, self.physics.base_duration_variation)
                )
            duration = base_duration + (distance / speed)
        elif duration > 0 and self.physics.duration_variation > 0:
            duration = max(1e-15, _apply_variation(duration, self.physics.duration_variation))
        return speed, duration

    def _apply_target_radius(self):
        if self.physics.target_radius > 0:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, self.physics.target_radius)
            self.x += math.cos(angle) * radius
            self.y += math.sin(angle) * radius

    def _calculate_overshoot(self, initial_x, initial_y, speed):
        speed_factor = max(1, speed / self._REFERENCE_SPEED)
        maximum_overshoot = speed * self._OVERSHOOT_DISTANCE_MULTIPLIER * self.physics.inconsistency * speed_factor
        movement_angle = math.atan2(self.y - initial_y, self.x - initial_x)
        if random.random() < 0.5:
            overshoot_angle = random.gauss(movement_angle, self._OVERSHOOT_ANGLE_DEVIATION)
        else: overshoot_angle = random.gauss(movement_angle + math.pi, self._OVERSHOOT_ANGLE_DEVIATION)
        inverse_speed_factor = self._REFERENCE_SPEED / max(1, speed)
        overshoot_radius = (random.random() ** inverse_speed_factor) * maximum_overshoot
        error_x = math.cos(overshoot_angle) * overshoot_radius
        error_y = math.sin(overshoot_angle) * overshoot_radius
        return self.x + error_x, self.y + error_y, error_x, error_y

    def _execute_readjustment_phases(
        self, error_x, error_y, speed, readjust_duration, original_target_x, original_target_y
    ):
        if speed >= self._SPEED_THRESHOLD_FOR_THREE_PHASES: number_of_phases = 3
        elif speed >= self._SPEED_THRESHOLD_FOR_TWO_PHASES: number_of_phases = 2
        else: number_of_phases = 1
        pauses = [
            random.uniform(
                self._MINIMUM_PAUSE_DURATION_SECONDS, self._MAXIMUM_PAUSE_DURATION_SECONDS
            ) for _ in range(number_of_phases - 1)
        ]
        available_time = readjust_duration - sum(pauses)
        if available_time < self._MINIMUM_PAUSE_DURATION_SECONDS:
            number_of_phases, pauses, available_time = 1, [], readjust_duration
        phase_times = self._calculate_phase_times(number_of_phases, available_time)
        error_fractions = self._calculate_error_fractions(number_of_phases)
        for i in range(number_of_phases):
            fraction = error_fractions[i]
            target_x = self.x + error_x * (1 - fraction)
            target_y = self.y + error_y * (1 - fraction)
            current_x, current_y = MouseInfo().coordinates
            self._execute_movement_phase(
                current_x, current_y, target_x, target_y, phase_times[i], speed * 0.5
            )
            if self.physics.target_radius > 0:
                latest_x, latest_y = MouseInfo().coordinates
                if math.hypot(latest_x - original_target_x, latest_y - original_target_y) <= self.physics.target_radius:
                    break
            if i < number_of_phases - 1:
                target_time = time.perf_counter() + pauses[i]
                while time.perf_counter() < target_time: pass

    def _calculate_phase_times(self, phases, available_time):
        if phases == 1:
            return [available_time]
        elif phases == 2:
            split = random.uniform(
                self._MINIMUM_TIME_FRACTION_FOR_TWO_PHASES, self._MAXIMUM_TIME_FRACTION_FOR_TWO_PHASES
            )
            return [available_time * split, available_time * (1 - split)]
        else:
            phase_1_fraction = random.uniform(
                self._MINIMUM_TIME_FRACTION_FOR_THREE_PHASES,
                self._MAXIMUM_TIME_FRACTION_FOR_THREE_PHASES
            )
            phase_2_fraction = random.uniform(
                self._MINIMUM_TIME_FRACTION_FOR_THREE_PHASES,
                self._MAXIMUM_TIME_FRACTION_FOR_THREE_PHASES
            )
            return [
                available_time * phase_1_fraction, available_time * phase_2_fraction, available_time * (1 - phase_1_fraction - phase_2_fraction)
            ]

    def _calculate_error_fractions(self, phases):
        if phases == 1: return [1]
        elif phases == 2:
            fraction_1 = self._TWO_PHASES_FIRST_TARGET_FRACTION + random.uniform(
                -self._PHASE_TARGET_FRACTION_VARIATION, self._PHASE_TARGET_FRACTION_VARIATION
            )
            return [min(1, fraction_1), 1]
        else:
            fraction_1 = self._THREE_PHASES_FIRST_TARGET_FRACTION + random.uniform(
                -self._PHASE_TARGET_FRACTION_VARIATION, self._PHASE_TARGET_FRACTION_VARIATION
            )
            fraction_2 = self._THREE_PHASES_SECOND_TARGET_FRACTION + random.uniform(
                -self._PHASE_TARGET_FRACTION_VARIATION, self._PHASE_TARGET_FRACTION_VARIATION
            )
            return [min(1, fraction_1), min(1, fraction_2), 1]

    def _execute_movement_phase(self, initial_x, initial_y, final_x, final_y, duration, speed):
        if duration <= 0: return
        distance = duration * speed
        steps = int(
            max(duration * self._STEPS_PER_SECOND, distance / self._MAXIMUM_PIXELS_PER_STEP, self._MINIMUM_STEPS)
        )
        path = self._generate_human_path(initial_x, initial_y, final_x, final_y, steps, speed)
        speed_factor = max(1, speed / self._REFERENCE_SPEED)
        tremor_chance = self._BASE_TREMOR_PROBABILITY * self.physics.inconsistency / speed_factor
        start_time = time.perf_counter()
        expected_time = start_time
        previous_x, previous_y = initial_x, initial_y
        distortion_factor = random.uniform(-self._MAXIMUM_EASE_DISTORTION, self._MAXIMUM_EASE_DISTORTION)
        for i in range(steps):
            progress = (i + 1) / steps
            ease = self._distorted_ease(progress, distortion_factor)
            index = int(ease * (steps - 1))
            current_x, current_y = path[index]
            if random.random() < tremor_chance and i < steps - 1:
                tremor_x, tremor_y = self._calculate_tremor(
                    current_x, current_y, final_x, final_y, speed
                )
                current_x += tremor_x
                current_y += tremor_y
            _set_cursor_position(current_x, current_y)
            step_distance = math.hypot(current_x - previous_x, current_y - previous_y)
            step_duration = duration / steps
            instant_speed = step_distance / step_duration
            if self.physics.minimum_speed > 0 and instant_speed < self.physics.minimum_speed:
                step_duration = step_distance / self.physics.minimum_speed
            if self.physics.maximum_speed > 0 and instant_speed > self.physics.maximum_speed:
                step_duration = step_distance / self.physics.maximum_speed
            expected_time += step_duration
            while time.perf_counter() < expected_time: pass
            previous_x, previous_y = current_x, current_y

    def _generate_human_path(self, initial_x, initial_y, target_x, target_y, steps, speed):
        distance = math.hypot(target_x - initial_x, target_y - initial_y)
        if distance == 0: return [(target_x, target_y)] * steps
        speed_factor = max(1, speed / self._REFERENCE_SPEED)
        adjusted_inconsistency = self.physics.inconsistency / speed_factor
        segments = self._BEZIER_CURVE_SEGMENTS
        segment_lengths = []
        remaining = 1
        for i in range(segments - 1):
            length = 1 / segments
            variation = length * self._SEGMENT_LENGTH_VARIATION_MULTIPLIER
            segment_length = min(
                length + random.uniform(-variation, variation),
                remaining - self._MINIMUM_FINAL_SEGMENT_LENGTH
            )
            segment_lengths.append(segment_length)
            remaining -= segment_length
        segment_lengths.append(remaining)
        points = []
        current_x, current_y = initial_x, initial_y
        remaining_steps = steps
        for i, length_percentage in enumerate(segment_lengths):
            segment_target_x = initial_x + (target_x - initial_x) * sum(segment_lengths[:i + 1])
            segment_target_y = initial_y + (target_y - initial_y) * sum(segment_lengths[:i + 1])
            segment_distance = distance * length_percentage
            segment_steps = int(steps * length_percentage)
            if i == segments - 1: segment_steps = remaining_steps
            remaining_steps -= segment_steps
            direction_x = (segment_target_x - current_x) / max(segment_distance, 1e-15)
            direction_y = (segment_target_y - current_y) / max(segment_distance, 1e-15)
            perpendicular_x, perpendicular_y = -direction_y, direction_x
            maximum_curve = segment_distance * adjusted_inconsistency
            control_point_1_x = current_x + (segment_target_x - current_x) * 1 / 3 + perpendicular_x * random.uniform(-maximum_curve, maximum_curve)
            control_point_1_y = current_y + (segment_target_y - current_y) * 1 / 3 + perpendicular_y * random.uniform(-maximum_curve, maximum_curve)
            control_point_2_x = current_x + (segment_target_x - current_x) * 2 / 3 + perpendicular_x * random.uniform(-maximum_curve, maximum_curve)
            control_point_2_y = current_y + (segment_target_y - current_y) * 2 / 3 + perpendicular_y * random.uniform(-maximum_curve, maximum_curve)
            for j in range(1, segment_steps + 1):
                progress = j / segment_steps
                points.append(
                    self._bezier_point(
                        (current_x, current_y),
                        (control_point_1_x, control_point_1_y),
                        (control_point_2_x, control_point_2_y),
                        (segment_target_x, segment_target_y),
                        progress
                    )
                )
            current_x, current_y = segment_target_x, segment_target_y
        return points

    def _bezier_point(self, point_0, point_1, point_2, point_3, progress):
        x = (1 - progress) ** 3 * point_0[0] + 3 * (1 - progress) ** 2 * progress * point_1[0] + 3 * (1 - progress) * progress ** 2 * point_2[0] + progress ** 3 * point_3[0]
        y = (1 - progress) ** 3 * point_0[1] + 3 * (1 - progress) ** 2 * progress * point_1[1] + 3 * (1 - progress) * progress ** 2 * point_2[1] + progress ** 3 * point_3[1]
        return x, y

    def _distorted_ease(self, progress, distortion_factor):
        base_ease = self._ease(progress)
        distortion = distortion_factor * (progress ** 2) * ((1 - progress) ** 2) * 16
        ease = max(0, min(1, base_ease + distortion))
        return ease

    def _ease(self, n):
        if n < 0.5: return 2 * n * n
        else:
            n = 2 * n - 1
            return -0.5 * (n * (n - 2) - 1)

    def _calculate_tremor(self, current_x, current_y, target_x, target_y, speed):
        speed_factor = max(1, speed / self._REFERENCE_SPEED)
        magnitude = random.uniform(self._MINIMUM_TREMOR_MAGNITUDE, self._MAXIMUM_TREMOR_MAGNITUDE) * self.physics.inconsistency / speed_factor
        if magnitude == 0: return 0, 0
        angle = random.gauss(0, self._TREMOR_ANGLE_DEVIATION)
        while abs(angle) >= self._MAXIMUM_TREMOR_ANGLE_LIMIT or angle == 0:
            angle = random.gauss(0, self._TREMOR_ANGLE_DEVIATION)
        angle_radians = math.radians(angle)
        difference_x = target_x - current_x
        difference_y = target_y - current_y
        distance = math.hypot(difference_x, difference_y)
        if distance == 0: return 0, 0
        direction_angle = math.atan2(difference_y, difference_x)
        final_angle = direction_angle + angle_radians
        tremor_x = math.cos(final_angle) * magnitude
        tremor_y = math.sin(final_angle) * magnitude
        return tremor_x, tremor_y