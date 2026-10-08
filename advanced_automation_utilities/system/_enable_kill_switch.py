from ._system_action import _SystemAction
from .._kill_switch_event import KILL_SWITCH_EVENT
from ..backend.windows._keyboard import _enable_kill_switch

class _EnableKillSwitch(_SystemAction):
    def __init__(self, *keys): self.keys = list(keys)

    def execute(self):
        KILL_SWITCH_EVENT.clear()
        _enable_kill_switch(self.keys)