from advanced_automation_utilities.system import System
from advanced_automation_utilities.system._open_file import _OpenFile
from advanced_automation_utilities.system._kill_process import _KillProcess
from advanced_automation_utilities.system._shutdown import _Shutdown
from advanced_automation_utilities.system._restart import _Restart
from advanced_automation_utilities.system._enable_kill_switch import _EnableKillSwitch
from advanced_automation_utilities.system._disable_kill_switch import _DisableKillSwitch
from advanced_automation_utilities._kill_switch_event import KILL_SWITCH_EVENT
from advanced_automation_utilities import WindowNotFoundError
import advanced_automation_utilities.system.system as system_module
import advanced_automation_utilities.system._system_action as system_action_module
import advanced_automation_utilities.system.system_info as system_info_module
import advanced_automation_utilities.system._open_file as open_file_module
import advanced_automation_utilities.system._kill_process as _kill_process_module
import advanced_automation_utilities.system._lock_screen as lock_screen_module
import advanced_automation_utilities.system._sign_out as sign_out_module
import advanced_automation_utilities.system._sleep as sleep_module
import advanced_automation_utilities.system._hibernate as hibernate_module
import advanced_automation_utilities.system._shutdown as _shutdown_module
import advanced_automation_utilities.system._restart as _restart_module
import advanced_automation_utilities.system._enable_kill_switch as _enable_kill_switch_module
import advanced_automation_utilities.system._disable_kill_switch as _disable_kill_switch_module
import advanced_automation_utilities.backend.windows._system as _system_backend
from types import SimpleNamespace
from hypothesis import strategies, given
import pytest

def test_system_facade_delegates_to_actions(monkeypatch):
    recorded_calls = []
    attributes = (
        ("_OpenFile", "open"), ("_KillProcess", "kill"), ("_LockScreen", "lock"),
        ("_SignOut", "sign-out"), ("_Sleep", "sleep"), ("_Hibernate", "hibernate"),
        ("_Shutdown", "shutdown"), ("_Restart", "restart"),
        ("_EnableKillSwitch", "enable"), ("_DisableKillSwitch", "disable")
    )
    for attribute, name in attributes:
        monkeypatch.setattr(
            system_module,
            attribute,
            lambda *arguments, name = name, **keyword_arguments: SimpleNamespace(
                execute = lambda: recorded_calls.append((name, arguments, keyword_arguments)) or name
            )
        )
    system = system_module.System()
    system.open_file("file")
    system.kill_process("process", force = False)
    system.lock_screen()
    system.sign_out()
    system.sleep()
    system.hibernate()
    system.shutdown(1)
    system.restart(2)
    system.enable_kill_switch()
    system.disable_kill_switch()
    assert [name for name, _, _ in recorded_calls] == [
        "open",
        "kill",
        "lock",
        "sign-out",
        "sleep",
        "hibernate",
        "shutdown",
        "restart",
        "enable",
        "disable"
    ]
    assert recorded_calls[-2][1] == ("ctrl", "shift", "alt", "k")

def test_abstract_system_action_probe():
    class SystemActionProbe(system_action_module._SystemAction):
        def execute(self): return super().execute()

    assert SystemActionProbe().execute() is None

def test_system_info_properties(monkeypatch):
    monkeypatch.setattr(system_info_module, "_get_clipboard_text", lambda: "clipboard")
    monkeypatch.setattr(system_info_module, "_get_active_window_title", lambda: "title")
    monkeypatch.setattr(
        system_info_module, "_is_process_running", lambda process_name: process_name == "yes"
    )
    info = system_info_module.SystemInfo()
    assert info.clipboard_text == "clipboard"
    assert info.active_window_title == "title"
    assert info.is_process_running("yes") is True

