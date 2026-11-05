from ._task import Task
import contextvars

_ACTIVE_ASYNCHRONOUS_QUEUES = contextvars.ContextVar("_ACTIVE_ASYNCHRONOUS_QUEUES", default = {})

class _AsynchronousContext:
    def __init__(self, controller):
        self._controller = controller
        self._task = Task()

    def __enter__(self):
        queues_map = dict(_ACTIVE_ASYNCHRONOUS_QUEUES.get())
        controller_id = id(self._controller)
        stack = list(queues_map.get(controller_id, []))
        stack.append([])
        queues_map[controller_id] = stack
        _ACTIVE_ASYNCHRONOUS_QUEUES.set(queues_map)
        return self._task

    def __exit__(self, exc_type, exc_val, exc_tb):
        queues_map = dict(_ACTIVE_ASYNCHRONOUS_QUEUES.get())
        controller_id = id(self._controller)
        stack = list(queues_map.get(controller_id, []))
        if stack:
            actions = stack.pop()
            if stack: queues_map[controller_id] = stack
            else: queues_map.pop(controller_id, None)
            _ACTIVE_ASYNCHRONOUS_QUEUES.set(queues_map)
            self._task._actions = actions
            self._controller._submit_task(self._task)