from .._utilities import _validate_between_range
from dataclasses import dataclass

@dataclass(frozen = True)
class KeyboardPhysics:
    """
    **Description:**

    Configuration class that defines the timing characteristics
    for keyboard actions, allowing for human-like typing speeds or instantaneous execution.

    **Arguments:**

    - **`press_delay` (`float`):** Seconds. Must be ≥ 0.
    - **`press_delay_variation` (`float`):** Must be ≥ 0.
    - **`press_duration` (`float`):** Seconds. Must be ≥ 0.
    - **`press_duration_variation` (`float`):** Must be ≥ 0.
    - **`hotkey_delay` (`float`):** Seconds. Must be ≥ 0.
    - **`hotkey_delay_variation` (`float`):** Must be ≥ 0.
    - **`typing_error_chance` (`float`):** Must be ≥ 0 and ≤ 1.
    - **`typing_error_correction_delay` (`float`):** Seconds. Must be ≥ 0.
    - **`typing_error_correction_delay_variation` (`float`):** Must be ≥ 0.
    - **`typing_error_delayed_realization_chance` (`float`):** Must be ≥ 0 and ≤ 1.
    - **`auto_repeat` (`bool`)**

    **Example:**

    ```python
    keyboard_physics = KeyboardPhysics(
        press_delay = 0.15,
        press_delay_variation = 0.5,
        press_duration = 0.05,
        press_duration_variation = 0.1,
        hotkey_delay = 0.01,
        hotkey_delay_variation = 0.5,
        typing_error_chance = 0.025,
        typing_error_correction_delay = 0.25,
        typing_error_correction_delay_variation = 0.5,
        typing_error_delayed_realization_chance = 0.5,
        auto_repeat = True
    )
    keyboard = Keyboard(keyboard_physics)
    ```
    """
    press_delay: float = 0.05
    press_delay_variation: float = 0
    press_duration: float = 0.05
    press_duration_variation: float = 0
    hotkey_delay: float = 0.01
    hotkey_delay_variation: float = 0
    typing_error_chance: float = 0
    typing_error_correction_delay: float = 0.1
    typing_error_correction_delay_variation: float = 0
    typing_error_delayed_realization_chance: float = 0
    auto_repeat: bool = True

    def __post_init__(self) -> None:
        _validate_between_range(
            press_delay = self.press_delay,
            press_delay_variation = self.press_delay_variation,
            press_duration = self.press_duration,
            press_duration_variation = self.press_duration_variation,
            hotkey_delay = self.hotkey_delay,
            hotkey_delay_variation = self.hotkey_delay_variation,
            typing_error_correction_delay = self.typing_error_correction_delay,
            typing_error_correction_delay_variation = self.typing_error_correction_delay_variation,
        )
        _validate_between_range(0, 1,
            typing_error_chance = self.typing_error_chance,
            typing_error_delayed_realization_chance = self.typing_error_delayed_realization_chance,
        )