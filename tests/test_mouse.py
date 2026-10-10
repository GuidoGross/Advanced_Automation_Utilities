from advanced_automation_utilities.mouse import Mouse, MousePhysics, _move, _wander
from advanced_automation_utilities.mouse._move import _Move
from advanced_automation_utilities.mouse._click import _Click
from advanced_automation_utilities.mouse._drag_and_drop import _DragAndDrop
from advanced_automation_utilities.mouse._scroll_until import _ScrollUntil
from advanced_automation_utilities.mouse._wander_until import _WanderUntil
import advanced_automation_utilities.mouse._hold_click as hold_module
import advanced_automation_utilities.mouse._release_click as release_module
import advanced_automation_utilities.mouse._scroll as scroll_module
from hypothesis import strategies, settings, given
from dataclasses import FrozenInstanceError
import math
import pytest
import time

def test_mouse_physics_is_immutable():
    physics = MousePhysics(speed = 500)
    with pytest.raises(FrozenInstanceError): physics.speed = 1

@given(
    start_x = strategies.integers(0, 1920),
    start_y = strategies.integers(0, 1080),
    target_x = strategies.integers(0, 1920),
    target_y = strategies.integers(0, 1080),
    target_radius = strategies.integers(0, 250)
)
@settings(deadline = None)
def test_move_arrives_within_target_radius(
    start_x, start_y, target_x, target_y, target_radius, fake_mouse
):
    fake_mouse.set_position(start_x, start_y)
    physics = MousePhysics(target_radius = target_radius)
    _move._Move(target_x, target_y, physics = physics).execute()
    final_x, final_y = fake_mouse.get_position()
    distance = math.hypot(final_x - target_x, final_y - target_y)
    assert int(distance) <= target_radius

@given(clicks = strategies.integers(min_value = -10, max_value = -1))
def test_click_rejects_a_negative_click_count(clicks):
    with pytest.raises(ValueError):
        _Click(0, 0, button = "left", clicks = clicks, physics = MousePhysics())

def test_zero_clicks_do_nothing(monkeypatch):
    def fail_if_called(self):
        pytest.fail("A zero-click action should not perform any mouse operations.")

    monkeypatch.setattr(_Click, "_move_if_needed", fail_if_called)
    monkeypatch.setattr(hold_module._HoldClick, "execute", fail_if_called)
    monkeypatch.setattr(release_module._ReleaseClick, "execute", fail_if_called)
    _Click(0, 0, button = "left", clicks = 0, physics = MousePhysics()).execute()

def test_click_always_releases_even_if_interrupted_mid_sequence(monkeypatch):
    calls = []

    class Interrupted(Exception): pass

    def down_then_interrupt(button):
        calls.append(("DOWN", button))
        raise Interrupted()

    monkeypatch.setattr(hold_module, "_mouse_down", down_then_interrupt)
    monkeypatch.setattr(release_module, "_mouse_up", lambda button: calls.append(("UP", button)))
    with pytest.raises(Interrupted):
        _Click(button = "left", clicks = 1, physics = MousePhysics()).execute()
    assert ("UP", "left") in calls, "the button was left held down after the interruption"

def test_drag_and_drop_always_releases_even_if_interrupted_mid_drag(monkeypatch):
    calls = []

    class Interrupted(Exception): pass

    def move_that_interrupts(self):
        calls.append("MOVE")
        if calls.count("MOVE") == 3: raise Interrupted()

    monkeypatch.setattr(hold_module, "_mouse_down", lambda button: calls.append(("DOWN", button)))
    monkeypatch.setattr(release_module, "_mouse_up", lambda button: calls.append(("UP", button)))
    monkeypatch.setattr(_Move, "execute", move_that_interrupts)
    with pytest.raises(Interrupted):
        _DragAndDrop(0, 0, 500, 500, button = "left", physics = MousePhysics()).execute()
    assert ("UP", "left") in calls, "the button was left held down mid-drag"

def test_scroll_until_result_is_retrievable_through_the_facade(monkeypatch):
    monkeypatch.setattr(scroll_module, "_scroll", lambda amount, direction: None)
    mouse = Mouse()
    returned = mouse.scroll_until(condition_function = lambda: True, timeout = 1, poll_interval = 0.01)
    assert returned is mouse
    assert mouse.last_result is True

def test_asynchronous_scroll_until_result_is_on_the_task(monkeypatch):
    monkeypatch.setattr(scroll_module, "_scroll", lambda amount, direction: None)
    mouse = Mouse()
    with mouse.asynchronous() as task:
        mouse.scroll_until(condition_function = lambda: True, timeout = 1, poll_interval = 0.01)
    task.wait()
    assert task.last_result is True

def test_scroll_until_stops_its_background_thread_if_interrupted(monkeypatch):
    scroll_calls = []
    monkeypatch.setattr(scroll_module, "_scroll", lambda amount, direction: scroll_calls.append(1))

    class Interrupted(Exception): pass

    def flaky_condition():
        if len(scroll_calls) > 3: raise Interrupted()
        return False

    action = _ScrollUntil(
        condition_function = flaky_condition, amount = 0, direction = "down",
        timeout = 0, poll_interval = 0.01, physics = MousePhysics(scroll_step = 1)
    )
    with pytest.raises(Interrupted): action.execute()
    calls_right_after = len(scroll_calls)
    time.sleep(0.3)
    assert len(scroll_calls) == calls_right_after, (
        "the scroll thread kept running in the background after execute() raised"
    )

@given(
    start_x = strategies.integers(500, 1500),
    start_y = strategies.integers(500, 1000),
    region = strategies.tuples(
        strategies.just(100), strategies.just(100), strategies.just(1900), strategies.just(1000)
    )
)
@settings(deadline = None)
def test_wander_stays_within_bounds(start_x, start_y, region, fake_mouse, monkeypatch):
    fake_mouse.set_position(start_x, start_y)

    def mock_move_execute(self):
        fake_mouse.set_position(self.x, self.y)
        assert region[0] <= self.x <= region[2]
        assert region[1] <= self.y <= region[3]

    monkeypatch.setattr(_Move, "execute", mock_move_execute)
    _wander._Wander(duration = 1, region = region).execute()

def test_wander_until_stops_its_background_thread_if_interrupted(monkeypatch, fake_mouse):
    move_calls = []
    monkeypatch.setattr(_Move, "execute", lambda self: move_calls.append(1))

    class Interrupted(Exception): pass

    def flaky_condition():
        if len(move_calls) > 3: raise Interrupted()
        return False

    action = _WanderUntil(
        condition_function = flaky_condition, region = (0, 0, 1920, 1080),
        timeout = 0, poll_interval = 0.01, physics = MousePhysics(speed = 2000)
    )
    with pytest.raises(Interrupted):
        action.execute()

    calls_right_after = len(move_calls)
    time.sleep(0.3)
    assert len(move_calls) == calls_right_after, (
        "the wander thread kept moving the mouse in the background after execute() raised"
    )