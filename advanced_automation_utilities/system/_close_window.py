from ._system_action import _SystemAction
from ..backend.windows._system import _close_window

class _CloseWindow(_SystemAction):
    def __init__(self, window_title): self.window_title = window_title

    def execute(self): _close_window(self.window_title)