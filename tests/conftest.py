from advanced_automation_utilities.exceptions import WindowNotFoundError
from advanced_automation_utilities.keyboard._press_key import _PressKey
import advanced_automation_utilities.mouse.mouse_info as _mouse_info_module
import advanced_automation_utilities.mouse._move as _move_module
import advanced_automation_utilities.keyboard._write as _write_module
import advanced_automation_utilities.screen.screen_info as _screen_info_module
import advanced_automation_utilities.screen._locate_image as _locate_image_module
import advanced_automation_utilities.screen._locate_text as _locate_text_module
import advanced_automation_utilities.backend.windows._screen as _screen_backend
import advanced_automation_utilities.sound._play_beep_sound as _play_beep_sound_module
import advanced_automation_utilities.sound._play_system_sound as _play_system_sound_module
import advanced_automation_utilities.sound._play_audio as _play_audio_module
import advanced_automation_utilities.sound._speak as _speak_module
import advanced_automation_utilities.system.system_info as _system_info_module
import advanced_automation_utilities.system._set_clipboard_text as _set_clipboard_text_module
import advanced_automation_utilities.system._focus_window as _focus_window_module
import advanced_automation_utilities.system._resize_window as _resize_window_module
import advanced_automation_utilities.system._move_window as _move_window_module
import advanced_automation_utilities.system._close_window as _close_window_module
import os
from hypothesis import settings, HealthCheck
import pytest

settings.register_profile(
    "development",
    max_examples = 25,
    deadline = None,
    suppress_health_check = [HealthCheck.function_scoped_fixture]
)
settings.register_profile(
    "pre_commit",
    max_examples = 250,
    deadline = None,
    suppress_health_check = [HealthCheck.function_scoped_fixture]
)
settings.register_profile(
    "post_commit",
    max_examples = 1000,
    deadline = None,
    suppress_health_check = [HealthCheck.function_scoped_fixture]
)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "development"))

class FakeMouse:
    def __init__(self, start_x = 960, start_y = 540):
        self.x = start_x
        self.y = start_y

    def set_position(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def get_position(self): return (self.x, self.y)

@pytest.fixture
def fake_mouse(monkeypatch):
    mouse = FakeMouse()
    monkeypatch.setattr(_move_module, "_set_cursor_position", mouse.set_position)
    monkeypatch.setattr(_mouse_info_module, "_get_cursor_position", mouse.get_position)
    return mouse

class FakeKeyboard:
    def __init__(self):
        self.text = ""
        self.cursor = 0

    def send_unicode(self, string):
        self.text = self.text[:self.cursor] + string + self.text[self.cursor:]
        self.cursor += len(string)

@pytest.fixture
def fake_keyboard(monkeypatch):
    keyboard = FakeKeyboard()
    monkeypatch.setattr(_write_module, "_send_unicode", keyboard.send_unicode)

    def mock_execute(self):
        match self.key:
            case "backspace":
                if keyboard.cursor > 0:
                    keyboard.text = keyboard.text[:keyboard.cursor - 1] + keyboard.text[keyboard.cursor:]
                    keyboard.cursor -= 1
            case "left_arrow":
                if keyboard.cursor > 0: keyboard.cursor -= 1
            case "right_arrow":
                if keyboard.cursor < len(keyboard.text): keyboard.cursor += 1
            case _: pass

    monkeypatch.setattr(_PressKey, "execute", mock_execute)
    return keyboard

class FakeScreen:
    def __init__(self):
        self.mock_image_location = None
        self.mock_pixel_color = (255, 255, 255)
        self.virtual_screen = {"left": 0, "top": 0, "width": 1920, "height": 1080}

    def run_ocr_on_region(self, *args, **kwargs):
        class MockResult: lines = []
        return MockResult()

    def locate_image(self, image_path, confidence, limit, region, monitor_index):
        return self.mock_image_location

    def get_pixel_color(self, x, y):
        left, top = self.virtual_screen["left"], self.virtual_screen["top"]
        width, height = self.virtual_screen["width"], self.virtual_screen["height"]
        if not (left <= x <= left + width - 1) or not (top <= y <= top + height - 1):
            raise ValueError("X and Y must be within the bounds of the virtual screen.")
        return self.mock_pixel_color

@pytest.fixture
def fake_screen(monkeypatch):
    screen = FakeScreen()
    monkeypatch.setattr(_locate_text_module, "_run_ocr_on_region", screen.run_ocr_on_region)
    monkeypatch.setattr(_screen_backend, "_take_screenshot", lambda *args, **kwargs: None)
    monkeypatch.setattr(_locate_image_module, "_locate_image", screen.locate_image)
    monkeypatch.setattr(_screen_info_module, "_get_pixel_color", screen.get_pixel_color)
    return screen

@pytest.fixture
def fake_sound(monkeypatch):
    sound = FakeSound()
    monkeypatch.setattr(
        _play_beep_sound_module,
        "_play_beep_sound",
        lambda frequency, duration: sound.beeps.append((frequency, int(duration * 1000)))
    )
    monkeypatch.setattr(_speak_module, "_speak", lambda text: sound.spoken.append(text))
    monkeypatch.setattr(
        _play_system_sound_module,
        "_play_system_sound",
        lambda sound_name: sound.system_sounds.append(sound_name)
    )
    monkeypatch.setattr(
        _play_audio_module,
        "_play_audio",
        lambda audio_path: sound.audio_played.append(audio_path)
    )
    return sound

class FakeSystem:
    def __init__(self):
        self.open_windows = set()
        self.calls = []
        self.clipboard = ""

    def _act(self, action, title):
        matches = [window for window in self.open_windows if window == title]
        if not matches: raise WindowNotFoundError(f'Window with title "{title}" not found.')
        self.calls.append((action, matches[0]))

@pytest.fixture
def fake_system(monkeypatch):
    system = FakeSystem()
    monkeypatch.setattr(
        _focus_window_module, "_focus_window", lambda title: system._act("focus", title)
    )
    monkeypatch.setattr(
        _close_window_module, "_close_window", lambda title: system._act("close", title)
    )
    monkeypatch.setattr(
        _move_window_module, "_move_window", lambda title, x, y: system._act("move", title)
    )
    monkeypatch.setattr(
        _resize_window_module,
        "_resize_window",
        lambda title, width, height: system._act("resize", title)
    )
    monkeypatch.setattr(
        _set_clipboard_text_module,"_set_clipboard_text",
        lambda text: setattr(system, "clipboard", text)
    )
    monkeypatch.setattr(_system_info_module, "_get_clipboard_text", lambda: system.clipboard)
    return system

class FakeSound:
    def __init__(self):
        self.beeps = []
        self.spoken = []
        self.system_sounds = []
        self.audio_played = []