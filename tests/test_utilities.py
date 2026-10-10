import re
from advanced_automation_utilities._utilities import (
    _validate_between_range, _validate_region, _validate_options, _validate_file_exists
)
from hypothesis import strategies, given
import pytest
import os

@given(minimum = strategies.integers(), maximum = strategies.integers(), value = strategies.integers())
def test_validate_between_range_integers(minimum, maximum, value):
    if not (minimum <= value <= maximum):
        with pytest.raises(ValueError): _validate_between_range(minimum, maximum, test_value = value)
    else: _validate_between_range(minimum, maximum, test_value = value)

@given(
    minimum = strategies.floats(allow_nan = False),
    maximum = strategies.floats(allow_nan = False),
    value = strategies.floats(allow_nan = False)
)
def test_validate_between_range_floats(minimum, maximum, value):
    if not (minimum <= value <= maximum):
        with pytest.raises(ValueError): _validate_between_range(minimum, maximum, test_value = value)
    else: _validate_between_range(minimum, maximum, test_value = value)

def test_validate_between_range_ignores_none(): _validate_between_range(0, 10, optional_argument = None)

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

@given(name = strategies.text(min_size = 1, max_size = 20).filter(lambda string: string.strip()))
def test_validate_file_exists_error_mentions_the_given_name(name):
    with pytest.raises(FileNotFoundError, match = re.escape(name)):
        _validate_file_exists(os.path.join("does", "not", "exist.txt"), name)

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