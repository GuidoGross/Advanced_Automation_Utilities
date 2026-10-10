from advanced_automation_utilities.screen import ScreenInfo, _locate_text
from advanced_automation_utilities.screen._locate_image import _LocateImage
from advanced_automation_utilities.backend.windows._screen import _adjust_coordinates_for_region
import advanced_automation_utilities.backend.windows._screen as screen_backend
import advanced_automation_utilities.screen.screen_info as screen_info_module
from hypothesis import strategies, settings, example, given
import pytest

def test_multi_monitor_coordinates_account_for_monitor_offset(monkeypatch):
    class FakeMssContext:
        monitors = {
            0: {"left": -1920, "top": 0, "width": 3840, "height": 1080},
            1: {"left": -1920, "top": 0, "width": 1920, "height": 1080},
        }

        def __enter__(self): return self

        def __exit__(self, *args): pass

    monkeypatch.setattr(screen_backend.mss, "mss", lambda: FakeMssContext())
    x, y = _adjust_coordinates_for_region(100, 50, region = None, monitor_index = 1)
    assert (x, y) == (100 - 1920, 50)

def test_locate_image_rejects_a_missing_file(tmp_path):
    missing_path = tmp_path / "does_not_exist.png"
    with pytest.raises(FileNotFoundError): _LocateImage(str(missing_path))

@given(text = strategies.text(min_size = 1))
@settings(deadline = None)
def test_locate_text_handles_all_strings(text, fake_screen):
    if not text.strip():
        with pytest.raises(ValueError): _locate_text._LocateText(text, exact_match = False).execute()
    else:
        result = _locate_text._LocateText(text, exact_match = False).execute()
        assert result == (None, None)

@given(text = strategies.just(""))
@example(text = "    ")
def test_locate_text_with_empty_strings(text, fake_screen):
    with pytest.raises(ValueError): _locate_text._LocateText(text, exact_match = False).execute()

@given(
    red = strategies.integers(0, 255),
    green = strategies.integers(0, 255),
    blue = strategies.integers(0, 255)
)
def test_pixel_color_rgb_and_hexadecimal_agree(red, green, blue, monkeypatch):
    monkeypatch.setattr(screen_info_module, "_get_pixel_color", lambda x, y: (red, green, blue))
    screen_info = ScreenInfo()
    assert screen_info.pixel_color(0, 0, format = "rgb") == (red, green, blue)
    assert screen_info.pixel_color(0, 0, format = "hexadecimal") == f"#{red:02x}{green:02x}{blue:02x}"

def test_pixel_color_rejects_a_format_outside_the_declared_literal(monkeypatch):
    monkeypatch.setattr(screen_info_module, "_get_pixel_color", lambda x, y: (0, 0, 0))
    with pytest.raises(ValueError): ScreenInfo().pixel_color(0, 0, format = "hex")

@given(
    actual = strategies.tuples(*(strategies.integers(0, 255),) * 3),
    tolerance = strategies.floats(min_value = 0, max_value = 1, allow_nan = False)
)
def test_pixel_matches_color_always_matches_itself(actual, tolerance, monkeypatch):
    monkeypatch.setattr(screen_info_module, "_get_pixel_color", lambda x, y: actual)
    screen_info = ScreenInfo()
    assert screen_info.pixel_matches_color(0, 0, actual, tolerance = tolerance) is True

@given(actual = strategies.tuples(*(strategies.integers(0, 55),) * 3))
def test_pixel_matches_color_rejects_a_far_color_at_strict_tolerance(actual, monkeypatch):
    monkeypatch.setattr(screen_info_module, "_get_pixel_color", lambda x, y: actual)
    screen_info = ScreenInfo()
    far_color = tuple(channel + 200 for channel in actual)
    assert screen_info.pixel_matches_color(0, 0, far_color, tolerance = 1) is False
