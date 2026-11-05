from advanced_automation_utilities.mouse import Mouse, MouseInfo, MousePhysics, _move, _wander
from advanced_automation_utilities.mouse._move import _Move
from advanced_automation_utilities.mouse._click import _Click
from advanced_automation_utilities.mouse._drag_and_drop import _DragAndDrop
from advanced_automation_utilities.mouse._scroll import _Scroll
from advanced_automation_utilities.mouse._scroll_until import _ScrollUntil
from advanced_automation_utilities.mouse._wander_until import _WanderUntil
from advanced_automation_utilities._kill_switch_event import KILL_SWITCH_EVENT
import advanced_automation_utilities.mouse.mouse as mouse_module
import advanced_automation_utilities.mouse._mouse_action as mouse_action_module
import advanced_automation_utilities.mouse.mouse_info as mouse_info_module
import advanced_automation_utilities.mouse._move as move_module
import advanced_automation_utilities.mouse._hold_click as hold_click_module
import advanced_automation_utilities.mouse._release_click as release_click_module
import advanced_automation_utilities.mouse._base_click as base_click_module
import advanced_automation_utilities.mouse._click as click_module
import advanced_automation_utilities.mouse._drag_and_drop as drag_module
import advanced_automation_utilities.mouse._scroll as scroll_module
import advanced_automation_utilities.mouse._scroll_until as scroll_until_module
import advanced_automation_utilities.mouse._wander as wander_module
import advanced_automation_utilities.mouse._wander_until as wander_until_module
from hypothesis import strategies, settings, given
from types import SimpleNamespace
from dataclasses import FrozenInstanceError
import time
import pytest
import math
import itertools
import threading

class FakeTiming:
    waits = []

    def wait(self, duration): self.waits.append(duration)

class FakeClock:
    def __init__(self, time_values):
        self._values = iter(time_values)
        self._last_value = 0

    @property
    def time(self):
        self._last_value = next(self._values, self._last_value)
        return self._last_value

def test_mouse_facade_and_info_delegation(monkeypatch):
    recorded_calls = []
    for action_attribute, action_name in (
        ("_Move", "move"),
        ("_DragAndDrop", "drag"),
        ("_Scroll", "scroll"),
        ("_Wander", "wander"),
        ("_WanderUntil", "wander-until")
    ):
        monkeypatch.setattr(
            mouse_module,
            action_attribute,
            lambda *arguments, action_name = action_name, **keyword_arguments: SimpleNamespace(
                execute = lambda: recorded_calls.append(
                    (action_name, arguments, keyword_arguments)
                ) or action_name
            )
        )
    mouse = mouse_module.Mouse()
    mouse.move(1, 2)
    mouse.drag_and_drop(1, 2, 3, 4)
    mouse.scroll(5, "up")
    mouse.wander(0)
    mouse.wander_until(lambda: True)
    assert [name for name, _, _ in recorded_calls] == [
        "move", "drag", "scroll", "wander", "wander-until"
    ]
    info_calls = {}

    class FakeScreenInfo:
        def pixel_color(self, x_coordinate, y_coordinate, format):
            return (x_coordinate, y_coordinate, format)

        def pixel_matches_color(self, **keyword_arguments):
            info_calls["pixel_matches_color"] = keyword_arguments
            return True

        def on_screen(self, *arguments, **keyword_arguments):
            info_calls["on_screen"] = (arguments, keyword_arguments)
            return True

    monkeypatch.setattr(mouse_info_module, "_get_cursor_position", lambda: (4, 5))
    monkeypatch.setattr(mouse_info_module, "ScreenInfo", FakeScreenInfo)
    info = mouse_info_module.MouseInfo()
    assert info.coordinates == (4, 5)
    assert info.x == 4 and info.y == 5
    assert info.pixel_color("hexadecimal") == (4, 5, "hexadecimal")
    assert info.pixel_matches_color("#040506") is True
    assert info_calls["pixel_matches_color"] == {
        "x": 4, "y": 5, "expected_color": "#040506", "tolerance": 1
    }
    assert info.on_screen(region = (0, 0, 10, 10)) is True
    assert info_calls["on_screen"] == ((4, 5), {"region": (0, 0, 10, 10), "monitor_index": 0})