def test_direct_system_actions_call_backend(monkeypatch):
    recorded_calls = []
    for module, action_class, backend_name, name in (
        (hibernate_module, hibernate_module._Hibernate, "_hibernate", "hibernate"),
        (lock_screen_module, lock_screen_module._LockScreen, "_lock_screen", "lock"),
        (sign_out_module, sign_out_module._SignOut, "_sign_out", "sign-out"),
        (sleep_module, sleep_module._Sleep, "_sleep", "sleep")
    ):
        monkeypatch.setattr(module, backend_name, lambda name = name: recorded_calls.append((name)))
        action_class().execute()

    monkeypatch.setattr(open_file_module.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(
        open_file_module, "_open_file", lambda path: recorded_calls.append(("open", path))
    )
    open_file_module._OpenFile("safe-test-file").execute()
    assert recorded_calls == [
        ("hibernate"), ("lock"), ("sign-out"), ("sleep"), ("open", "safe-test-file")
    ]

@given(text = strategies.text())
def test_clipboard_round_trips_whatever_text_is_set(text, fake_system):
    system = System()
    system.set_clipboard_text(text)
    assert fake_system.clipboard == text

def test_open_file_accepts_a_name_resolvable_via_path(): _OpenFile("python")

@pytest.mark.parametrize("extension", [".exe", ".com", ".bat", ".cmd"])
def test_open_file_starts_executable_with_its_parent_as_working_directory(
    extension, tmp_path, monkeypatch
):
    executable_path = tmp_path / f"program{extension}"
    executable_path.touch()
    popen_calls = []
    startfile_calls = []
    monkeypatch.setattr(
        _system_backend.subprocess, "Popen", lambda command, cwd: popen_calls.append((command, cwd))
    )
    monkeypatch.setattr(_system_backend.os, "startfile", lambda path: startfile_calls.append(path))
    _system_backend._open_file(str(executable_path))
    expected_command = (
        ["cmd.exe", "/d", "/c", str(executable_path)]
        if extension in {".bat", ".cmd"}  else [str(executable_path)]
    )
    assert popen_calls == [(expected_command, str(tmp_path))]
    assert startfile_calls == []

def test_open_file_opens_non_executable_file_with_its_default_application(tmp_path, monkeypatch):
    file_path = tmp_path / "document.txt"
    file_path.touch()
    popen_calls = []
    startfile_calls = []
    monkeypatch.setattr(
        _system_backend.subprocess, "Popen", lambda *args, **kwargs: popen_calls.append((args, kwargs))
    )
    monkeypatch.setattr(_system_backend.os, "startfile", lambda path: startfile_calls.append(path))
    _system_backend._open_file(str(file_path))
    assert popen_calls == []
    assert startfile_calls == [str(file_path)]

def test_open_file_rejects_a_path_that_does_not_exist_and_is_not_on_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        _OpenFile(str(tmp_path / "definitely_not_a_real_executable.exe"))

@pytest.mark.parametrize("action_name, call", [
    ("focus_window", lambda system, title: system.focus_window(title)),
    ("resize_window", lambda system, title: system.resize_window(title, 800, 600)),
    ("move_window", lambda system, title: system.move_window(title, 0, 0)),
    ("close_window", lambda system, title: system.close_window(title))
])
def test_window_actions_succeed_on_an_existing_window(action_name, call, fake_system):
    fake_system.open_windows.add("Notepad")
    system = System()
    call(system, "Notepad")
    assert fake_system.calls == [(action_name.replace("_window", ""), "Notepad")]

@pytest.mark.parametrize("action_name, call", [
    ("focus_window", lambda system, title: system.focus_window(title)),
    ("resize_window", lambda system, title: system.resize_window(title, 800, 600)),
    ("move_window", lambda system, title: system.move_window(title, 0, 0)),
    ("close_window", lambda system, title: system.close_window(title))
])
def test_window_actions_raise_when_the_window_does_not_exist(action_name, call, fake_system):
    system = System()
    with pytest.raises(WindowNotFoundError): call(system, "A Window That Was Never Opened")

def test_close_window_only_acts_on_one_window_even_with_duplicate_titles(fake_system):
    fake_system.open_windows.add("Untitled - Notepad")
    System().close_window("Untitled - Notepad")
    assert len(fake_system.calls) == 1

def test_kill_process_defaults_to_force_true(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        _kill_process_module, "_kill_process", lambda process, force: captured.update(force = force)
    )
    _KillProcess("notepad.exe").execute()
    assert captured["force"] is True

@pytest.mark.parametrize("force", [True, False])
def test_kill_process_passes_force_through(force, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        _kill_process_module, "_kill_process",
        lambda process, force: captured.update(process = process, force = force)
    )
    _KillProcess("notepad.exe", force = force).execute()
    assert captured == {"process": "notepad.exe", "force": force}

def test_enable_kill_switch_clears_a_previously_set_event_and_passes_the_keys(monkeypatch):
    KILL_SWITCH_EVENT.set()
    captured = {}
    monkeypatch.setattr(
        _enable_kill_switch_module,
        "_enable_kill_switch",
        lambda keys: captured.setdefault("keys", keys)
    )
    _EnableKillSwitch("ctrl", "shift", "k").execute()
    assert not KILL_SWITCH_EVENT.is_set()
    assert captured["keys"] == ["ctrl", "shift", "k"]

def test_disable_kill_switch_clears_the_event_and_calls_the_backend(monkeypatch):
    KILL_SWITCH_EVENT.set()
    calls = []
    monkeypatch.setattr(_disable_kill_switch_module, "_disable_kill_switch", lambda: calls.append(1))
    _DisableKillSwitch().execute()
    assert not KILL_SWITCH_EVENT.is_set()
    assert calls == [1]

@pytest.mark.parametrize(
    "action_class,"
    "module,"
    "backend_name",
    [(_Restart, _restart_module, "_restart"), (_Shutdown, _shutdown_module, "_shutdown")]
)
def test_restart_and_shutdown_pass_the_delay_through(action_class, module, backend_name, monkeypatch):
    captured = {}
    monkeypatch.setattr(module, backend_name, lambda delay: captured.setdefault("delay", delay))
    action_class(delay = 30).execute()
    assert captured["delay"] == 30

@pytest.mark.parametrize(
    "action_class, module", [(_Restart, _restart_module), (_Shutdown, _shutdown_module)]
)
def test_restart_and_shutdown_reject_a_negative_delay(action_class, module):
    with pytest.raises(ValueError): action_class(delay = -1)