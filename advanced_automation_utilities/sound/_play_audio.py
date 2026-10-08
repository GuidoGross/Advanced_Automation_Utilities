from ._sound_action import _SoundAction
from .._utilities import _validate_file_exists
from ..backend.windows._sound import _play_audio

class _PlayAudio(_SoundAction):
    def __init__(self, file_path):
        self.file_path = file_path
        _validate_file_exists(self.file_path, "Audio file")

    def execute(self): _play_audio(self.file_path)