def test_mouse_info_returns_integer_pointer_coordinates():
    x, y = MouseInfo().coordinates
    assert isinstance(x, int) and isinstance(y, int)

def test_abstract_mouse_action_probe():
    class MouseActionProbe(mouse_action_module._MouseAction):
        def execute(self): return super().execute()

    assert MouseActionProbe().physics is not None
    assert MouseActionProbe(mouse_module.MousePhysics()).physics is not None
    assert MouseActionProbe().execute() is None

def test_mouse_physics_is_immutable():
    physics = MousePhysics(speed = 500)
    with pytest.raises(FrozenInstanceError): setattr(physics, "speed", 1)

@given(
    start_x = strategies.integers(0, 1920),
    start_y = strategies.integers(0, 1080),
    target_x = strategies.integers(0, 1920),
    target_y = strategies.integers(0, 1080),
    target_radius = strategies.integers(0, 250),
    speed = strategies.floats(min_value = 50, max_value = 4000, allow_nan = False),
    inconsistency = strategies.floats(min_value = 0, max_value = 1, allow_nan = False),
    readjustment_duration_ratio = strategies.floats(min_value = 0, max_value = 0.9, allow_nan = False)
)
@settings(deadline = None)
def test_move_arrives_within_target_radius(
    start_x,
    start_y,
    target_x,
    target_y,
    target_radius,
    speed,
    inconsistency,
    readjustment_duration_ratio,
    fake_mouse
):
    fake_mouse.set_position(start_x, start_y)
    physics = MousePhysics(
        target_radius = target_radius,
        speed = speed,
        inconsistency = inconsistency,
        readjustment_duration_ratio = readjustment_duration_ratio
    )
    _move._Move(target_x, target_y, physics = physics).execute()
    final_x, final_y = fake_mouse.get_position()
    distance = math.hypot(final_x - target_x, final_y - target_y)
    assert int(distance) <= target_radius

def test_inconsistent_move_reaches_target_without_readjustment_time(fake_mouse):
    fake_mouse.set_position(0, 0)
    physics = MousePhysics(
        speed = 50,
        inconsistency = 1,
        target_radius = 0,
        readjustment_duration_ratio = 0
    )
    _Move(0, 1, physics = physics).execute()
    assert fake_mouse.get_position() == (0, 1)

