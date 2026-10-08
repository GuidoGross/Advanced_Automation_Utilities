from ._sound_action import _SoundAction
from .._utilities import _validate_options
from ..backend.windows._sound import _play_system_sound

class _PlaySystemSound(_SoundAction):
    def __init__(self, sound_type):
        self.sound_type = sound_type
        _validate_options(
            self.sound_type.lower(), ["info", "warning", "error", "question", "ok"], "system sound type"
        )

    def execute(self): _play_system_sound(self.sound_type)