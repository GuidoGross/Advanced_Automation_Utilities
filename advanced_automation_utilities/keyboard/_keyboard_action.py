from .keyboard_physics import KeyboardPhysics
from abc import ABC, abstractmethod

class _KeyboardAction(ABC):
    def __init__(self, physics = None): self.physics = physics or KeyboardPhysics()

    @abstractmethod
    def execute(self): pass