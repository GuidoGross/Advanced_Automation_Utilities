from advanced_automation_utilities.keyboard import KeyboardPhysics, _write
from advanced_automation_utilities.keyboard._hotkey import _Hotkey
from advanced_automation_utilities.backend.windows._keyboard import _get_virtual_key_code
import advanced_automation_utilities.keyboard._hold_key as hold_module
import advanced_automation_utilities.keyboard._release_key as release_module
from hypothesis import strategies, settings, given
from dataclasses import FrozenInstanceError
import pytest

def test_virtual_key_scan_failure_is_reported_as_none_not_a_bogus_code():
    unmappable_character = "\U0001F600"
    assert _get_virtual_key_code(unmappable_character) is None

def test_keyboard_physics_is_immutable():
    physics = KeyboardPhysics(typing_error_chance = 0.05)
    with pytest.raises(FrozenInstanceError): physics.typing_error_chance = 1

def test_invalid_key_name_is_rejected_up_front():
    with pytest.raises(KeyError): _Hotkey("ctrl", "not_a_real_key").execute()

def test_hotkey_releases_only_the_keys_it_actually_held_in_reverse_order(monkeypatch):
    calls = []

    class Interrupted(Exception): pass

    def hold_that_interrupts_on_third_key(self):
        calls.append(("HOLD", self.key))
        if self.key == "esc": raise Interrupted()

    monkeypatch.setattr(hold_module._HoldKey, "execute", hold_that_interrupts_on_third_key)
    monkeypatch.setattr(
        release_module._ReleaseKey, "execute", lambda self: calls.append(("RELEASE", self.key))
    )
    with pytest.raises(Interrupted): _Hotkey("ctrl", "shift", "esc").execute()
    held = [key for action, key in calls if action == "HOLD"]
    released = [key for action, key in calls if action == "RELEASE"]
    assert held == ["ctrl", "shift", "esc"]
    assert released == ["shift", "ctrl"], "should release only the keys actually held, in reverse order"

@given(
    text = strategies.text(min_size = 0, max_size = 100),
    error_chance = strategies.floats(min_value = 0, max_value = 1, allow_nan = False),
    delayed_chance = strategies.floats(min_value = 0, max_value = 1, allow_nan = False),
)
@settings(deadline = None)
def test_write_produces_correct_text(text, error_chance, delayed_chance, fake_keyboard):
    fake_keyboard.text = ""
    fake_keyboard.cursor = 0
    physics = KeyboardPhysics(
        typing_error_chance = error_chance,
        typing_error_delayed_realization_chance = delayed_chance,
        press_delay = 0,
        press_delay_variation = 0,
        typing_error_correction_delay = 0,
        typing_error_correction_delay_variation = 0
    )
    _write._Write(text, physics = physics).execute()
    assert fake_keyboard.text == text