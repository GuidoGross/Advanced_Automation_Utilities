from ._task import _ACTIVE_TASKS
from .exceptions import KillSwitchTriggered
import threading
import ctypes

KILL_SWITCH_EVENT = threading.Event()

def trigger_kill_switch():
    if KILL_SWITCH_EVENT.is_set(): return
    KILL_SWITCH_EVENT.set()
    for task in list(_ACTIVE_TASKS): task.cancel()
    current_thread_id = threading.get_ident()
    for thread in threading.enumerate():
        if thread.ident == current_thread_id: continue
        if thread.is_alive() and (thread.name.startswith("worker_thread_") or thread is threading.main_thread()):
            _asynchronous_raise(thread.ident, KillSwitchTriggered)

def _asynchronous_raise(thread_id, exception_type):
    if thread_id is None: return
    result = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(thread_id), ctypes.py_object(exception_type)
    )
    if result == 0: pass
    elif result != 1: ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 0)