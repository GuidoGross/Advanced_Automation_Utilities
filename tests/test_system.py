from advanced_automation_utilities.system import System
from advanced_automation_utilities.system._open_file import _OpenFile
from advanced_automation_utilities import WindowNotFoundError
import advanced_automation_utilities.backend.windows._system as _system_backend
from hypothesis import strategies, given
import pytest

@given(text = strategies.text())
def test_clipboard_round_trips_whatever_text_is_set(text, fake_system):
    system = System()
    system.set_clipboard_text(text)
    assert fake_system.clipboard == text

def test_open_file_rejects_a_path_that_does_not_exist_and_is_not_on_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        _OpenFile(str(tmp_path / "definitely_not_a_real_executable.exe"))

def test_open_file_accepts_a_name_resolvable_via_path(): _OpenFile("python")

@pytest.mark.parametrize("extension", [".exe", ".com", ".bat", ".cmd"])
def test_open_file_starts_executable_with_its_parent_as_working_directory(
    extension,
    tmp_path,
    monkeypatch
):
    executable_path = tmp_path / f"program{extension}"
    executable_path.touch()
    popen_calls = []
    startfile_calls = []
    monkeypatch.setattr(
        _system_backend.subprocess,
        "Popen",
        lambda command, cwd: popen_calls.append((command, cwd))
    )
    monkeypatch.setattr(
        _system_backend.os,
        "startfile",
        lambda path: startfile_calls.append(path)
    )
    _system_backend._open_file(str(executable_path))
    expected_command = (
        ["cmd.exe", "/d", "/c", str(executable_path)] if extension in {".bat", ".cmd"}  else [str(executable_path)]
    )
    assert popen_calls == [(expected_command, str(tmp_path))]
    assert startfile_calls == []

def test_open_file_opens_non_executable_file_with_its_default_application(tmp_path, monkeypatch):
    file_path = tmp_path / "document.txt"
    file_path.touch()
    popen_calls = []
    startfile_calls = []
    monkeypatch.setattr(
        _system_backend.subprocess,
        "Popen",
        lambda *args, **kwargs: popen_calls.append((args, kwargs))
    )
    monkeypatch.setattr(
        _system_backend.os,
        "startfile",
        lambda path: startfile_calls.append(path)
    )
    _system_backend._open_file(str(file_path))
    assert popen_calls == []
    assert startfile_calls == [str(file_path)]

@pytest.mark.parametrize("action_name, call", [
    ("focus_window", lambda system, title: system.focus_window(title)),
    ("resize_window", lambda system, title: system.resize_window(title, 800, 600)),
    ("move_window", lambda system, title: system.move_window(title, 0, 0)),
    ("close_window", lambda system, title: system.close_window(title)),
])
def test_window_actions_raise_when_the_window_does_not_exist(action_name, call, fake_system):
    system = System()
    with pytest.raises(WindowNotFoundError): call(system, "A Window That Was Never Opened")

@pytest.mark.parametrize("action_name, call", [
    ("focus_window", lambda system, title: system.focus_window(title)),
    ("resize_window", lambda system, title: system.resize_window(title, 800, 600)),
    ("move_window", lambda system, title: system.move_window(title, 0, 0)),
    ("close_window", lambda system, title: system.close_window(title)),
])
def test_window_actions_succeed_on_an_existing_window(action_name, call, fake_system):
    fake_system.open_windows.add("Notepad")
    system = System()
    call(system, "Notepad")
    assert fake_system.calls == [(action_name.replace("_window", ""), "Notepad")]

def test_close_window_only_acts_on_one_window_even_with_duplicate_titles(fake_system):
    fake_system.open_windows.add("Untitled - Notepad")
    System().close_window("Untitled - Notepad")
    assert len(fake_system.calls) == 1