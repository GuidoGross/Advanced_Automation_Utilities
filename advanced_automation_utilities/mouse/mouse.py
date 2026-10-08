from .mouse_physics import MousePhysics
from ._move import _Move
from ._hold_click import _HoldClick
from ._release_click import _ReleaseClick
from ._click import _Click
from ._drag_and_drop import _DragAndDrop
from ._scroll import _Scroll
from ._scroll_until import _ScrollUntil
from ._wander import _Wander
from ._wander_until import _WanderUntil
from .._queueable_controller import _QueueableController
from .._typing import MouseButton, ScrollDirection
from typing import Optional, Self, Callable

class Mouse(_QueueableController):
    """
    **Description:**

    Native pointer manipulation governed by Bézier-curve physics to simulate authentic human behavior. Perform smooth movements, random wandering, and complex dragging operations while remaining undetected by simple anti-bot mechanisms.
    """
    def __init__(self, physics: Optional[MousePhysics] = None) -> None:
        """
        **Description:**

        Initializes the Mouse controller.

        **Arguments:**

        - **`physics` (`Optional[MousePhysics]`)**

        **Returns:**

        **`None`**
        """
        super().__init__()
        self.physics = physics or MousePhysics()

    def move(self, x: int, y: int) -> Self:
        """
        **`Mouse().move()`:** Moves the pointer to the specified coordinates smoothly based on the configured physics.

        **Description:**

        Generates a realistic Bézier curve from the current pointer location to the target. The trajectory, speed, and overshoots are governed by `MousePhysics`.

        **Arguments:**

        - **`x` (`int`)**
        - **`y` (`int`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().move(x = 250, y = 500)
        ```

        **Note:**

        Because it uses Bézier curves, the mouse will naturally curve and accelerate/decelerate just like a real human hand.
        """
        return self._execute_or_queue(_Move(x = x, y = y, physics = self.physics))

    def hold_click(
        self, x: Optional[int] = None, y: Optional[int] = None, button: MouseButton = "left"
    ) -> Self:
        """
        **`Mouse().hold_click()`:** Holds down a mouse button at specified coordinates.

        **Description:**

        Sends the physical DOWN signal for the mouse button without releasing it.

        **Arguments:**

        - **`x` (`Optional[int]`)**
        - **`y` (`Optional[int]`)**
        - **`button` (`str`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().hold_click(x = 250, y = 500, button = "left")
        ```

        **Warning:**

        Always ensure you eventually call `release_click()` to avoid leaving the system in a locked state.
        """
        return self._execute_or_queue(_HoldClick(x = x, y = y, button = button, physics = self.physics))

    def release_click(
        self, x: Optional[int] = None, y: Optional[int] = None, button: MouseButton = "left"
    ) -> Self:
        """
        **`Mouse().release_click()`:** Releases a previously held mouse button at specified coordinates.

        **Description:**

        Sends the physical UP signal for the mouse button.

        **Arguments:**

        - **`x` (`Optional[int]`)**
        - **`y` (`Optional[int]`)**
        - **`button` (`str`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().release_click(x = 250, y = 500, button = "left")
        ```
        """
        return self._execute_or_queue(
            _ReleaseClick(x = x, y = y, button = button, physics = self.physics)
        )

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: MouseButton = "left",
        clicks: int = 1
    ) -> Self:
        """
        **`Mouse().click()`:** Clicks the mouse at specified coordinates.

        **Description:**

        Simulates a physical click (DOWN and UP events) with a customizable, randomized delay in between.

        **Arguments:**

        - **`x` (`Optional[int]`)**
        - **`y` (`Optional[int]`)**
        - **`button` (`str`):** Valid options: "left", "right", "middle". Matching is case-insensitive.
        - **`clicks` (`int`):** Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().click(x = 250, y = 500, button = "left", clicks = 1)
        ```

        **Tip:**

        Passing `x` and `y` automatically moves the pointer to that location before clicking. It is exactly equivalent to `Mouse().move(x, y).click()`.
        """
        return self._execute_or_queue(
            _Click(x = x, y = y, button = button, clicks = clicks, physics = self.physics)
        )

    def double_click(
        self, x: Optional[int] = None, y: Optional[int] = None, button: MouseButton = "left"
    ) -> Self:
        """
        **`Mouse().double_click()`:** Performs a double click at specified coordinates.

        **Description:**

        A convenient wrapper around `click()` that forces `clicks = 2`.

        **Arguments:**

        - **`x` (`Optional[int]`)**
        - **`y` (`Optional[int]`)**
        - **`button` (`str`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().double_click(x = 250, y = 500, button = "left")
        ```
        """
        return self.click(x = x, y = y, button = button, clicks = 2)

    def right_click(
        self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1
    ) -> Self:
        """
        **`Mouse().right_click()`:** Performs a right click at specified coordinates.

        **Description:**

        A convenient wrapper around `click()` that forces `button = "right"`.

        **Arguments:**

        - **`x` (`Optional[int]`)**
        - **`y` (`Optional[int]`)**
        - **`clicks` (`int`):** Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().right_click(x = 250, y = 500, clicks = 1)
        ```
        """
        return self.click(x = x, y = y, button = "right", clicks = clicks)

    def middle_click(
        self, x: Optional[int] = None, y: Optional[int] = None, clicks: int = 1
    ) -> Self:
        """
        **`Mouse().middle_click()`:** Performs a middle click at specified coordinates.

        **Description:**

        A convenient wrapper around `click()` that forces `button = "middle"`.

        **Arguments:**

        - **`x` (`Optional[int]`)**
        - **`y` (`Optional[int]`)**
        - **`clicks` (`int`):** Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().middle_click(x = 100, y = 200, clicks = 1)
        ```
        """
        return self.click(x = x, y = y, button = "middle", clicks = clicks)

    def drag_and_drop(
        self, start_x: int, start_y: int, end_x: int, end_y: int, button: MouseButton = "left"
    ) -> Self:
        """
        **`Mouse().drag_and_drop()`:** Drags an item from start to end coordinates smoothly, based on the configured physics.

        **Description:**

        Moves to the start coordinates, holds the specified button, waits, smoothly moves to the end coordinates, waits again, and releases the button.

        **Arguments:**

        - **`start_x` (`int`)**
        - **`start_y` (`int`)**
        - **`end_x` (`int`)**
        - **`end_y` (`int`)**
        - **`button` (`str`):** Valid options: "left", "right", "middle". Matching is case-insensitive.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().drag_and_drop(start_x = 250, start_y = 500, end_x = 750, end_y = 250, button = "left")
        ```

        **Note:**

        Short pauses are automatically inserted before moving and before releasing to simulate a human confirming the grab and drop actions.
        """
        return self._execute_or_queue(
            _DragAndDrop(
                start_x = start_x,
                start_y = start_y,
                end_x = end_x,
                end_y = end_y,
                button = button,
                physics = self.physics
            )
        )

    def scroll(self, amount: int, direction: ScrollDirection = "down") -> Self:
        """
        **`Mouse().scroll()`:** Scrolls the mouse wheel by the specified amount in the specified direction.

        **Description:**

        Sends discrete mouse wheel signals to scroll the active window.

        **Arguments:**

        - **`amount` (`int`):** Must be ≥ 0.
        - **`direction` (`str`):** Valid options are "up", "down", "left", or "right". Matching is case-insensitive.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().scroll(amount = 1000, direction = "down")
        ```
        """
        return self._execute_or_queue(
            _Scroll(amount = amount, direction = direction, physics = self.physics)
        )

    def scroll_until(
        self,
        condition_function: Callable[[], bool],
        amount: int = 0,
        direction: ScrollDirection = "down",
        timeout: float = 0,
        poll_interval: float = 0.1
    ) -> Self:
        """
        **`Mouse().scroll_until()`:** Scrolls the mouse wheel continuously until a condition is met.

        **Description:**

        Executes in a loop, scrolling step by step while periodically until either the `condition_function` is met or the `amount`/`timeout` is reached.

        **Arguments:**

        - **`condition_function` (`Callable[[], bool]`)**
        - **`amount` (`int`):** Must be ≥ 0.
        - **`direction` (`str`):** Valid options are "up", "down", "left", or "right". Matching is case-insensitive.
        - **`timeout` (`float`):** Seconds. Must be ≥ 0.
        - **`poll_interval` (`float`):** Seconds. Must be > 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().scroll_until(
            condition_function = lambda: KeyboardInfo().is_pressed("shift"),
            amount = 1000,
            direction = "down",
            timeout = 5,
            poll_interval = 0.1
        )
        ```
        """
        return self._execute_or_queue(
            _ScrollUntil(
                condition_function = condition_function,
                amount = amount,
                direction = direction,
                timeout = timeout,
                poll_interval = poll_interval,
                physics = self.physics
            )
        )

    def wander(
        self,
        duration: float = 10,
        region: Optional[tuple[int, int, int, int]] = None,
        maximum_steps: Optional[int] = None
    ) -> Self:
        """
        **`Mouse().wander()`:** Simulates idle mouse wandering by moving the pointer around randomly.

        **Description:**

        Generates erratic but smooth Bézier movements around a specific region, to keep the computer awake or simulate idle human activity.

        **Arguments:**

        - **`duration` (`float`):** Seconds. Must be ≥ 0.
        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`maximum_steps` (`Optional[int]`):** Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().wander(duration = 10, region = (250, 250, 500, 500), maximum_steps = 3)
        ```

        **Note:**

        Although random, the movements generally tend toward the center of the region.
        """
        return self._execute_or_queue(_Wander(duration, region, maximum_steps, physics = self.physics))

    def wander_until(
        self,
        condition_function: Callable[[], bool],
        region: Optional[tuple[int, int, int, int]] = None,
        maximum_steps: Optional[int] = None,
        timeout: float = 0,
        poll_interval: float = 0.1
    ) -> Self:
        """
        **`Mouse().wander_until()`:** Simulates idle mouse wandering continuously until a condition is met.

        **Description:**

        Executes the wander logic until the `condition_function` is met or the `maximum_steps`/`timeout` is reached.

        **Arguments:**

        - **`condition_function` (`Callable[[], bool]`)**
        - **`region` (`Optional[tuple[int, int, int, int]]`):** Format: (left, top, right, bottom).
        - **`maximum_steps` (`Optional[int]`):** Must be ≥ 0.
        - **`timeout` (`float`):** Seconds. Must be ≥ 0.
        - **`poll_interval` (`float`):** Seconds. Must be > 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Mouse().wander_until(
            condition_function = lambda: KeyboardInfo().is_pressed("shift"),
            region = (250, 250, 500, 500),
            maximum_steps = 3,
            timeout = 5,
            poll_interval = 0.1
        )
        ```
        """
        return self._execute_or_queue(
            _WanderUntil(
                condition_function = condition_function,
                region = region,
                maximum_steps = maximum_steps,
                timeout = timeout,
                poll_interval = poll_interval,
                physics = self.physics
            )
        )