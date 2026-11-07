from advanced_automation_utilities import KillSwitchTriggered
from advanced_automation_utilities._queueable_controller import _QueueableController
from advanced_automation_utilities._asynchronous_context import _AsynchronousContext
from advanced_automation_utilities._task import Task
from advanced_automation_utilities._kill_switch_event import trigger_kill_switch, KILL_SWITCH_EVENT
from advanced_automation_utilities._kill_switch_event import _asynchronous_raise
import advanced_automation_utilities._kill_switch_event as kill_switch_module
from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import time
import threading
import pytest
import queue

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
    def test_no_task_silently_hangs_forever(self):
        for task in self.tasks:
            completed_in_time = task._done_event.wait(timeout = 2)
            assert completed_in_time

    def teardown(self):
        trigger_kill_switch()
        try:
            for task in self.tasks:
                if not task._done_event.wait(timeout = 1): continue
                try: task.wait()
                except KillSwitchTriggered: pass
        finally:
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
    with controller.asynchronous() as second_task:
        controller._execute_or_queue(Recording("second", 0.1))
    first_task.wait()
    second_task.wait()
    second_start = next(
        timestamp for action, name, timestamp in order if action == "start" and name == "second"
    )
    first_end = next(
        timestamp for action, name, timestamp in order if action == "end" and name == "first"
    )
    assert second_start >= first_end

def test_an_empty_asynchronous_block_resolves_immediately():
    controller = _QueueableController()
    with controller.asynchronous() as task: pass
    assert task._done_event.is_set()

def test_nested_asynchronous_contexts():
    controller = _QueueableController()
    execution_order = []

    class RecordAction:
        def __init__(self, tag): self.tag = tag

        def execute(self): execution_order.append(self.tag)

    with controller.asynchronous() as task_1:
        controller._execute_or_queue(RecordAction("outer_action_1"))
        with controller.asynchronous() as task_2:
            controller._execute_or_queue(RecordAction("inner_action_1"))
            controller._execute_or_queue(RecordAction("inner_action_2"))
        controller._execute_or_queue(RecordAction("outer_action_2"))
    assert task_1 is task_2
    completed = task_1.wait(timeout = 2)
    assert completed is True
    assert execution_order == ["outer_action_1", "inner_action_1", "inner_action_2", "outer_action_2"]

def test_nested_asynchronous_context_caught_exception_prunes_only_inner_actions():
    controller = _QueueableController()
    execution_order = []

    class RecordAction:
        def __init__(self, tag): self.tag = tag

        def execute(self): execution_order.append(self.tag)

    with controller.asynchronous() as task:
        controller._execute_or_queue(RecordAction("outer_action_1"))
        try:
            with controller.asynchronous():
                controller._execute_or_queue(RecordAction("inner_action_1"))
                raise ValueError("inner failure")
        except ValueError: pass
        assert not task._done_event.is_set()
        assert task._exception is None
        controller._execute_or_queue(RecordAction("outer_action_2"))
    assert task.wait(timeout = 2) is True
    assert execution_order == ["outer_action_1", "outer_action_2"]

def test_nested_asynchronous_context_uncaught_exception_cancels_all_actions():
    controller = _QueueableController()
    execution_order = []

    class RecordAction:
        def __init__(self, tag): self.tag = tag

        def execute(self): execution_order.append(self.tag)

    try:
        with controller.asynchronous() as task:
            controller._execute_or_queue(RecordAction("outer_action_1"))
            with controller.asynchronous():
                controller._execute_or_queue(RecordAction("inner_action_1"))
                raise ValueError("uncaught failure")
            controller._execute_or_queue(RecordAction("outer_action_2"))
    except ValueError: pass
    else: pytest.fail("exception should have propagated")
    assert task._done_event.is_set()
    assert isinstance(task._exception, ValueError)
    assert not execution_order
    with pytest.raises(ValueError, match = "uncaught failure"): task.wait()

