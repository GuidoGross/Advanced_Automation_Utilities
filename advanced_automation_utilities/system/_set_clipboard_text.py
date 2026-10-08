from ._system_action import _SystemAction
from ..backend.windows._system import _set_clipboard_text

class _SetClipboardText(_SystemAction):
    def __init__(self, text): self.text = text

    def execute(self): _set_clipboard_text(str(self.text))