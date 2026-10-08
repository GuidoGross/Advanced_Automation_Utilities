from ._wait import _Wait
from ._wait_random import _WaitRandom
from ._wait_until import _WaitUntil
from typing import Callable

class Timing:
    """
    **Description:**

    Precise delays, chronometers, and condition-based execution flow. Use this module to introduce smart waits that continuously poll for conditions, simulate human-like random pauses, or precisely benchmark the execution time of your functions.
    """
    def wait(self, duration: float) -> None:
        """
        **`Timing().wait()`:** Pauses execution for an exact amount of seconds.

        **Description:**

        Pauses execution for an exact amount of seconds. It acts as a safe, responsive wrapper around standard sleep mechanisms, ensuring that long pauses can still be instantly interrupted if the global kill switch is triggered.

        **Arguments:**

        - **`duration` (`float`):** Seconds. Must be ≥ 0.

        **Returns:**

        **`None`**

        **Example:**

        ```python
        Timing().wait(duration = 2.5)
        ```

        **Note:**

        This internally uses the global `KILL_SWITCH_EVENT`, meaning if the Kill Switch is triggered during a wait, the wait is aborted instantly.
        """
        return _Wait(duration = duration).execute()

    def wait_random(self, minimum_duration: float, maximum_duration: float) -> None:
        """
        **`Timing().wait_random()`:** Pauses execution for a random duration between two limits.

        **Description:**

        Pauses execution for a random duration between two limits. This is particularly useful for simulating human unpredictability and preventing strict pattern recognition in automated tasks.

        **Arguments:**

        - **`minimum_duration` (`float`):** Seconds. Must be ≥ 0.
        - **`maximum_duration` (`float`):** Seconds. Must be ≥ 0.

        **Returns:**

        **`None`**

        **Example:**

        ```python
        Timing().wait_random(minimum_duration = 1, maximum_duration = 3)
        ```
        """
        return _WaitRandom(
            minimum_duration = minimum_duration, maximum_duration = maximum_duration
        ).execute()

    def wait_until(
        self,
        condition_function: Callable[[], bool],
        timeout: float = 0,
        poll_interval: float = 0.1
    ) -> bool:
        """
        **`Timing().wait_until()`:** Pauses execution until a given condition function is met.

        **Description:**

        Continuously polls the condition function at a specified interval until is met or the timeout is reached.

        **Arguments:**

        - **`condition_function` (`Callable[[], bool]`)**
        - **`timeout` (`float`):** Seconds. Must be ≥ 0.
        - **`poll_interval` (`float`):** Seconds. Must be > 0.

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        Timing().wait_until(
            condition_function = lambda: KeyboardInfo().is_pressed("shift"),
            timeout = 10,
            poll_interval = 0.1
        )
        ```
        """
        return _WaitUntil(
            condition_function = condition_function,
            timeout = timeout,
            poll_interval = poll_interval
        ).execute()