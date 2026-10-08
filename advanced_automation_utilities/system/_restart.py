from ._system_action import _SystemAction
from .._utilities import _validate_between_range
from ..backend.windows._system import _restart

class _Restart(_SystemAction):
    def __init__(self, delay = 0):
        self.delay = delay
        _validate_between_range(delay = delay)

    def execute(self): _restart(self.delay)