def test_asynchronous_context_exit_with_an_empty_stack():
    controller = _QueueableController()
    asynchronous_context = _AsynchronousContext(controller)
    asynchronous_context.__exit__(None, None, None)

def test_controller_level_wait_executes_through_the_queue(monkeypatch):
    controller = _QueueableController()
    start_time = time.perf_counter()
    controller.wait(0.05)
    assert time.perf_counter() - start_time >= 0.05

def test_controller_level_wait_random_executes_through_the_queue():
    controller = _QueueableController()
    start_time = time.perf_counter()
    controller.wait_random(0.02, 0.05)
    assert time.perf_counter() - start_time >= 0.02

def test_controller_level_wait_until_executes_through_the_queue():
    controller = _QueueableController()
    calls = {"n": 0}

    def becomes_true_on_the_second_check():
        calls["n"] += 1
        return calls["n"] >= 2

    controller.wait_until(becomes_true_on_the_second_check, timeout = 2, poll_interval = 0.01)
    assert calls["n"] == 2

def test_controller_shuts_down_cleanly_on_the_none_sentinel():
    controller = _QueueableController()

    class Tiny:
        def execute(self): pass

    with controller.asynchronous() as task: controller._execute_or_queue(Tiny())
    task.wait()
    worker_thread = controller._worker_thread
    assert worker_thread is not None
    controller._task_queue.put(None)
    worker_thread.join(timeout = 2)
    assert not worker_thread.is_alive()

def test_controller_close_when_no_worker_is_running():
    controller = _QueueableController()
    controller._close()
    assert controller._worker_thread is None

def test_controller_context_manager_closes_its_worker():
    with _QueueableController() as controller:
        with controller.asynchronous() as task: controller._execute_or_queue(DummyAction(0.01))
        task.wait()
        worker_thread = controller._worker_thread
        if worker_thread is not None: worker_thread.join()
        assert controller._worker_thread is None
        assert worker_thread is None or not worker_thread.is_alive()

def test_worker_stops_after_processing_all_queued_tasks():
    controller = _QueueableController()
    with controller.asynchronous() as task: controller._execute_or_queue(DummyAction(0.01))
    task.wait()
    worker_thread = controller._worker_thread
    if worker_thread is not None: worker_thread.join()
    assert controller._worker_thread is None
    assert worker_thread is None or not worker_thread.is_alive()

def test_worker_restarts_for_a_later_asynchronous_block():
    controller = _QueueableController()
    worker_threads = []

    class RecordWorker:
        def execute(self): worker_threads.append(threading.current_thread())

    with controller.asynchronous() as first_task: controller._execute_or_queue(RecordWorker())
    first_task.wait()
    first_worker = worker_threads[-1]
    first_worker.join()
    with controller.asynchronous() as second_task: controller._execute_or_queue(RecordWorker())
    second_task.wait()
    second_worker = worker_threads[-1]
    second_worker.join()
    assert first_worker is not second_worker
    assert controller._worker_thread is None

def test_a_task_cancelled_before_the_worker_ever_starts_it_runs_no_actions():
    class Tiny:
        def __init__(self): self.ran = False

        def execute(self): self.ran = True

    controller = _QueueableController()
    action = Tiny()
    with controller.asynchronous() as task:
        controller._execute_or_queue(action)
        task.cancel()
    assert task._done_event.wait(timeout = 2)
    assert not action.ran

def test_cancelling_mid_task_stops_before_the_next_action():
    class CancellingFirstAction:
        def __init__(self, task_ref): self.task_ref = task_ref; self.ran = False

        def execute(self):
            self.ran = True
            self.task_ref["task"].cancel()

    class ShouldNeverRun:
        def __init__(self): self.ran = False

        def execute(self): self.ran = True

    controller = _QueueableController()
    task_ref = {}
    with controller.asynchronous() as task:
        task_ref["task"] = task
        first = CancellingFirstAction(task_ref)
        second = ShouldNeverRun()
        controller._execute_or_queue(first)
        controller._execute_or_queue(second)
    assert task._done_event.wait(timeout = 2)
    assert first.ran and not second.ran