def test_move_helper_paths_and_time_limited_phase_execution(fake_mouse, monkeypatch):
    monkeypatch.setattr(move_module, "_apply_variation", lambda value, variation: value / 2)
    speed_move = move_module._Move(
        10,
        10,
        MousePhysics(
            speed = 100,
            speed_variation = 0.5,
            base_duration = 2,
            base_duration_variation = 0.5,
            inconsistency = 1
        )
    )
    assert speed_move._calculate_speed_and_duration(10) == (50, pytest.approx(1.2))
    duration_move = move_module._Move(10, 10, MousePhysics(duration = 2, duration_variation = 0.5))
    assert duration_move._calculate_speed_and_duration(10) == (0, 1)
    monkeypatch.setattr(move_module.random, "random", lambda: 0.9)
    monkeypatch.setattr(move_module.random, "gauss", lambda mean, standard_deviation: mean)
    assert speed_move._calculate_overshoot(0, 0, 100)[0:2] != (speed_move.x, speed_move.y)
    monkeypatch.setattr(move_module.random, "random", lambda: 0.1)
    assert speed_move._calculate_overshoot(0, 0, 100)[0:2] != (speed_move.x, speed_move.y)
    assert len(speed_move._calculate_phase_times(3, 1)) == 3
    assert len(speed_move._calculate_error_fractions(3)) == 3
    assert speed_move._calculate_phase_times(4, 1) is None
    assert speed_move._calculate_error_fractions(4) is None
    zero_duration_move = move_module._Move(1, 1, MousePhysics())
    zero_duration_move._execute_movement_phase(0, 0, 1, 1, 0, 1)
    zero_duration_move._execute_movement_phase(0, 0, 1, 1, 1e-7, 1)
    moved_positions = []
    phase_move = move_module._Move(1, 1, MousePhysics(minimum_speed = 1, maximum_speed = 10))
    monkeypatch.setattr(
        phase_move,
        "_generate_human_path",
        lambda x1, y1, x2, y2, steps, speed: [(1000, 0)] * steps
    )
    monkeypatch.setattr(
        move_module, "_set_cursor_position", lambda x, y: moved_positions.append((x, y))
    )
    monkeypatch.setattr(move_module.random, "uniform", lambda *args: 0)
    monkeypatch.setattr(move_module.random, "random", lambda: 1)
    counter = itertools.count(0, 100)
    monkeypatch.setattr(move_module.time, "perf_counter", lambda: next(counter))
    phase_move._execute_movement_phase(0, 0, 1, 1, 0.1, 100)
    assert moved_positions
    executed_phases = []
    monkeypatch.setattr(move_module, "MouseInfo", lambda: SimpleNamespace(coordinates = (0, 0)))
    monkeypatch.setattr(
        speed_move, "_execute_movement_phase", lambda *arguments: executed_phases.append(arguments)
    )
    monkeypatch.setattr(
        move_module.random, "uniform", lambda minimum, maximum: (minimum + maximum) / 2
    )
    counter = itertools.count(0, 100)
    monkeypatch.setattr(move_module.time, "perf_counter", lambda: next(counter))
    speed_move._execute_readjustment_phases(1, 1, 1500, 1, 100, 100)
    speed_move._execute_readjustment_phases(1, 1, 3000, 0.01, 100, 100)
    assert executed_phases
    target_radius_move = move_module._Move(1, 1, MousePhysics(target_radius = 1))
    monkeypatch.setattr(target_radius_move, "_execute_movement_phase", lambda *args: None)
    target_radius_move._execute_readjustment_phases(1, 1, 100, 1, 0, 0)
    nonmatching_radius_move = move_module._Move(1, 1, MousePhysics(target_radius = 1))
    monkeypatch.setattr(nonmatching_radius_move, "_execute_movement_phase", lambda *args: None)
    monkeypatch.setattr(move_module, "MouseInfo", lambda: SimpleNamespace(coordinates = (100, 100)))
    counter = itertools.count(0, 100)
    monkeypatch.setattr(move_module.time, "perf_counter", lambda: next(counter))
    nonmatching_radius_move._execute_readjustment_phases(1, 1, 1500, 1, 0, 0)
    unpatched_path_move = move_module._Move(1, 1, MousePhysics())
    assert unpatched_path_move._generate_human_path(1, 1, 1, 1, 3, 10) == [(1, 1)] * 3
    no_tremor_move = move_module._Move(1, 1, MousePhysics(inconsistency = 0))
    assert no_tremor_move._calculate_tremor(0, 0, 1, 1, 1) == (0, 0)
    tremor_move = move_module._Move(1, 1, MousePhysics(inconsistency = 1))
    angles = iter([0, 100, 30, 30])
    monkeypatch.setattr(move_module.random, "uniform", lambda *args: 1)
    monkeypatch.setattr(move_module.random, "gauss", lambda *args: next(angles))
    assert tremor_move._calculate_tremor(0, 0, 1, 0, 1) != (0, 0)
    assert tremor_move._calculate_tremor(0, 0, 0, 0, 1) == (0, 0)

