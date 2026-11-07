from ._task import Task
import contextvars

_ACTIVE_ASYNCHRONOUS_QUEUES = contextvars.ContextVar("_ACTIVE_ASYNCHRONOUS_QUEUES", default = {})
_ACTIVE_ASYNCHRONOUS_TASKS = contextvars.ContextVar("_ACTIVE_ASYNCHRONOUS_TASKS", default = {})

class _AsynchronousContext:
    def __init__(self, controller):
        self._controller = controller
        self._task = Task()
        self._is_nested = False

    def __enter__(self):
        controller_id = id(self._controller)
        queues_map = dict(_ACTIVE_ASYNCHRONOUS_QUEUES.get())
        tasks_map = dict(_ACTIVE_ASYNCHRONOUS_TASKS.get())
        queue_stack = list(queues_map.get(controller_id, []))
        task_stack = list(tasks_map.get(controller_id, []))
        if queue_stack:
            self._is_nested = True
            self._task = task_stack[-1]
            queue_stack.append(queue_stack[-1])
            task_stack.append(self._task)
        else:
            self._is_nested = False
            queue_stack.append([])
            task_stack.append(self._task)
        queues_map[controller_id] = queue_stack
        tasks_map[controller_id] = task_stack
        _ACTIVE_ASYNCHRONOUS_QUEUES.set(queues_map)
        _ACTIVE_ASYNCHRONOUS_TASKS.set(tasks_map)
        return self._task

    def __exit__(self, exc_type, exc_val, exc_tb):
        controller_id = id(self._controller)
        queues_map = dict(_ACTIVE_ASYNCHRONOUS_QUEUES.get())
        tasks_map = dict(_ACTIVE_ASYNCHRONOUS_TASKS.get())
        queue_stack = list(queues_map.get(controller_id, []))
        task_stack = list(tasks_map.get(controller_id, []))
        if queue_stack:
            actions = queue_stack.pop()
            if queue_stack: queues_map[controller_id] = queue_stack
            else: queues_map.pop(controller_id, None)
            _ACTIVE_ASYNCHRONOUS_QUEUES.set(queues_map)
            task_stack.pop()
            if task_stack: tasks_map[controller_id] = task_stack
            else: tasks_map.pop(controller_id, None)
            _ACTIVE_ASYNCHRONOUS_TASKS.set(tasks_map)
            if exc_type is not None:
                actions.clear()
                self._task._actions = []
                self._task._exception = exc_val
                self._task._done_event.set()
                return
            if not self._is_nested:
                self._task._actions = actions
                self._controller._submit_task(self._task)