from advanced_automation_utilities._utilities import (
    _validate_between_range,
    _validate_region,
    _validate_options,
    _validate_file_exists,
    _apply_variation
)
import advanced_automation_utilities
from pathlib import Path
from types import SimpleNamespace
from hypothesis import strategies, given
import types
import sys
import pytest
import math
import re
import os

def test_package_import_guards_cover_unsupported_platform_and_dpi_failure(monkeypatch):
    package_file = Path(advanced_automation_utilities.__file__)
    header_code = "\n".join(package_file.read_text(encoding = "utf-8").splitlines()[:9])
    fake_os_module = types.ModuleType("os")
    fake_os_module.name = "posix"
    monkeypatch.setitem(sys.modules, "os", fake_os_module)
    with pytest.raises(NotImplementedError, match = "only supported on Windows"):
        exec(compile(header_code, str(package_file), "exec"), {})
    fake_os_module.name = "nt"
    fake_ctypes_module = types.ModuleType("ctypes")
    fake_ctypes_module.windll = SimpleNamespace(
        user32 = SimpleNamespace(
            SetProcessDPIAware = lambda: (_ for _ in ()).throw(RuntimeError("no DPI API"))
        )
    )
    monkeypatch.setitem(sys.modules, "ctypes", fake_ctypes_module)
    exec(compile(header_code, str(package_file), "exec"), {})

@given(
    minimum = strategies.floats(allow_nan = False),
    maximum = strategies.floats(allow_nan = False),
    value = strategies.floats(allow_nan = False)
)
def test_validate_between_range_floats(minimum, maximum, value):
    if not (minimum <= value <= maximum):
        with pytest.raises(ValueError): _validate_between_range(minimum, maximum, test_value = value)
    else: _validate_between_range(minimum, maximum, test_value = value)

@given(minimum = strategies.integers(), maximum = strategies.integers(), value = strategies.integers())
def test_validate_between_range_integers(minimum, maximum, value):
    if not (minimum <= value <= maximum):
        with pytest.raises(ValueError): _validate_between_range(minimum, maximum, test_value = value)
    else: _validate_between_range(minimum, maximum, test_value = value)

def test_validate_between_range_ignores_none():
    _validate_between_range(0, 10, optional_argument = None)

@pytest.mark.parametrize(
    "minimum, maximum, value, name, expected_message",
    [
        (0, math.inf, -1, "speed", "cannot be negative"),
        (1, math.inf, 0, "clicks", "greater than or equal to 1"),
        (5, math.inf, 1, "some_value", "greater than or equal to"),
        (0, 1, 2, "confidence", "between 0 and 1")
    ]
)
def test_validate_between_range_error_messages(minimum, maximum, value, name, expected_message):
    with pytest.raises(ValueError, match = expected_message):
        _validate_between_range(minimum, maximum, **{name: value})

@given(
    region = strategies.tuples(
        strategies.integers(), strategies.integers(), strategies.integers(), strategies.integers()
    )
)
def test_validate_region(region):
    left, top, right, bottom = region
    if left >= right or top >= bottom:
        with pytest.raises(ValueError): _validate_region(region)
    else: _validate_region(region)

def test_validate_region_accepts_none(): _validate_region(None)

@given(wrong_length = strategies.lists(strategies.integers(), min_size = 0, max_size = 10))
def test_validate_region_rejects_wrong_length(wrong_length):
    if len(wrong_length) == 4: return
    with pytest.raises(ValueError): _validate_region(tuple(wrong_length))

@given(
    valid_options = strategies.lists(
        strategies.text(min_size = 1), min_size = 1, max_size = 5, unique = True
    ),
    value = strategies.text(min_size = 1)
)
def test_validate_options(valid_options, value):
    if value in valid_options: _validate_options(value, valid_options)
    else:
        with pytest.raises(ValueError): _validate_options(value, valid_options)

def test_validate_options_error_names_the_valid_choices():
    with pytest.raises(ValueError, match = r"left.*right.*middle"):
        _validate_options("diagonal", ["left", "right", "middle"], "mouse button")

def test_validate_file_exists_passes_for_a_real_file(tmp_path):
    real_file = tmp_path / "exists.txt"
    real_file.write_text("content")
    _validate_file_exists(str(real_file))

def test_validate_file_exists_rejects_a_missing_file(tmp_path):
    missing_file = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError): _validate_file_exists(str(missing_file))

@given(name = strategies.text(min_size = 1, max_size = 25).filter(lambda string: string.strip()))
def test_validate_file_exists_error_mentions_the_given_name(name):
    with pytest.raises(FileNotFoundError, match = re.escape(name)):
        _validate_file_exists(os.path.join("does", "not", "exist.txt"), name)

def test_apply_variation_zero_variation(): assert _apply_variation(7, 0) == 7