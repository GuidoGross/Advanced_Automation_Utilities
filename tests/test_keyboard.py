from advanced_automation_utilities.keyboard import KeyboardPhysics, _write
from advanced_automation_utilities.keyboard._block_key import _BlockKey
from advanced_automation_utilities.keyboard._unblock_key import _UnblockKey
from advanced_automation_utilities.keyboard._hold_key import _HoldKey
from advanced_automation_utilities.keyboard._release_key import _ReleaseKey
from advanced_automation_utilities.keyboard._press_key import _PressKey
from advanced_automation_utilities.keyboard._hotkey import _Hotkey
from advanced_automation_utilities.backend.windows._keyboard import _get_virtual_key_code
import advanced_automation_utilities.keyboard.keyboard as keyboard_module
import advanced_automation_utilities.keyboard._keyboard_action as keyboard_action_module
import advanced_automation_utilities.keyboard.keyboard_info as keyboard_info_module
import advanced_automation_utilities.keyboard._block_key as block_key_module
import advanced_automation_utilities.keyboard._unblock_key as unblock_key_module
import advanced_automation_utilities.keyboard._hold_key as hold_key_module
import advanced_automation_utilities.keyboard._release_key as release_key_module
import advanced_automation_utilities.keyboard._hotkey as hotkey_module
import advanced_automation_utilities.keyboard._write as write_module
from types import SimpleNamespace
from dataclasses import FrozenInstanceError
from hypothesis import strategies, settings, example, given
import pytest

def test_keyboard_facade_and_info_delegation(monkeypatch):
    recorded_calls = []
    for action_attribute, action_name in (
        ("_HoldKey", "hold"),
        ("_ReleaseKey", "release"),
        ("_PressKey", "press"),
        ("_Hotkey", "hotkey"),
        ("_BlockKey", "block"),
        ("_UnblockKey", "unblock"),
        ("_Write", "write")
    ):
        monkeypatch.setattr(
            keyboard_module,
            action_attribute,
            lambda *arguments, action_name = action_name, **keyword_arguments: SimpleNamespace(
                execute = lambda: recorded_calls.append(
                    (action_name, arguments, keyword_arguments)
                ) or action_name
            )
        )
    keyboard = keyboard_module.Keyboard()
    assert keyboard.hold_key("a") is keyboard
    assert keyboard.release_key("a") is keyboard
    assert keyboard.press_key("a") is keyboard
    assert keyboard.hotkey("ctrl", "a") is keyboard
    assert keyboard.block_key("a") is keyboard
    assert keyboard.unblock_key("a") is keyboard
    assert keyboard.write("hello") is keyboard
    assert [name for name, _, _ in recorded_calls] == [
        "hold", "release", "press", "hotkey", "block", "unblock", "write"
    ]
    monkeypatch.setattr(keyboard_info_module, "_get_virtual_key_code", lambda key: key == "a")
    monkeypatch.setattr(keyboard_info_module, "_is_pressed", lambda key: key == "a")
    assert keyboard_info_module.KeyboardInfo().is_pressed("a") is True
    with pytest.raises(KeyError): keyboard_info_module.KeyboardInfo().is_pressed("unsupported")

def test_abstract_keyboard_action_probe():
    class KeyboardActionProbe(keyboard_action_module._KeyboardAction):
        def execute(self): return super().execute()

    supplied_physics = KeyboardPhysics()
    assert KeyboardActionProbe().physics is not None
    assert KeyboardActionProbe(supplied_physics).physics is supplied_physics
    assert KeyboardActionProbe().execute() is None

def test_keyboard_physics_is_immutable():
    physics = KeyboardPhysics(typing_error_chance = 0.05)
    with pytest.raises(FrozenInstanceError): physics.typing_error_chance = 1

def test_virtual_key_scan_failure_is_reported_as_none_not_a_bogus_code():
    unmappable_character = "\U0001F600"
    assert _get_virtual_key_code(unmappable_character) is None

def test_block_key_sends_the_key_to_the_backend(monkeypatch):
    blocked = []
    monkeypatch.setattr(block_key_module, "_block_key", lambda key: blocked.append(key))
    _BlockKey("a").execute()
    assert blocked == ["a"]

def test_block_key_rejects_an_invalid_key():
    with pytest.raises(KeyError): _BlockKey("not_a_real_key")

def test_unblock_key_sends_the_key_to_the_backend(monkeypatch):
    unblocked = []
    monkeypatch.setattr(unblock_key_module, "_unblock_key", lambda key: unblocked.append(key))
    _UnblockKey("a").execute()
    assert unblocked == ["a"]

def test_unblock_key_rejects_an_invalid_key():
    with pytest.raises(KeyError): _UnblockKey("not_a_real_key")