def test_exception_while_a_task_is_already_dequeued_still_resolves_that_task(monkeypatch):
    class PoisonedTask:
        def __init__(self):
            self._done_event = threading.Event()
            self._actions = []
            self.results = []
            self.last_result = None
            self._exception = None

        @property
        def _cancelled(self): raise KillSwitchTriggered()

    class Tiny:
        def execute(self): pass

    controller = _QueueableController()
    poisoned_task = PoisonedTask()
    served = {"n": False}

    class OneShotQueue:
        def __init__(self): self._fallback = controller._task_queue

        def get(self):
            if not served["n"]:
                served["n"] = True
                return poisoned_task
            return self._fallback.get()

        def put(self, item): self._fallback.put(item)

        def empty(self): return self._fallback.empty()

    monkeypatch.setattr(controller, "_task_queue", OneShotQueue())
    controller._submit_task(Task())
    assert poisoned_task._done_event.wait(timeout = 2)
    assert isinstance(getattr(poisoned_task, "_exception"), KillSwitchTriggered)
    with controller.asynchronous() as task: controller._execute_or_queue(Tiny())
    assert task._done_event.wait(timeout = 2)

def test_an_exception_while_queueing_actions_skips_them_all_and_still_marks_the_task_done():
    controller = _QueueableController()
    executed = []

    class Dummy:
        def execute(self): executed.append(True)

    try:
        with controller.asynchronous() as task:
            controller._execute_or_queue(Dummy())
            raise ValueError("boom")
    except ValueError: pass
    else: pytest.fail("the ValueError raised inside the with block should have propagated")
    assert task._done_event.is_set()
    assert isinstance(task._exception, ValueError)
    assert not executed
    with pytest.raises(ValueError, match = "boom"): task.wait()

def test_task_wait_with_timeout_returns_true_when_completed():
    controller = _QueueableController()
    with controller.asynchronous() as task: controller.wait(0.01)
    assert task.wait(timeout = 2) is True

def test_task_wait_with_timeout_returns_false_when_timed_out():
    controller = _QueueableController()
    with controller.asynchronous() as task: controller.wait(0.5)
    assert task.wait(timeout = 0.01) is False
    assert task.wait(timeout = 2) is True

def test_task_wait_with_negative_timeout_raises_value_error():
    task = Task()
    with pytest.raises(ValueError, match = "(?i)timeout"): task.wait(timeout = -1)

def test_worker_recovers_deterministically_from_the_exact_gap_the_outer_except_fixes(monkeypatch):
    class Tiny:
        def execute(self): pass

    controller = _QueueableController()
    real_queue = queue.Queue()
    call_count = {"n": 0}

    class PoisonedQueue:
        def get(self):
            call_count["n"] += 1
            if call_count["n"] == 2: raise KillSwitchTriggered()
            return real_queue.get()

        def put(self, item): real_queue.put(item)

        def empty(self): return real_queue.empty()

    monkeypatch.setattr(controller, "_task_queue", PoisonedQueue())
    with controller.asynchronous() as task_a: controller._execute_or_queue(Tiny())
    task_a.wait()
    assert task_a.is_done and task_a._exception is None
    with controller.asynchronous() as task_b: controller._execute_or_queue(Tiny())
    assert task_b._done_event.wait(timeout = 2)