def test_move_reaches_the_defensive_nan_readjustment_branch(fake_mouse, monkeypatch):
    physics = SimpleNamespace(
        target_radius = 0,
        speed = 10,
        duration = 1,
        speed_variation = 0,
        base_duration = 0,
        base_duration_variation = 0,
        duration_variation = 0,
        inconsistency = 1,
        readjustment_duration_ratio = float("nan")
    )
    action = move_module._Move(10, 0, physics)
    monkeypatch.setattr(move_module, "MouseInfo", lambda: SimpleNamespace(coordinates = (0, 0)))
    monkeypatch.setattr(action, "_execute_movement_phase", lambda *args: None)
    action.execute()

@pytest.mark.parametrize("signal_name", ["stop_event", "kill_switch"])
def test_move_stops_during_wait_when_cancelled(signal_name, monkeypatch):
    KILL_SWITCH_EVENT.clear()
    stop_event = threading.Event()
    moved_positions = []
    wait_durations = []
    move_action = move_module._Move(100, 100, MousePhysics())
    monkeypatch.setattr(move_module, "MouseInfo", lambda: SimpleNamespace(coordinates = (0, 0)))
    monkeypatch.setattr(
        move_action,
        "_generate_human_path",
        lambda x1, y1, x2, y2, steps, speed: [(step, 0) for step in range(steps)]
    )
    monkeypatch.setattr(
        move_module, "_set_cursor_position", lambda x, y: moved_positions.append((x, y))
    )
    monkeypatch.setattr(move_module.time, "perf_counter", lambda: 0)

    def activate_cancellation(timing, duration):
        wait_durations.append(duration)
        stop_event.set() if signal_name == "stop_event" else KILL_SWITCH_EVENT.set()

    monkeypatch.setattr(move_module.Timing, "wait", activate_cancellation)
    try: move_action._execute_movement_phase(0, 0, 10, 10, 0.1, 100, stop_event)
    finally: KILL_SWITCH_EVENT.clear()
    assert len(wait_durations) == 1
    assert len(moved_positions) == 1

    stop_event.clear()
    moved_phases = []
    monkeypatch.setattr(move_action, "_execute_movement_phase", lambda *args: moved_phases.append(args))
    wait_durations.clear()
    monkeypatch.setattr(
        move_module.Timing, "wait", lambda timing, duration: activate_cancellation(timing, duration)
    )
    try: move_action._execute_readjustment_phases(1, 1, 1500, 1, 100, 100, stop_event)
    finally: KILL_SWITCH_EVENT.clear()
    assert len(wait_durations) == 1
    assert len(moved_phases) == 1

def test_click_performs_every_hold_and_release_for_a_multi_click(monkeypatch, fake_mouse):
    calls = []
    fake_mouse.set_position(0, 0)
    monkeypatch.setattr(hold_click_module, "_mouse_down", lambda button: calls.append(("DOWN", button)))
    monkeypatch.setattr(release_click_module, "_mouse_up", lambda button: calls.append(("UP", button)))
    _Click(0, 0, button = "right", clicks = 3, physics = MousePhysics()).execute()
    assert calls == [("DOWN", "right"), ("UP", "right")] * 3

@pytest.mark.parametrize(
    "action_callback, button, expected_clicks",
    [
        (lambda mouse: mouse.double_click(0, 0), "left", 2),
        (lambda mouse: mouse.right_click(0, 0), "right", 1),
        (lambda mouse: mouse.middle_click(0, 0), "middle", 1)
    ]
)
def test_click_variant_facades_use_the_right_button_and_click_count(
    action_callback, button, expected_clicks, monkeypatch, fake_mouse
):
    down_calls = []
    monkeypatch.setattr(
        hold_click_module, "_mouse_down", lambda button_name: down_calls.append(button_name)
    )
    monkeypatch.setattr(release_click_module, "_mouse_up", lambda button_name: None)
    action_callback(Mouse())
    assert down_calls == [button] * expected_clicks

def test_hold_click_then_release_click_facades(monkeypatch, fake_mouse):
    recorded_calls = []
    monkeypatch.setattr(
        hold_click_module, "_mouse_down", lambda button: recorded_calls.append(("DOWN", button))
    )
    monkeypatch.setattr(
        release_click_module, "_mouse_up", lambda button: recorded_calls.append(("UP", button))
    )
    mouse = Mouse()
    mouse.hold_click(0, 0, button = "left")
    mouse.release_click(button = "left")
    assert recorded_calls == [("DOWN", "left"), ("UP", "left")]

