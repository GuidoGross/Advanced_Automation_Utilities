from advanced_automation_utilities.screen import ScreenInfo, _locate_text
from advanced_automation_utilities.screen._take_screenshot import _TakeScreenshot
from advanced_automation_utilities.screen._locate_image import _LocateImage
from advanced_automation_utilities.screen._read_text import _ReadText
from advanced_automation_utilities.backend.windows._screen import _adjust_coordinates_for_region
import advanced_automation_utilities.screen.screen as screen_module
import advanced_automation_utilities.screen._screen_action as screen_action_module
import advanced_automation_utilities.screen.screen_info as screen_info_module
import advanced_automation_utilities.screen._take_screenshot as _take_screenshot_module
import advanced_automation_utilities.screen._locate_image as _locate_image_module
import advanced_automation_utilities.screen._read_text as _read_text_module
import advanced_automation_utilities.screen._locate_text as locate_text_module
import advanced_automation_utilities.backend.windows._screen as screen_backend_module
from types import SimpleNamespace
from hypothesis import strategies, settings, example, given
import pytest

def test_screen_facade_delegates_to_actions(monkeypatch):
    recorded_calls = []
    for action_attribute, action_name in (
        ("_TakeScreenshot", "screenshot"),
        ("_LocateImage", "image"),
        ("_ReadText", "read"),
        ("_LocateText", "text")
    ):
        monkeypatch.setattr(
            screen_module,
            action_attribute,
            lambda *arguments, action_name = action_name, **keyword_arguments: SimpleNamespace(
                execute = lambda: recorded_calls.append(
                    (action_name, arguments, keyword_arguments)
                ) or action_name
            )
        )
    screen = screen_module.Screen()
    assert screen.take_screenshot() == "screenshot"
    assert screen.locate_image("image.png") == "image"
    assert screen.read_text() == "read"
    assert screen.locate_text("text") == "text"

def test_abstract_screen_action_probe():
    class ScreenActionProbe(screen_action_module._ScreenAction):
        def execute(self): return super().execute()

    assert ScreenActionProbe().execute() is None

def test_screen_info_simple_properties(monkeypatch):
    monkeypatch.setattr(screen_info_module, "_get_screen_resolution", lambda: (1920, 1080))
    monkeypatch.setattr(screen_info_module, "_get_work_area", lambda: (0, 0, 1920, 1040))
    screen_info = ScreenInfo()
    assert screen_info.resolution == (1920, 1080)
    assert screen_info.width == 1920
    assert screen_info.height == 1080
    assert screen_info.work_area == (0, 0, 1920, 1040)

def test_screen_info_returns_positive_resolution():
    width, height = ScreenInfo().resolution
    assert width > 0 and height > 0

def test_screen_info_returns_valid_work_area_bounds():
    left, top, right, bottom = ScreenInfo().work_area
    assert right > left and bottom > top

def test_screen_info_pixel_and_on_screen_methods(monkeypatch):
    class FakeMssCapture:
        def __enter__(self): return self

        def __exit__(self, *args): return False

        monitors = [
            {"left": 0, "top": 0, "width": 50, "height": 50},
            {"left": 100, "top": 200, "width": 50, "height": 50}
        ]

    monkeypatch.setattr(
        screen_info_module, "_get_pixel_color", lambda x_coordinate, y_coordinate: (10, 20, 30)
    )
    monkeypatch.setattr(
        screen_info_module, "mss", SimpleNamespace(MSS = FakeMssCapture)
    )
    info = screen_info_module.ScreenInfo()
    assert info.pixel_color(1, 2, "hexadecimal") == "#0a141e"
    assert info.pixel_matches_color(1, 2, "#0a141e") is True
    assert info.on_screen(100, 200, monitor_index = 1) is True
    assert info.on_screen(150, 250, monitor_index = 1) is False
    assert info.on_screen(110, 220, region = (10, 20, 30, 40), monitor_index = 1) is True
    assert info.on_screen(130, 220, region = (10, 20, 30, 40), monitor_index = 1) is False

@given(
    red = strategies.integers(0, 255),
    green = strategies.integers(0, 255),
    blue = strategies.integers(0, 255)
)
def test_pixel_color_rgb_and_hexadecimal_agree(red, green, blue, monkeypatch):
    monkeypatch.setattr(
        screen_info_module, "_get_pixel_color", lambda x_coordinate, y_coordinate: (red, green, blue)
    )
    screen_info = ScreenInfo()
    assert screen_info.pixel_color(0, 0, format = "rgb") == (red, green, blue)
    assert screen_info.pixel_color(0, 0, format = "hexadecimal") == f"#{red:02x}{green:02x}{blue:02x}"

def test_pixel_color_rejects_a_format_outside_the_declared_literal(monkeypatch):
    monkeypatch.setattr(
        screen_info_module, "_get_pixel_color", lambda x_coordinate, y_coordinate: (0, 0, 0)
    )
    with pytest.raises(ValueError): ScreenInfo().pixel_color(0, 0, format = "hex")