def test_hold_key_without_auto_repeat_sends_the_key_down_exactly_once(monkeypatch):
    sent = []
    monkeypatch.setattr(
        hold_key_module, "_send_key", lambda key, key_released = False: sent.append(key)
    )
    monkeypatch.setattr(hold_key_module.Timing, "wait", lambda self, duration: None)
    physics = KeyboardPhysics(auto_repeat = False, press_delay = 0, press_delay_variation = 0)
    _HoldKey("a", physics = physics).execute()
    assert sent == ["a"]

def test_hold_key_with_auto_repeat_sends_the_key_more_than_once(monkeypatch):
    sent = []
    monkeypatch.setattr(
        hold_key_module, "_send_key", lambda key, key_released = False: sent.append(key)
    )
    monkeypatch.setattr(hold_key_module.Timing, "wait", lambda self, duration: None)
    physics = KeyboardPhysics(
        auto_repeat = True,
        press_delay = 0,
        press_delay_variation = 0,
        press_duration = 1.0,
        press_duration_variation = 0
    )
    _HoldKey("a", physics = physics).execute()
    assert sent.count("a") > 1

def test_hold_key_variation_and_auto_repeat_paths(monkeypatch):
    class FakeTiming:
        waits = []

        def wait(self, duration): self.waits.append(duration)

    monkeypatch.setattr(hold_key_module, "_get_virtual_key_code", lambda _: (65, 0))
    monkeypatch.setattr(hold_key_module, "Timing", FakeTiming)
    monkeypatch.setattr(hold_key_module, "_send_key", lambda *arguments, **keyword_arguments: None)
    monkeypatch.setattr(hold_key_module, "_apply_variation", lambda *_: -1)
    hold_key_module._HoldKey(
        "a",
        KeyboardPhysics(
            press_delay = 1,
            press_delay_variation = 1,
            press_duration = 1,
            press_duration_variation = 1,
            auto_repeat = False
        )
    ).execute()
    assert FakeTiming.waits[-2:] == [0, 0]
    FakeTiming.waits.clear()
    sent_keys = []
    monkeypatch.setattr(
        hold_key_module, "_send_key", lambda key, **keyword_arguments: sent_keys.append(key)
    )
    hold_key_module._HoldKey(
        "a", KeyboardPhysics(press_duration = 0.632, auto_repeat = True)
    ).execute()
    assert len(sent_keys) == 5
    monkeypatch.setattr(hold_key_module, "_get_virtual_key_code", lambda _: None)
    with pytest.raises(KeyError): hold_key_module._HoldKey("bad")

def test_hold_key_auto_repeat_stops_cleanly_when_the_remaining_time_is_short(monkeypatch):
    sent = []
    monkeypatch.setattr(
        hold_key_module, "_send_key", lambda key, key_released = False: sent.append(key)
    )
    monkeypatch.setattr(hold_key_module.Timing, "wait", lambda self, duration: None)
    physics = KeyboardPhysics(
        auto_repeat = True,
        press_delay = 0,
        press_delay_variation = 0,
        press_duration = 0.51,
        press_duration_variation = 0
    )
    _HoldKey("a", physics = physics).execute()
    assert sent == ["a"]

@given(press_delay_variation = strategies.floats(min_value = 0, max_value = 0.5, allow_nan = False))
@settings(deadline = None)
def test_release_key_sends_the_release_with_or_without_delay_variation(
    press_delay_variation, monkeypatch
):
    sent = []
    monkeypatch.setattr(
        release_key_module, "_send_key", lambda key, key_released = False: sent.append(key_released)
    )
    monkeypatch.setattr(release_key_module.Timing, "wait", lambda self, duration: None)
    physics = KeyboardPhysics(press_delay = 0.01, press_delay_variation = press_delay_variation)
    _ReleaseKey("a", physics = physics).execute()
    assert sent == [True]

def test_release_key_rejects_an_invalid_key():
    with pytest.raises(KeyError): _ReleaseKey("not_a_real_key")

def test_press_key_holds_then_releases_normally(monkeypatch):
    calls = []
    monkeypatch.setattr(hold_key_module._HoldKey, "execute", lambda self: calls.append("HOLD"))
    monkeypatch.setattr(
        release_key_module, "_send_key", lambda key, key_released = False: calls.append("UP")
    )
    _PressKey("a").execute()
    assert calls == ["HOLD", "UP"]

def test_press_key_rejects_an_invalid_key():
    with pytest.raises(KeyError): _PressKey("not_a_real_key")

def test_press_key_still_releases_if_the_hold_itself_is_interrupted(monkeypatch):
    calls = []

    class Interrupted(Exception): pass

    def hold_interrupts(self):
        calls.append("HOLD")
        raise Interrupted()

    monkeypatch.setattr(hold_key_module._HoldKey, "execute", hold_interrupts)
    monkeypatch.setattr(
        release_key_module, "_send_key", lambda key, key_released = False: calls.append("UP")
    )
    with pytest.raises(Interrupted): _PressKey("a").execute()
    assert calls == ["HOLD", "UP"]