@given(clicks = strategies.integers(min_value = -10, max_value = -1))
def test_click_rejects_a_negative_click_count(clicks):
    with pytest.raises(ValueError):
        _Click(0, 0, button = "left", clicks = clicks, physics = MousePhysics())

def test_zero_clicks_do_nothing(monkeypatch):
    def fail_if_called(self):
        pytest.fail("A zero-click action should not perform any mouse operations.")

    monkeypatch.setattr(_Click, "_move_if_needed", fail_if_called)
    monkeypatch.setattr(hold_click_module._HoldClick, "execute", fail_if_called)
    monkeypatch.setattr(release_click_module._ReleaseClick, "execute", fail_if_called)
    _Click(0, 0, button = "left", clicks = 0, physics = MousePhysics()).execute()

def test_click_always_releases_even_if_interrupted_mid_sequence(monkeypatch):
    calls = []

    class Interrupted(Exception): pass

    def down_then_interrupt(button):
        calls.append(("DOWN", button))
        raise Interrupted()

    monkeypatch.setattr(hold_click_module, "_mouse_down", down_then_interrupt)
    monkeypatch.setattr(release_click_module, "_mouse_up", lambda button: calls.append(("UP", button)))
    with pytest.raises(Interrupted):
        _Click(button = "left", clicks = 1, physics = MousePhysics()).execute()
    assert ("UP", "left") in calls

def test_drag_and_drop_always_releases_even_if_interrupted_mid_drag(monkeypatch):
    calls = []

    class Interrupted(Exception): pass

    def move_that_interrupts(self):
        calls.append("MOVE")
        if calls.count("MOVE") == 3: raise Interrupted()

    monkeypatch.setattr(
        hold_click_module, "_mouse_down", lambda button: calls.append(("DOWN", button))
    )
    monkeypatch.setattr(release_click_module, "_mouse_up", lambda button: calls.append(("UP", button)))
    monkeypatch.setattr(_Move, "execute", move_that_interrupts)
    with pytest.raises(Interrupted):
        _DragAndDrop(0, 0, 500, 500, button = "left", physics = MousePhysics()).execute()
    assert ("UP", "left") in calls

