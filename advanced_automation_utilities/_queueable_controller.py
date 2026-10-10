from ._task import Task
from ._asynchronous_context import _AsynchronousContext
from .timing._wait import _Wait
from .timing._wait_random import _WaitRandom
from .timing._wait_until import _WaitUntil
from ._kill_switch_event import KILL_SWITCH_EVENT
from .exceptions import KillSwitchTriggered
from typing import Any, Callable, Self
import queue
import threading

class _QueueableController:
    def __init__(self):
        self._queue_mode: bool = False
        self._queue: list[Any] = []
        self._task_queue: queue.Queue[Task] = queue.Queue()
        self._worker_thread: threading.Thread | None = None
        self.results: list[Any] = []
        self.last_result: Any = None

    def asynchronous(self):
        """
        **Description:**

        Context manager to queue actions and execute them asynchronously.
        Returns a Task object that can be awaited or cancelled.

        **Returns:**

        **`Task`**

        **Example:**

        ```python
        with mouse.asynchronous() as mouse_task:
            mouse.click(x = 250, y = 500)
            mouse.scroll(amount = 1000, direction = "down")
        ```
        """
        return _AsynchronousContext(self)

    def wait(self, duration: float) -> Self:
        """
        **Description:**

        Pauses execution for an exact amount of seconds.
        Can be chained and queued asynchronously.

        **Arguments:**

        - **`duration` (`float`):** Seconds. Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        with mouse.asynchronous() as mouse_task: mouse.wait(duration = 2.5)
        ```
        """
        return self._execute_or_queue(_Wait(duration = duration))

    def wait_random(self, minimum_duration: float, maximum_duration: float) -> Self:
        """
        **Description:**

        Pauses execution for a random duration between two limits.
        Can be chained and queued asynchronously.

        **Arguments:**

        - **`minimum_duration` (`float`):** Seconds. Must be ≥ 0.
        - **`maximum_duration` (`float`):** Seconds. Must be ≥ 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        with mouse.asynchronous() as mouse_task:
            mouse.wait_random(minimum_duration = 1, maximum_duration = 3)
        ```
        """
        return self._execute_or_queue(_WaitRandom(
            minimum_duration = minimum_duration, maximum_duration = maximum_duration
        ))

    def wait_until(
        self, condition_function: Callable[[], bool], timeout: float = 0, poll_interval: float = 0.1
    ) -> Self:
        """
        **Description:**

        Pauses execution until a given function or lambda condition evaluates to True.
        Can be chained and queued asynchronously.

        **Arguments:**

        - **`condition_function` (`Callable[[], bool]`)**
        - **`timeout` (`float`):** Seconds. Must be ≥ 0.
        - **`poll_interval` (`float`):** Seconds. Must be > 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        with mouse.asynchronous() as mouse_task:
            mouse.wait_until(
                condition_function = lambda: KeyboardInfo().is_pressed(key = "shift"),
                timeout = 5,
                poll_interval = 0.1
            )
        ```
        """
        return self._execute_or_queue(_WaitUntil(
            condition_function = condition_function,
            timeout = timeout,
            poll_interval = poll_interval
        ))

    def _ensure_worker_running(self):
        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_thread = threading.Thread(
                target = self._worker_loop, daemon = True, name = f"worker_thread_{id(self)}"
            )
            self._worker_thread.start()

    def _worker_loop(self):
        while True:
            task = None
            try:
                task = self._task_queue.get()
                if task is None: break
                if task._cancelled or KILL_SWITCH_EVENT.is_set():
                    task._done_event.set()
                    continue
                try:
                    for action in task._actions:
                        if task._cancelled or KILL_SWITCH_EVENT.is_set(): break
                        import inspect
                        if "stop_event" in inspect.signature(action.execute).parameters:
                            result = action.execute(stop_event = task._cancel_event)
                        else: result = action.execute()
                        task.results.append(result)
                        task.last_result = result
                except BaseException as error:
                    task._exception = error
                    if not isinstance(error, (Exception, KillSwitchTriggered)): raise
                finally: task._done_event.set()
            except BaseException:
                if task is not None and not task._done_event.is_set():
                    task._exception = KillSwitchTriggered()
                    task._done_event.set()
                continue

    def _execute_or_queue(self, action):
        if self._queue_mode: self._queue.append(action)
        else:
            result = action.execute()
            self.results.append(result)
            self.last_result = result
        return self