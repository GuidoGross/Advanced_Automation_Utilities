from ._keyboard_action import _KeyboardAction
from ..backend.windows._keyboard import _get_virtual_key_code, _unblock_key

class _UnblockKey(_KeyboardAction):
    def __init__(self, key):
        if not _get_virtual_key_code(key):
            raise KeyError(f"The \"{key}\" key is not valid or supported.")
        super().__init__()
        self.key = key

    def execute(self): _unblock_key(self.key)