def test_click_drag_and_scroll_variation_paths(monkeypatch):
    events = []
    monkeypatch.setattr(
        base_click_module,
        "_Move",
        lambda *arguments, **keyword_arguments: _create_mock_action(
            lambda: events.append(("move", arguments, keyword_arguments))
        )
    )
    monkeypatch.setattr(base_click_module, "Timing", FakeTiming)
    monkeypatch.setattr(base_click_module, "_apply_variation", lambda *args: -1)

    class ConcreteBaseClick(base_click_module._BaseClick):
        def execute(self): pass

    ConcreteBaseClick(
        1, 2, physics = MousePhysics(click_delay = 1, click_delay_variation = 1)
    )._move_if_needed()
    assert events[0][0] == "move"
    assert FakeTiming.waits[-1] == 0
    clicks = []
    monkeypatch.setattr(click_module, "Timing", FakeTiming)
    monkeypatch.setattr(click_module, "_apply_variation", lambda *args: -1)
    monkeypatch.setattr(
        click_module,
        "_HoldClick",
        lambda *arguments, **keyword_arguments: _create_mock_action(
            lambda: clicks.append(("hold", arguments, keyword_arguments))
        )
    )
    monkeypatch.setattr(
        click_module,
        "_ReleaseClick",
        lambda *arguments, **keyword_arguments: _create_mock_action(
            lambda: clicks.append(("release", arguments, keyword_arguments))
        )
    )
    click_module._Click(
        clicks = 2, physics = MousePhysics(click_duration = 1, click_duration_variation = 1)
    ).execute()
    assert [event[0] for event in clicks] == ["hold", "release", "hold", "release"]
    assert FakeTiming.waits[-1] == 0
    holds = []
    monkeypatch.setattr(hold_click_module, "Timing", FakeTiming)
    monkeypatch.setattr(hold_click_module, "_apply_variation", lambda *args: -1)
    monkeypatch.setattr(hold_click_module, "_mouse_down", lambda button: holds.append(button))
    hold_click_module._HoldClick(
        physics = MousePhysics(click_duration = 1, click_duration_variation = 1)
    ).execute()
    assert holds == ["left"]
    assert FakeTiming.waits[-1] == 0
    drag_events = []
    monkeypatch.setattr(drag_module, "Timing", FakeTiming)
    monkeypatch.setattr(
        drag_module,
        "_Move",
        lambda *arguments, **keyword_arguments: _create_mock_action(
            lambda: drag_events.append(("move", arguments, keyword_arguments))
        )
    )
    monkeypatch.setattr(
        drag_module,
        "_HoldClick",
        lambda *arguments, **keyword_arguments: _create_mock_action(
            lambda: drag_events.append(("hold", arguments, keyword_arguments))
        )
    )
    monkeypatch.setattr(
        drag_module,
        "_ReleaseClick",
        lambda *arguments, **keyword_arguments: _create_mock_action(
            lambda: drag_events.append(("release", arguments, keyword_arguments))
        )
    )
    drag_module._DragAndDrop(1, 2, 3, 4).execute()
    assert [event[0] for event in drag_events] == ["move", "hold", "move", "release"]
    scroll_events = []
    monkeypatch.setattr(scroll_module, "Timing", FakeTiming)
    monkeypatch.setattr(
        scroll_module, "_scroll", lambda amount, direction: scroll_events.append((amount, direction))
    )
    monkeypatch.setattr(scroll_module, "_apply_variation", lambda value, variation: value)
    scroll_module._Scroll(
        2,
        physics = MousePhysics(
            scroll_duration = 1,
            scroll_duration_variation = 1,
            scroll_pause_variation = 1
        )
    ).execute()
    scroll_module._Scroll(
        2,
        physics = MousePhysics(
            scroll_speed = 2,
            scroll_speed_variation = 1,
            scroll_pause_variation = 1
        )
    ).execute()
    assert scroll_events == [(1, "down"), (1, "down"), (1, "down"), (1, "down")]

@given(amount = strategies.integers(min_value = 1, max_value = 500))
def test_scroll_instant_path_sends_the_whole_amount_in_one_call(amount, monkeypatch):
    calls = []
    monkeypatch.setattr(scroll_module, "_scroll", lambda amount, direction: calls.append(amount))
    _Scroll(amount = amount, direction = "down", physics = MousePhysics()).execute()
    assert calls == [amount]

@given(
    amount = strategies.integers(min_value = 10, max_value = 200),
    step = strategies.integers(min_value = 1, max_value = 20),
    use_duration = strategies.booleans()
)
@settings(deadline = None)
def test_scroll_animated_path_sends_the_full_amount_across_several_calls(
    amount, step, use_duration, monkeypatch
):
    calls = []
    monkeypatch.setattr(scroll_module, "_scroll", lambda amount, direction: calls.append(amount))
    monkeypatch.setattr(scroll_module.Timing, "wait", lambda self, duration: None)
    physics = MousePhysics(
        scroll_step = step,
        scroll_duration = 1 if use_duration else 0,
        scroll_speed = 0 if use_duration else 50
    )
    _Scroll(amount = amount, direction = "up", physics = physics).execute()
    assert sum(calls) == amount
    assert all(call <= step for call in calls)

def test_scroll_zero_amount_never_calls_the_backend(monkeypatch):
    monkeypatch.setattr(
        scroll_module, "_scroll", lambda *a, **k: pytest.fail("should not scroll at all")
    )
    _Scroll(amount = 0, direction = "down", physics = MousePhysics()).execute()

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

