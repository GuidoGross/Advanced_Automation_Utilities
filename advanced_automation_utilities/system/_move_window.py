from ._system_action import _SystemAction
from ..backend.windows._system import _move_window

class _MoveWindow(_SystemAction):
    def __init__(self, window_title, x, y):
        self.window_title = window_title
        self.x = x
        self.y = y

    def execute(self): _move_window(self.window_title, self.x, self.y)