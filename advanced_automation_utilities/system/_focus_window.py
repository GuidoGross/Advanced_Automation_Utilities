from ._system_action import _SystemAction
from ..backend.windows._system import _focus_window

class _FocusWindow(_SystemAction):
    def __init__(self, window_title): self.window_title = window_title

    def execute(self): _focus_window(self.window_title)