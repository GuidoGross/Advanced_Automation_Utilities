from advanced_automation_utilities.timing._wait import _Wait
from advanced_automation_utilities.timing._wait_until import _WaitUntil
from advanced_automation_utilities._kill_switch_event import KILL_SWITCH_EVENT
from tui_utilities import decimal_format
import threading
import time

def test_wait_is_interrupted_promptly_by_the_kill_switch_instead_of_running_the_full_duration():
    threading.Timer(0.25, KILL_SWITCH_EVENT.set).start()
    start_time = time.perf_counter()
    _Wait(5).execute()
    elapsed = time.perf_counter() - start_time
    KILL_SWITCH_EVENT.clear()
    assert elapsed < 1, (
        f"wait() took {decimal_format(elapsed, 2)}s -- the kill switch did not interrupt it promptly"
    )

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