def test_hotkey_presses_and_releases_every_key_on_a_normal_run(monkeypatch):
    calls = []
    monkeypatch.setattr(
        hold_key_module._HoldKey, "execute", lambda self: calls.append(("HOLD", self.key))
    )
    monkeypatch.setattr(
        release_key_module._ReleaseKey, "execute", lambda self: calls.append(("RELEASE", self.key))
    )
    _Hotkey("ctrl", "shift", "esc").execute()
    assert calls == [
        ("HOLD", "ctrl"),
        ("HOLD", "shift"),
        ("HOLD", "esc"),
        ("RELEASE", "esc"),
        ("RELEASE", "shift"),
        ("RELEASE", "ctrl")
    ]

def test_hotkey_variation_paths(monkeypatch):
    class FakeTiming:
        waits = []

        def wait(self, duration): self.waits.append(duration)

    monkeypatch.setattr(hotkey_module, "_get_virtual_key_code", lambda _: (65, 0))
    monkeypatch.setattr(hotkey_module, "_apply_variation", lambda *_: -1)
    monkeypatch.setattr(hotkey_module, "Timing", FakeTiming)
    held_keys = []
    monkeypatch.setattr(
        hotkey_module,
        "_HoldKey",
        lambda key, physics: SimpleNamespace(execute = lambda: held_keys.append(("hold", key)))
    )
    monkeypatch.setattr(
        hotkey_module,
        "_ReleaseKey",
        lambda key, physics: SimpleNamespace(execute = lambda: held_keys.append(("release", key)))
    )
    hotkey_module._Hotkey(
        "ctrl",
        "a",
        physics = KeyboardPhysics(
            hotkey_delay = 1,
            hotkey_delay_variation = 1,
            press_duration = 1,
            press_duration_variation = 1
        )
    ).execute()
    assert held_keys == [("hold", "ctrl"), ("hold", "a"), ("release", "a"), ("release", "ctrl")]

def test_hotkey_rejects_invalid_key_name_up_front():
    with pytest.raises(KeyError): _Hotkey("ctrl", "not_a_real_key").execute()

def test_hotkey_releases_only_the_keys_it_actually_held_in_reverse_order(monkeypatch):
    calls = []

    class Interrupted(Exception): pass

    def hold_that_interrupts_on_third_key(self):
        calls.append(("HOLD", self.key))
        if self.key == "esc": raise Interrupted()

    monkeypatch.setattr(hold_key_module._HoldKey, "execute", hold_that_interrupts_on_third_key)
    monkeypatch.setattr(
        release_key_module._ReleaseKey, "execute", lambda self: calls.append(("RELEASE", self.key))
    )
    with pytest.raises(Interrupted): _Hotkey("ctrl", "shift", "esc").execute()
    held = [key for action, key in calls if action == "HOLD"]
    released = [key for action, key in calls if action == "RELEASE"]
    assert held == ["ctrl", "shift", "esc"]
    assert released == ["shift", "ctrl"]

@given(
    text = strategies.text(min_size = 0, max_size = 100),
    error_chance = strategies.floats(min_value = 0, max_value = 1, allow_nan = False),
    delayed_chance = strategies.floats(min_value = 0, max_value = 1, allow_nan = False)
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

@example(text = "the quick brown fox jumps over a lazy dog, more than once, on purpose")
@given(text = strategies.text(min_size = 40, max_size = 80))
@settings(deadline = None, max_examples = 15)
def test_write_still_correct_with_near_certain_errors_and_delayed_realization(text, fake_keyboard):
    fake_keyboard.text = ""
    fake_keyboard.cursor = 0
    physics = KeyboardPhysics(
        typing_error_chance = 0.95,
        typing_error_delayed_realization_chance = 0.97,
        press_delay = 0, press_delay_variation = 0,
        typing_error_correction_delay = 0, typing_error_correction_delay_variation = 0
    )
    _write._Write(text, physics = physics).execute()
    assert fake_keyboard.text == text

def test_write_typing_error_and_delay_variation(monkeypatch):
    class FakeTiming:
        waits = []

        def wait(self, duration): self.waits.append(duration)

    writer = write_module._Write(
        "x",
        KeyboardPhysics(
            press_delay = 1,
            press_delay_variation = 1,
            typing_error_correction_delay = 1,
            typing_error_correction_delay_variation = 1
        )
    )
    monkeypatch.setattr(write_module, "_apply_variation", lambda *_: -1)
    monkeypatch.setattr(write_module, "_send_unicode", lambda *_: None)
    monkeypatch.setattr(
        write_module,
        "_PressKey",
        lambda *arguments, **keyword_arguments: SimpleNamespace(execute = lambda: None)
    )
    writer._wait_press_delay(FakeTiming())
    assert writer._simulate_typing_error(0, "x", FakeTiming(), writer.physics, writer.physics) == 1