def test_scroll_until_runs_and_cleans_up_for_all_exit_conditions(monkeypatch):
    created_threads = []
    recorded_scrolls = []

    class InlineThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon
            self.joined = False
            created_threads.append(self)

        def start(self): self.target()

        @staticmethod
        def is_alive(): return False

        def join(self): self.joined = True

    monkeypatch.setattr(scroll_until_module.threading, "Thread", InlineThread)
    monkeypatch.setattr(scroll_until_module, "Timing", FakeTiming)
    monkeypatch.setattr(scroll_until_module, "TimingInfo", lambda: FakeClock([0, 0]))
    monkeypatch.setattr(
        scroll_until_module,
        "_Scroll",
        lambda **keyword_arguments: _create_mock_action(
            lambda: recorded_scrolls.append(keyword_arguments)
        )
    )
    action = scroll_until_module._ScrollUntil(lambda: False, amount = 1, timeout = 1)
    assert action.execute() is False
    assert recorded_scrolls[0]["amount"] == 1
    assert created_threads[-1].joined is True
    assert scroll_until_module._ScrollUntil(lambda: True, amount = 1, timeout = 1).execute() is True
    stopped = threading.Event()
    stopped.set()
    assert scroll_until_module._ScrollUntil(
        lambda: False, amount = 1, timeout = 1
    ).execute(stopped) is False

    class WaitingThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon
            self.joined = False

        def start(self): pass

        @staticmethod
        def is_alive(): return True

        def join(self): self.joined = True

    conditions = iter([False, True])
    monkeypatch.setattr(scroll_until_module.threading, "Thread", WaitingThread)
    monkeypatch.setattr(scroll_until_module, "TimingInfo", lambda: FakeClock([0, 0, 0]))
    FakeTiming.waits.clear()
    assert scroll_until_module._ScrollUntil(
        lambda: next(conditions), amount = 1, timeout = 1
    ).execute() is True
    assert FakeTiming.waits[-1] == 0.1
    monkeypatch.setattr(scroll_until_module.threading, "Thread", WaitingThread)
    monkeypatch.setattr(scroll_until_module, "TimingInfo", lambda: FakeClock([0, 2]))
    assert scroll_until_module._ScrollUntil(lambda: False, amount = 1, timeout = 1).execute() is False

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
    assert len(scroll_calls) == calls_right_after

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

def test_wander_covers_default_stop_variation_and_insufficient_time(monkeypatch):
    recorded_moves = []
    monkeypatch.setattr(wander_module, "Timing", FakeTiming)
    monkeypatch.setattr(
        wander_module,
        "_Move",
        lambda *arguments, **keyword_arguments: _create_mock_action(
            lambda: recorded_moves.append((arguments, keyword_arguments))
        )
    )
    monkeypatch.setattr(wander_module._Wander, "_get_next_target", lambda *args: (10, 20))
    monkeypatch.setattr(wander_module, "_apply_variation", lambda value, variation: value)
    monkeypatch.setattr(
        wander_module,
        "ScreenInfo",
        lambda: SimpleNamespace(work_area = (0, 0, 100, 100))
    )
    wander_module._Wander(0).execute()
    monkeypatch.setattr(wander_module, "TimingInfo", lambda: FakeClock([0, 0, 1]))
    default_region_wander = wander_module._Wander(1)
    default_region_wander.execute()
    assert default_region_wander.region == (0, 10, 100, 100)
    stop_event = threading.Event()
    stop_event.set()
    monkeypatch.setattr(wander_module, "TimingInfo", lambda: FakeClock([0, 0]))
    wander_module._Wander(1, region = (0, 0, 10, 10)).execute(stop_event)
    monkeypatch.setattr(wander_module, "TimingInfo", lambda: FakeClock([0, 0, 0]))
    wander_module._Wander(
        2,
        region = (0, 0, 10, 10),
        maximum_steps = 1,
        physics = MousePhysics(
            duration = 0.5,
            duration_variation = 0.5,
            wander_distance_ratio = 1,
            wander_distance_ratio_variation = 0.5
        )
    ).execute()
    monkeypatch.setattr(wander_module, "TimingInfo", lambda: FakeClock([0, 0, 0.1]))
    wander_module._Wander(
        0.1,
        region = (0, 0, 10, 10),
        physics = MousePhysics(wander_delay = 0.1, wander_delay_variation = 0.5)
    ).execute()
    FakeTiming.waits.clear()
    monkeypatch.setattr(wander_module, "TimingInfo", lambda: FakeClock([0, 0]))
    wander_module._Wander(
        0.1,
        region = (0, 0, 10, 10),
        physics = MousePhysics(duration = 1)
    ).execute()
    assert FakeTiming.waits[-1] == pytest.approx(0.1)
    waits = []
    fake_event = SimpleNamespace(
        is_set = lambda: False, wait = lambda duration: waits.append(duration) or False
    )
    monkeypatch.setattr(wander_module, "TimingInfo", lambda: FakeClock([0, 0]))
    wander_module._Wander(
        0.1,
        region = (0, 0, 10, 10),
        physics = MousePhysics(duration = 1)
    ).execute(fake_event)
    assert waits == [pytest.approx(0.1)]
    assert recorded_moves
    non_breaking_event = SimpleNamespace(is_set = lambda: False, wait = lambda duration: False)
    monkeypatch.setattr(wander_module, "TimingInfo", lambda: FakeClock([0, 0, 0]))
    wander_module._Wander(10, region = (0, 0, 10, 10), maximum_steps = 1).execute(non_breaking_event)