@given(
    actual_color = strategies.tuples(*(strategies.integers(0, 255),) * 3),
    tolerance = strategies.floats(min_value = 0, max_value = 1, allow_nan = False)
)
def test_pixel_matches_color_always_matches_itself(actual_color, tolerance, monkeypatch):
    monkeypatch.setattr(
        screen_info_module, "_get_pixel_color", lambda x_coordinate, y_coordinate: actual_color
    )
    screen_info = ScreenInfo()
    assert screen_info.pixel_matches_color(0, 0, actual_color, tolerance = tolerance) is True

@given(actual_color = strategies.tuples(*(strategies.integers(0, 255),) * 3))
def test_pixel_matches_color_rejects_a_far_color_at_strict_tolerance(actual_color, monkeypatch):
    monkeypatch.setattr(
        screen_info_module, "_get_pixel_color", lambda x_coordinate, y_coordinate: actual_color
    )
    screen_info = ScreenInfo()
    far_color = tuple(channel_value + 200 for channel_value in actual_color)
    assert screen_info.pixel_matches_color(0, 0, far_color, tolerance = 1) is False

def test_multi_monitor_coordinates_account_for_monitor_offset(monkeypatch):
    class FakeMssContext:
        def __enter__(self): return self

        def __exit__(self, *args): pass

        monitors = {
            0: {"left": -1920, "top": 0, "width": 3840, "height": 1080},
            1: {"left": -1920, "top": 0, "width": 1920, "height": 1080}
        }

    monkeypatch.setattr(screen_backend_module.mss, "MSS", lambda: FakeMssContext())
    adjusted_x, adjusted_y = _adjust_coordinates_for_region(100, 50, region = None, monitor_index = 1)
    assert (adjusted_x, adjusted_y) == (100 - 1920, 50)

def test_take_screenshot_accepts_no_save_path(monkeypatch):
    monkeypatch.setattr(
        _take_screenshot_module,
        "_take_screenshot",
        lambda region, monitor_index, save_path: "a-screenshot-object"
    )
    assert _TakeScreenshot().execute() == "a-screenshot-object"

def test_take_screenshot_passes_the_save_path_through(tmp_path, monkeypatch):
    captured_calls = {}
    monkeypatch.setattr(
        _take_screenshot_module,
        "_take_screenshot",
        lambda region, monitor_index, save_path: captured_calls.setdefault("save_path", save_path)
    )
    destination_file_path = str(tmp_path / "screenshot_output.png")
    _TakeScreenshot(save_path = destination_file_path).execute()
    assert captured_calls["save_path"] == destination_file_path

def test_take_screenshot_with_region_delegates_correctly(monkeypatch):
    captured_screenshots = []
    monkeypatch.setattr(
        _take_screenshot_module,
        "_take_screenshot",
        lambda *arguments: captured_screenshots.append(arguments) or "capture"
    )
    assert _take_screenshot_module._TakeScreenshot(region = (0, 0, 1, 1)).execute() == "capture"
    assert captured_screenshots == [((0, 0, 1, 1), 0, None)]

def test_take_screenshot_rejects_a_non_string_save_path():
    with pytest.raises(ValueError): _TakeScreenshot(save_path = 12345)

def test_locate_image_delegates_with_every_argument(tmp_path, monkeypatch):
    dummy_image_path = tmp_path / "dummy_image.png"
    dummy_image_path.write_bytes(b"\x00")
    captured_calls = {}
    monkeypatch.setattr(
        _locate_image_module,
        "_locate_image",
        lambda *arguments: captured_calls.setdefault("arguments", arguments)
    )
    _LocateImage(
        str(dummy_image_path), confidence = 0.8, limit = 3, region = (0, 0, 10, 10), monitor_index = 1
    ).execute()
    assert captured_calls["arguments"] == (str(dummy_image_path), 0.8, 3, (0, 0, 10, 10), 1)

def test_locate_image_rejects_a_missing_file(tmp_path):
    missing_path = tmp_path / "does_not_exist.png"
    with pytest.raises(FileNotFoundError): _LocateImage(str(missing_path))

@given(
    confidence = strategies.one_of(
        strategies.floats(max_value = -0.001), strategies.floats(min_value = 1.001)
    )
)
def test_locate_image_rejects_confidence_outside_zero_one(confidence, tmp_path):
    dummy_image_path = tmp_path / "dummy_image.png"
    dummy_image_path.write_bytes(b"\x00")
    with pytest.raises(ValueError): _LocateImage(str(dummy_image_path), confidence = confidence)

@given(limit = strategies.integers(max_value = -1))
def test_locate_image_rejects_a_negative_limit(limit, tmp_path):
    dummy_image_path = tmp_path / "dummy_image.png"
    dummy_image_path.write_bytes(b"\x00")
    with pytest.raises(ValueError): _LocateImage(str(dummy_image_path), limit = limit)

def test_read_text_returns_the_ocr_result_text(monkeypatch):
    class FakeOcrResult: text = "hello world"
    monkeypatch.setattr(
        _read_text_module, "_run_ocr_on_region", lambda region, monitor_index: FakeOcrResult()
    )
    assert _ReadText().execute() == "hello world"

