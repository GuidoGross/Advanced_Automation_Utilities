**[Home](Home)** ➔ **[Physics](Physics)**

<div align = "center">

# **Physics**

**To evade bot-detection mechanisms and simulate real user interactions, both `Mouse` and `Keyboard` modules are governed by highly configurable, immutable dataclasses (`MousePhysics` and `KeyboardPhysics`) that force pointer movements to follow randomized Bézier curves with dynamic speeds and overshoots, while making keyboard typing simulate human delays, keystroke variations, and even random typos with delayed corrections.**

</div>

---

> [!TIP]
> Physics parameters are highly granular. You can pass a custom physics object to their respective facades to alter their simulation parameters dynamically.

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

---

## **MousePhysics**

Configures movement, clicking, scrolling, and wandering behavior.

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

---

## **KeyboardPhysics**

Configures keyboard timing and typing behavior.

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