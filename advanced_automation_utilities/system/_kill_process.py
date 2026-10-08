from ._system_action import _SystemAction
from ..backend.windows._system import _kill_process

class _KillProcess(_SystemAction):
    def __init__(self, process, force = True):
        self.process = process
        self.force = force

    def execute(self): _kill_process(self.process, self.force)