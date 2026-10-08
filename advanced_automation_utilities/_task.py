from typing import Any
import threading

class Task:
    """
    **Description:**

    Represents an asynchronous sequence of actions.
    """
    def __init__(self) -> None:
        self._actions: list[Any] = []
        self._cancel_event: threading.Event = threading.Event()
        self._done_event: threading.Event = threading.Event()
        self._exception: BaseException | None = None
        self._cancelled: bool = False
        self.results: list[Any] = []
        self.last_result: Any = None

    def wait(self) -> None:
        """
        **Description:**

        Blocks the calling thread until the task is complete or cancelled.

        **Returns:**

        **`None`**

        **Example:**

        ```python
        with mouse.asynchronous() as mouse_task: mouse.move(x = 500, y = 500)
        mouse_task.wait()
        ```
        """
        self._done_event.wait()
        if self._exception: raise self._exception

    def cancel(self) -> None:
        """
        **Description:**

        Cancels the task if it hasn't started or is currently running.

        **Returns:**

        **`None`**

        **Example:**

        ```python
        with mouse.asynchronous() as mouse_task: mouse.move(x = 250, y = 500)
        image_found = screen.locate_image(
            image_path = "error.png",
            confidence = 0.9,
            region = [250, 250, 500, 500],
            monitor_index = 0
        )
        if image_found: mouse_task.cancel()
        ```
        """
        self._cancelled = True
        self._cancel_event.set()

    @property
    def is_done(self) -> bool:
        """
        **Description:**

        Checks if the task is complete or cancelled.

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        with keyboard.asynchronous() as keyboard_task: keyboard.write("Hello, world!")
        with mouse.asynchronous() as mouse_task:
            mouse.wander_until(condition_function = lambda: keyboard_task.is_done)
        ```
        """
        return self._done_event.is_set()