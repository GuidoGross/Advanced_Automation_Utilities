from ._system_action import _SystemAction
from ..backend.windows._system import _open_process
import os
import shutil

class _OpenProcess(_SystemAction):
    def __init__(self, process_path):
        self.process_path = process_path
        if not (os.path.exists(self.process_path) or shutil.which(self.process_path)):
            raise FileNotFoundError(
                f"The executable file \"{self.process_path}\" does not exist or could not be found."
            )

    def execute(self): _open_process(self.process_path)