from ._system_action import _SystemAction
from ..backend.windows._system import _resize_window

class _ResizeWindow(_SystemAction):
    def __init__(self, window_title, width, height):
        self.window_title = window_title
        self.width = width
        self.height = height

    def execute(self): _resize_window(self.window_title, self.width, self.height)