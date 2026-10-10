from advanced_automation_utilities import KillSwitchTriggered
from advanced_automation_utilities._queueable_controller import _QueueableController
from advanced_automation_utilities._kill_switch_event import KILL_SWITCH_EVENT, trigger_kill_switch
from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import time
import threading
import pytest

class DummyAction:
    def __init__(self, duration = 0.05):
        self.duration = duration
        self.executed = False

    def execute(self, stop_event = None):
        end_time = time.perf_counter() + self.duration
        while time.perf_counter() < end_time:
            if stop_event is not None and stop_event.is_set(): return
            if KILL_SWITCH_EVENT.is_set(): return
            time.sleep(0.005)
        self.executed = True

class AsyncStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.controller = _QueueableController()
        self.tasks = []

    @rule()
    def queue_an_action(self):
        with self.controller.asynchronous() as task: self.controller._execute_or_queue(DummyAction())
        self.tasks.append(task)

    @rule()
    def cancel_a_task(self):
        if self.tasks: self.tasks[-1].cancel()

    @rule()
    def trigger_kill_switch(self):
        trigger_kill_switch()
        KILL_SWITCH_EVENT.clear()

    @invariant()
    def no_task_silently_hangs_forever(self):
        for task in self.tasks:
            completed_in_time = task._done_event.wait(timeout = 2)
            assert completed_in_time, "a queued task never completed"

    def teardown(self):
        trigger_kill_switch()
        for task in self.tasks:
            if not task._done_event.wait(timeout = 1): continue
            try: task.wait()
            except KillSwitchTriggered: pass
        KILL_SWITCH_EVENT.clear()

TestAsyncStateMachine = AsyncStateMachine.TestCase
TestAsyncStateMachine.settings = settings(deadline = None, stateful_step_count = 15)

def test_two_asynchronous_blocks_on_the_same_controller_wait_for_each_other():
    controller = _QueueableController()
    order = []

    class Recording:
        def __init__(self, name, duration): self.name, self.duration = name, duration
        def execute(self):
            order.append(("start", self.name, time.perf_counter()))
            time.sleep(self.duration)
            order.append(("end", self.name, time.perf_counter()))

    with controller.asynchronous() as first_task: controller._execute_or_queue(Recording("first", 0.2))
    with controller.asynchronous() as second_task: controller._execute_or_queue(Recording("second", 0.1))
    first_task.wait()
    second_task.wait()
    second_start = next(
        timestamp for action, name, timestamp in order if action == "start" and name == "second"
    )
    first_end = next(
        timestamp for action, name, timestamp in order if action == "end" and name == "first"
    )
    assert second_start >= first_end, "the second block started before the first one finished"

def test_real_kill_switch_interrupts_a_genuinely_busy_worker_thread():
    class BusySpin:
        def __init__(self, seconds): self.seconds, self.iterations = seconds, 0

        def execute(self):
            end_time = time.perf_counter() + self.seconds
            while time.perf_counter() < end_time: self.iterations += 1

    controller = _QueueableController()
    action = BusySpin(5)
    with controller.asynchronous() as task: controller._execute_or_queue(action)
    threading.Timer(0.2, trigger_kill_switch).start()
    start_time = time.perf_counter()
    with pytest.raises(KillSwitchTriggered): task.wait()
    elapsed = time.perf_counter() - start_time
    KILL_SWITCH_EVENT.clear()
    assert elapsed < 1, "the busy worker thread ran to completion instead of being interrupted"