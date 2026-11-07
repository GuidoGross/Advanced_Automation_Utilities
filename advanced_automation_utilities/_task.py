from ._utilities import _validate_between_range
from typing import Any, Optional
import weakref
import threading

_ACTIVE_TASKS: weakref.WeakSet = weakref.WeakSet()

class Task:
    """
    **`Task`:** Tracks an asynchronous task and provides waiting, cancellation, and results.

    **Description:**

    Represents an asynchronous sequence of actions.
    """
    def __init__(self) -> None:
        self._actions: list[Any] = []
        self._cancel_event: threading.Event = threading.Event()
        self._done_event: threading.Event = threading.Event()
        self._exception: Optional[BaseException] = None
        self._cancelled: bool = False
        self.results: list[Any] = []
        self.last_result: Any = None
        _ACTIVE_TASKS.add(self)

    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        **`Task().wait()`:** Blocks until the task completes, is cancelled, or timeout expires.

        **Description:**

        Waits for every queued action to finish, for cancellation to stop the sequence, or until timeout seconds elapse. If an action raises an exception, the same exception is raised in the thread calling this method.

        **Arguments:**

        - **`timeout` (`Optional[float]`):** Maximum seconds to wait. Must be ≥ 0.

        **Returns:**

        **`bool`**

        **Example:**

        ```python
        with mouse.asynchronous() as mouse_task: mouse.move(x = 500, y = 500)
        completed = mouse_task.wait(timeout = 5)
        ```
        """
        if timeout is not None: _validate_between_range(timeout = timeout)
        completed = self._done_event.wait(timeout = timeout)
        if self._exception:
            raise self._exception
        return completed

    def cancel(self) -> None:
        """
        **`Task().cancel()`:** Cancels a task that has not started or is still running.

        **Description:**

        Requests cancellation of the queued sequence. Actions that have not started are skipped, and a running action receives the task's cancellation event so it can stop cooperatively.

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
        **`Task().is_done`:** Checks whether the task is complete or cancelled.

        **Description:**

        Returns True after the queued sequence has stopped, whether it completed, was cancelled, or ended because an action raised an exception.

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