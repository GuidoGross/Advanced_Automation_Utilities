from ._press_key import _PressKey
from ._keyboard_action import _KeyboardAction
from .._utilities import _apply_variation
from ..timing import Timing
from ..backend.windows._keyboard import _send_unicode
import random
from dataclasses import replace
import string

class _Write(_KeyboardAction):
    _FAST_NAVIGATION_SPEED_DIVISOR = 3
    _MAXIMUM_BACKSPACE_CORRECTION_LENGTH = 5

    def __init__(self, text, physics = None):
        super().__init__(physics = physics)
        self.text = text

    def execute(self):
        timing = Timing()
        correction_physics, fast_navigation_physics = self._setup_physics()
        index = 0
        while index < len(self.text):
            character = self.text[index]
            if self.physics.typing_error_chance > 0 and random.random() < self.physics.typing_error_chance:
                index = self._simulate_typing_error(
                    index, character, timing, correction_physics, fast_navigation_physics
                )
                continue
            _send_unicode(character)
            if index < len(self.text) - 1:
                self._wait_press_delay(timing)
            index += 1

    def _setup_physics(self):
        correction_physics = replace(
            self.physics,
            press_delay = self.physics.typing_error_correction_delay,
            press_delay_variation = self.physics.typing_error_correction_delay_variation
        )
        fast_navigation_physics = replace(
            self.physics,
            press_delay = self.physics.press_delay / self._FAST_NAVIGATION_SPEED_DIVISOR
        )
        return correction_physics, fast_navigation_physics

    def _wait_press_delay(self, timing, custom_physics = None):
        physics = custom_physics or self.physics
        delay = physics.press_delay
        if physics.press_delay_variation > 0:
            delay = _apply_variation(delay, physics.press_delay_variation)
        timing.wait(max(0, delay))

    def _simulate_typing_error(
        self, index, correct_character, timing, correction_physics, fast_navigation_physics
    ):
        possible_characters = string.ascii_letters.replace(correct_character, "")
        incorrect_character = random.choice(possible_characters) if possible_characters else "a"
        _send_unicode(incorrect_character)
        extra_characters_typed = self._type_extra_characters(index, timing)
        if extra_characters_typed < self._MAXIMUM_BACKSPACE_CORRECTION_LENGTH:
            self._correct_with_backspace(
                correct_character,
                index,
                extra_characters_typed,
                timing,
                correction_physics,
                fast_navigation_physics
            )
        else:
            self._correct_with_arrows(
                correct_character,
                extra_characters_typed,
                timing,
                correction_physics,
                fast_navigation_physics
            )
        after_correction_delay = self.physics.typing_error_correction_delay
        if self.physics.typing_error_correction_delay_variation > 0:
            after_correction_delay = _apply_variation(
                after_correction_delay, self.physics.typing_error_correction_delay_variation
            )
        timing.wait(max(0, after_correction_delay))
        return index + extra_characters_typed + 1

    def _type_extra_characters(self, current_index, timing):
        extra_characters_typed = 0
        while current_index + 1 + extra_characters_typed < len(self.text):
            if random.random() < self.physics.typing_error_delayed_realization_chance:
                self._wait_press_delay(timing)
                _send_unicode(self.text[current_index + 1 + extra_characters_typed])
                extra_characters_typed += 1
            else: break
        return extra_characters_typed

    def _correct_with_backspace(
        self,
        correct_character,
        current_index,
        extra_characters_typed,
        timing,
        correction_physics,
        fast_navigation_physics
    ):
        for j in range(extra_characters_typed + 1):
            physics = correction_physics if j == 0 else fast_navigation_physics
            _PressKey("backspace", physics = physics).execute()
        _send_unicode(correct_character)
        for j in range(extra_characters_typed):
            self._wait_press_delay(timing)
            _send_unicode(self.text[current_index + 1 + j])

    def _correct_with_arrows(
        self,
        correct_character,
        extra_characters_typed,
        timing,
        correction_physics,
        fast_navigation_physics
    ):
        self._wait_press_delay(timing, custom_physics = correction_physics)
        for _ in range(extra_characters_typed):
            _PressKey("left_arrow", physics = fast_navigation_physics).execute()
        _PressKey("backspace", physics = fast_navigation_physics).execute()
        _send_unicode(correct_character)
        for _ in range(extra_characters_typed):
            _PressKey("right_arrow", physics = fast_navigation_physics).execute()