def test_real_kill_switch_interrupts_a_genuinely_busy_worker_thread(monkeypatch):
    class BusySpin:
        def __init__(self, seconds): self.seconds, self.iterations = seconds, 0

        def execute(self):
            end_time = time.perf_counter() + self.seconds
            while time.perf_counter() < end_time: self.iterations += 1

    controller = _QueueableController()
    action = BusySpin(5)
    with controller.asynchronous() as task: controller._execute_or_queue(action)
    main_thread_id = threading.get_ident()
    real_asynchronous_raise = kill_switch_module._asynchronous_raise

    def raise_on_worker_threads(thread_id, exception_type):
        if thread_id != main_thread_id: real_asynchronous_raise(thread_id, exception_type)

    monkeypatch.setattr(kill_switch_module, "_asynchronous_raise", raise_on_worker_threads)
    timer = threading.Timer(0.2, trigger_kill_switch)
    timer.start()
    start_time = time.perf_counter()
    try:
        with pytest.raises(KillSwitchTriggered): task.wait()
        elapsed = time.perf_counter() - start_time
    finally: timer.join(timeout = 2)
    assert elapsed < 1

def test_trigger_kill_switch_reaches_more_than_one_live_worker_thread(monkeypatch):
    class BusySpin:
        def execute(self):
            end_time = time.perf_counter() + 2.0
            while time.perf_counter() < end_time: pass

    controller_a, controller_b = _QueueableController(), _QueueableController()
    with controller_a.asynchronous() as task_a: controller_a._execute_or_queue(BusySpin())
    with controller_b.asynchronous() as task_b: controller_b._execute_or_queue(BusySpin())
    main_thread_id = threading.get_ident()
    real_asynchronous_raise = kill_switch_module._asynchronous_raise

    def raise_on_worker_threads(thread_id, exception_type):
        if thread_id != main_thread_id: real_asynchronous_raise(thread_id, exception_type)

    monkeypatch.setattr(kill_switch_module, "_asynchronous_raise", raise_on_worker_threads)
    timer = threading.Timer(0.1, trigger_kill_switch)
    timer.start()
    interrupted = 0
    try:
        for task in (task_a, task_b):
            try: task.wait()
            except KillSwitchTriggered: interrupted += 1
    finally: timer.join(timeout = 2)
    assert interrupted == 2

def test_trigger_kill_switch_is_idempotent_and_does_not_re_scan_threads_when_already_set():
    KILL_SWITCH_EVENT.set()
    real_enumerate = threading.enumerate
    calls = {"n": 0}

    def spy_enumerate():
        calls["n"] += 1
        return real_enumerate()

    kill_switch_module.threading.enumerate = spy_enumerate
    try:
        trigger_kill_switch()
        assert calls["n"] == 0
    finally:
        kill_switch_module.threading.enumerate = real_enumerate
        KILL_SWITCH_EVENT.clear()

def test_trigger_kill_switch_ignores_unrelated_alive_threads(monkeypatch):
    class UnrelatedAliveThread:
        ident = 200
        name = "unrelated-background-thread"

        @staticmethod
        def is_alive(): return True

    fake_kill_switch_event = threading.Event()
    recorded_asynchronous_raise_calls = []
    monkeypatch.setattr(kill_switch_module, "KILL_SWITCH_EVENT", fake_kill_switch_event)
    monkeypatch.setattr(kill_switch_module.threading, "get_ident", lambda: 100)
    monkeypatch.setattr(kill_switch_module.threading, "enumerate", lambda: [UnrelatedAliveThread()])
    monkeypatch.setattr(kill_switch_module.threading, "main_thread", lambda: object())
    monkeypatch.setattr(
        kill_switch_module,
        "_asynchronous_raise",
        lambda *arguments: recorded_asynchronous_raise_calls.append(arguments)
    )
    kill_switch_module.trigger_kill_switch()
    assert fake_kill_switch_event.is_set()
    assert recorded_asynchronous_raise_calls == []

def test_asynchronous_raise_with_no_thread_id_does_nothing():
    _asynchronous_raise(None, KillSwitchTriggered)

def test_asynchronous_raise_with_a_nonexistent_thread_id_does_nothing():
    _asynchronous_raise(999999999, KillSwitchTriggered)

@pytest.fixture(autouse = True)
def _reset_kill_switch_event():
    KILL_SWITCH_EVENT.clear()
    yield
    KILL_SWITCH_EVENT.clear()