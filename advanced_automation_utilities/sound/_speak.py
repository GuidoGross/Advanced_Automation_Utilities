from ._sound_action import _SoundAction
from ..backend.windows._sound import _speak

class _Speak(_SoundAction):
    def __init__(self, text): self.text = text

    def execute(self): _speak(self.text)