def test_wander_until_starts_the_inner_action_and_resolves_every_exit(monkeypatch):
    recorded_runs = []
    recorded_threads = []

    class InlineThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon
            self.joined = False
            recorded_threads.append(self)

        def start(self): self.target()

        @staticmethod
        def is_alive(): return False

        def join(self): self.joined = True

    monkeypatch.setattr(wander_until_module.threading, "Thread", InlineThread)
    monkeypatch.setattr(wander_until_module, "Timing", FakeTiming)
    monkeypatch.setattr(wander_until_module, "TimingInfo", lambda: FakeClock([0, 0]))
    monkeypatch.setattr(
        wander_until_module,
        "_Wander",
        lambda **keyword_arguments: _create_mock_action(
            lambda: recorded_runs.append(keyword_arguments)
        )
    )
    assert wander_until_module._WanderUntil(lambda: False, timeout = 1).execute() is False
    assert recorded_runs[-1]["duration"] == 1
    assert recorded_threads[-1].joined is True
    assert wander_until_module._WanderUntil(lambda: True, timeout = 1).execute() is True
    stopped = threading.Event()
    stopped.set()
    assert wander_until_module._WanderUntil(lambda: False, timeout = 1).execute(stopped) is False

    class WaitingThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon
            self.joined = False

        def start(self): pass

        @staticmethod
        def is_alive(): return True

        def join(self): self.joined = True

    conditions = iter([False, True])
    monkeypatch.setattr(wander_until_module.threading, "Thread", WaitingThread)
    monkeypatch.setattr(wander_until_module, "TimingInfo", lambda: FakeClock([0, 0, 0]))
    FakeTiming.waits.clear()
    assert wander_until_module._WanderUntil(lambda: next(conditions), timeout = 1).execute() is True
    assert FakeTiming.waits[-1] == 0.1
    monkeypatch.setattr(wander_until_module.threading, "Thread", WaitingThread)
    monkeypatch.setattr(wander_until_module, "TimingInfo", lambda: FakeClock([0, 2]))
    assert wander_until_module._WanderUntil(lambda: False, timeout = 1).execute() is False

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
    with pytest.raises(Interrupted): action.execute()
    calls_right_after = len(move_calls)
    time.sleep(0.3)
    assert len(move_calls) == calls_right_after

def _create_mock_action(callback):
    return SimpleNamespace(execute = lambda *arguments, **keyword_arguments: callback())