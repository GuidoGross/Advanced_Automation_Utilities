from .._utilities import _validate_between_range
from dataclasses import dataclass
import math

@dataclass(frozen = True)
class MousePhysics:
    """
    **`MousePhysics`:** Configures movement, clicking, scrolling, and wandering behavior.

    **Description:**

    Configuration class that defines the timing and movement characteristics for mouse actions, allowing for human-like or instantaneous execution.

    **Arguments:**

    - **`speed` (`float`):** Must be ≥ 0.
    - **`minimum_speed` (`float`):** Must be ≥ 0.
    - **`maximum_speed` (`float`):** Must be ≥ 0.
    - **`speed_variation` (`float`):** Must be ≥ 0.
    - **`duration` (`float`):** Seconds. Must be ≥ 0.
    - **`duration_variation` (`float`):** Must be ≥ 0.
    - **`base_duration` (`float`):** Seconds. Must be ≥ 0.
    - **`base_duration_variation` (`float`):** Must be ≥ 0.
    - **`inconsistency` (`float`):** Must be ≥ 0.
    - **`target_radius` (`float`):** Must be ≥ 0.
    - **`readjustment_duration_ratio` (`float`):** Must be ≥ 0 and ≤ 1.
    - **`click_delay` (`float`):** Seconds. Must be ≥ 0.
    - **`click_delay_variation` (`float`):** Must be ≥ 0.
    - **`click_duration` (`float`):** Seconds. Must be ≥ 0.
    - **`click_duration_variation` (`float`):** Must be ≥ 0.
    - **`scroll_speed` (`float`):** Must be ≥ 0.
    - **`scroll_speed_variation` (`float`):** Must be ≥ 0.
    - **`scroll_duration` (`float`):** Seconds. Must be ≥ 0.
    - **`scroll_duration_variation` (`float`):** Must be ≥ 0.
    - **`scroll_step` (`int`):** Must be ≥ 1.
    - **`scroll_pause_variation` (`float`):** Must be ≥ 0.
    - **`wander_delay` (`float`):** Seconds. Must be ≥ 0.
    - **`wander_delay_variation` (`float`):** Must be ≥ 0.
    - **`wander_distance_ratio` (`float`):** Must be ≥ 0.
    - **`wander_distance_ratio_variation` (`float`):** Must be ≥ 0.

    **Example:**

    ```python
    mouse_physics = MousePhysics(
        speed = 1500,
        minimum_speed = 0,
        maximum_speed = 0,
        speed_variation = 0.1,
        duration = 0,
        duration_variation = 0,
        base_duration = 0.1,
        base_duration_variation = 0.1,
        inconsistency = 0.25,
        target_radius = 25,
        readjustment_duration_ratio = 0.25,
        click_delay = 0.05,
        click_delay_variation = 0.1,
        click_duration = 0.05,
        click_duration_variation = 0.1,
        scroll_speed = 1000,
        scroll_speed_variation = 0.1,
        scroll_duration = 0,
        scroll_duration_variation = 0,
        scroll_step = 120,
        scroll_pause_variation = 0.1
    )
    mouse = Mouse(mouse_physics)
    ```
    """
    speed: float = 0
    minimum_speed: float = 0
    maximum_speed: float = 0
    speed_variation: float = 0
    duration: float = 0
    duration_variation: float = 0
    base_duration: float = 0
    base_duration_variation: float = 0
    inconsistency: float = 0
    target_radius: float = 0
    readjustment_duration_ratio: float = 0.25
    click_delay: float = 0.05
    click_delay_variation: float = 0
    click_duration: float = 0.05
    click_duration_variation: float = 0
    scroll_speed: float = 0
    scroll_speed_variation: float = 0
    scroll_duration: float = 0
    scroll_duration_variation: float = 0
    scroll_step: int = 1
    scroll_pause_variation: float = 0
    wander_delay: float = 0
    wander_delay_variation: float = 0
    wander_distance_ratio: float = 0
    wander_distance_ratio_variation: float = 0

    def __post_init__(self) -> None:
        _validate_between_range(
            speed = self.speed,
            minimum_speed = self.minimum_speed,
            maximum_speed = self.maximum_speed,
            speed_variation = self.speed_variation,
            duration = self.duration,
            duration_variation = self.duration_variation,
            base_duration = self.base_duration,
            base_duration_variation = self.base_duration_variation,
            inconsistency = self.inconsistency,
            target_radius = self.target_radius,
            click_delay = self.click_delay,
            click_delay_variation = self.click_delay_variation,
            click_duration = self.click_duration,
            click_duration_variation = self.click_duration_variation,
            scroll_speed = self.scroll_speed,
            scroll_speed_variation = self.scroll_speed_variation,
            scroll_duration = self.scroll_duration,
            scroll_duration_variation = self.scroll_duration_variation,
            scroll_pause_variation = self.scroll_pause_variation,
            wander_delay = self.wander_delay,
            wander_delay_variation = self.wander_delay_variation,
            wander_distance_ratio = self.wander_distance_ratio,
            wander_distance_ratio_variation = self.wander_distance_ratio_variation,
        )
        _validate_between_range(0, 1, readjustment_duration_ratio = self.readjustment_duration_ratio)
        _validate_between_range(1, math.inf, scroll_step = self.scroll_step)