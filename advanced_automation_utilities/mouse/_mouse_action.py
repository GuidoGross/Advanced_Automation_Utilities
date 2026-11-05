from .mouse_physics import MousePhysics
from abc import ABC, abstractmethod

class _MouseAction(ABC):
    def __init__(self, physics = None):
        self.physics = physics if physics else MousePhysics()

    @abstractmethod
    def execute(self):
        pass