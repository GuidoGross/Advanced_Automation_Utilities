from ._task import Task

class _AsynchronousContext:
    def __init__(self, controller):
        self.controller = controller
        self.task = Task()

    def __enter__(self):
        self.controller._queue_mode = True
        self.controller._queue.clear()
        return self.task

    def __exit__(self, exc_type, exc_value, traceback):
        self.controller._queue_mode = False
        if not exc_type and self.controller._queue:
            self.task._actions = list(self.controller._queue)
            self.controller._task_queue.put(self.task)
            self.controller._ensure_worker_running()
        else: self.task._done_event.set()
        self.controller._queue.clear()