def test_read_text_rejects_an_invalid_region():
    with pytest.raises(ValueError): _ReadText(region = (10, 10, 5, 5))

@given(text = strategies.text(min_size = 1))
@settings(deadline = None)
def test_locate_text_handles_all_strings(text, fake_screen):
    if not text.strip():
        with pytest.raises(ValueError): _locate_text._LocateText(text, exact_match = False).execute()
    else:
        coordinates = _locate_text._LocateText(text, exact_match = False).execute()
        assert coordinates == (None, None)

def test_locate_text_matches_a_distinct_word_not_a_substring_of_its_neighbor(monkeypatch):
    monkeypatch.setattr(
        locate_text_module,
        "_run_ocr_on_region",
        lambda region, monitor_index: SimpleNamespace(
            lines = [_create_mock_line(("Skip", 0, 140), ("on", 200, 40))]
        )
    )
    coordinates = locate_text_module._LocateText("on", exact_match = False).execute()
    assert coordinates == (220, 20)

def test_locate_text_finds_the_center_of_a_multi_word_phrase(monkeypatch):
    monkeypatch.setattr(
        locate_text_module,
        "_run_ocr_on_region",
        lambda region, monitor_index: SimpleNamespace(
            lines = [_create_mock_line(("Save", 100, 80), ("as", 200, 50))]
        )
    )
    coordinates = locate_text_module._LocateText("Save as", exact_match = False).execute()
    assert coordinates == (175, 20)

def test_locate_text_exact_match_true_positive(monkeypatch):
    monkeypatch.setattr(
        locate_text_module,
        "_run_ocr_on_region",
        lambda region, monitor_index: SimpleNamespace(lines = [_create_mock_line(("Submit", 0, 80))])
    )
    coordinates = locate_text_module._LocateText("Submit", exact_match = True).execute()
    assert coordinates == (40, 20)

def test_locate_text_exact_match_requires_the_whole_line_not_a_substring(monkeypatch):
    monkeypatch.setattr(
        locate_text_module,
        "_run_ocr_on_region",
        lambda region, monitor_index: SimpleNamespace(
            lines = [_create_mock_line(("Submit", 0, 80), ("form", 90, 70), ("now", 170, 60))]
        )
    )
    coordinates = locate_text_module._LocateText("Submit", exact_match = True).execute()
    assert coordinates == (None, None)

def test_locate_text_line_and_word_filtering(monkeypatch):
    bounding_box = SimpleNamespace(x = 2, y = 3, width = 4, height = 5)
    unmatched_line = SimpleNamespace(text = "other", words = [])
    candidate_line_without_word_match = SimpleNamespace(
        text = "contains target",
        words = [SimpleNamespace(text = "other", bounding_rect = bounding_box)]
    )
    matching_line = SimpleNamespace(
        text = "target", words = [SimpleNamespace(text = "target", bounding_rect = bounding_box)]
    )
    monkeypatch.setattr(
        locate_text_module,
        "_run_ocr_on_region",
        lambda *args: SimpleNamespace(
            lines = [unmatched_line, candidate_line_without_word_match, matching_line]
        )
    )
    monkeypatch.setattr(
        locate_text_module, "_adjust_coordinates_for_region", lambda x, y, *args: (x, y)
    )
    assert locate_text_module._LocateText("target").execute() == (4, 5.5)
    exact_mismatch_line = SimpleNamespace(text = "almost", words = [])
    exact_match_line = SimpleNamespace(
        text = "Exact", words = [SimpleNamespace(text = "different", bounding_rect = bounding_box)]
    )
    monkeypatch.setattr(
        locate_text_module,
        "_run_ocr_on_region",
        lambda *args: SimpleNamespace(lines = [exact_mismatch_line, exact_match_line])
    )
    assert locate_text_module._LocateText("Exact", exact_match = True).execute() == (4, 5.5)

@given(text = strategies.just(""))
@example(text = "    ")
def test_locate_text_with_empty_strings(text, fake_screen):
    with pytest.raises(ValueError): _locate_text._LocateText(text, exact_match = False).execute()

def _create_mock_bounding_rect(x_coordinate, width = 60, y_coordinate = 10, height = 20):
    return SimpleNamespace(x = x_coordinate, y = y_coordinate, width = width, height = height)

def _create_mock_word(text, x_coordinate, width = 60):
    return SimpleNamespace(
        text = text, bounding_rect = _create_mock_bounding_rect(x_coordinate, width = width)
    )

def _create_mock_line(*word_definitions):
    normalized_word_definitions = [
        (
            word_definition[0], word_definition[1], word_definition[2]
            if len(word_definition) > 2 else 60
        )
        for word_definition in word_definitions
    ]
    return SimpleNamespace(
        text = " ".join(word_text for word_text, _, _ in normalized_word_definitions),
        words = [
            _create_mock_word(word_text, x_coordinate, width = word_width)
            for word_text, x_coordinate, word_width in normalized_word_definitions
        ]
    )