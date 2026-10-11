from ._system_action import _SystemAction
from ..backend.windows._system import _open_file
import os
import shutil

class _OpenFile(_SystemAction):
    def __init__(self, file_path):
        self.file_path = file_path
        if not (os.path.exists(self.file_path) or shutil.which(self.file_path)):
            raise FileNotFoundError(
                f"The file \"{self.file_path}\" does not exist or could not be found."
            )

    def execute(self): _open_file(self.file_path)