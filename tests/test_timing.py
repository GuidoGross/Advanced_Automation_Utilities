from advanced_automation_utilities.timing import Timing, measure_time
from advanced_automation_utilities.timing._wait import _Wait
from advanced_automation_utilities.timing._wait_until import _WaitUntil
from advanced_automation_utilities._kill_switch_event import KILL_SWITCH_EVENT
import advanced_automation_utilities.timing.timing as timing_module
import advanced_automation_utilities.timing._timing_action as timing_action_module
import advanced_automation_utilities.timing._wait as wait_module
import advanced_automation_utilities.timing._wait_random as wait_random_module
from types import SimpleNamespace
import pytest
import threading
import time

def test_timing_facade_and_wait_random(monkeypatch):
    recorded_waits = []
    monkeypatch.setattr(
        timing_module,
        "_WaitRandom",
        lambda *arguments, **keyword_arguments: SimpleNamespace(
            execute = lambda: recorded_waits.append((arguments, keyword_arguments))
        )
    )
    monkeypatch.setattr(
        timing_module,
        "_WaitUntil",
        lambda *arguments, **keyword_arguments: SimpleNamespace(execute = lambda: True)
    )
    assert timing_module.Timing().wait_random(1, 2) is None
    assert timing_module.Timing().wait_until(lambda: True) is True
    assert recorded_waits == [((), {"minimum_duration": 1, "maximum_duration": 2})]
    with pytest.raises(ValueError, match = "Minimum duration"): wait_random_module._WaitRandom(2, 1)

def test_abstract_timing_action_probe():
    class TimingActionProbe(timing_action_module._TimingAction):
        def execute(self): return super().execute()

    assert TimingActionProbe().execute() is None

def test_wait_rejects_negative_duration():
    with pytest.raises(ValueError, match = "Duration cannot be negative."): Timing().wait(-0.01)

def test_wait_executes_sub_margin_duration(): assert Timing().wait(0.001) is None

def test_wait_stops_when_the_kill_switch_is_already_set():
    KILL_SWITCH_EVENT.set()
    try: _Wait(1).execute()
    finally: KILL_SWITCH_EVENT.clear()

def test_wait_stops_when_cancelled_during_the_final_spin(monkeypatch):
    class StopAfterFirstSpinCheck:
        def __init__(self): self.checks = 0

        def is_set(self):
            self.checks += 1
            return self.checks == 2

    stop_event = StopAfterFirstSpinCheck()
    clock_values = iter((0, 0, 0.0005))
    monkeypatch.setattr(wait_module.time, "perf_counter", lambda: next(clock_values))
    assert _Wait(0.001).execute(stop_event = stop_event) is None
    assert stop_event.checks == 2

def test_wait_is_interrupted_promptly_by_the_kill_switch_instead_of_running_the_full_duration():
    threading.Timer(0.25, KILL_SWITCH_EVENT.set).start()
    start_time = time.perf_counter()
    Timing().wait(5)
    elapsed = time.perf_counter() - start_time
    KILL_SWITCH_EVENT.clear()
    assert elapsed < 1

def test_wait_until_returns_true_as_soon_as_the_condition_becomes_true():
    calls = {"count": 0}

    def becomes_true_on_the_third_check():
        calls["count"] += 1
        return calls["count"] >= 3

    result = _WaitUntil(becomes_true_on_the_third_check, timeout = 5, poll_interval = 0.01).execute()
    assert result is True
    assert calls["count"] == 3

def test_wait_until_returns_false_after_timing_out():
    start_time = time.perf_counter()
    result = _WaitUntil(lambda: False, timeout = 0.3, poll_interval = 0.01).execute()
    elapsed = time.perf_counter() - start_time
    assert result is False
    assert 0.3 <= elapsed < 1

def test_wait_until_stops_early_when_its_stop_event_is_set():
    stop_event = threading.Event()
    threading.Timer(0.1, stop_event.set).start()
    start_time = time.perf_counter()
    result = _WaitUntil(
        lambda: False, timeout = 0, poll_interval = 0.01
    ).execute(stop_event = stop_event)
    elapsed = time.perf_counter() - start_time
    assert result is False
    assert elapsed < 0.5

def test_measure_time_preserves_the_return_value_and_arguments():
    @measure_time
    def add(a, b): return a + b

    assert add(2, 3) == 5

def test_measure_time_does_not_swallow_exceptions():
    @measure_time
    def boom(): raise ValueError("Expected")

    with pytest.raises(ValueError, match = "Expected"): boom()