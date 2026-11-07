from advanced_automation_utilities.exceptions import WindowNotFoundError
import advanced_automation_utilities.backend.windows._mouse as mouse_backend
import advanced_automation_utilities.backend.windows._keyboard as keyboard_backend
import advanced_automation_utilities.backend.windows._screen as screen_backend
import advanced_automation_utilities.backend.windows._sound as sound_backend
import advanced_automation_utilities.backend.windows._system as system_backend
import advanced_automation_utilities.backend.windows._windows_backend_utilities as windows_backend_utilities
from pathlib import Path
from types import SimpleNamespace
import ctypes
import os
import pytest
import threading
import numpy
import io
import base64

class _MouseUser32:
    def __init__(self):
        self.sent_inputs = []
        self.cursor_position = (17, -4)
        self.set_positions = []

    def SendInput(self, count, pointer, size):
        array_type = mouse_backend._Input * count
        address = ctypes.cast(pointer, ctypes.c_void_p).value
        assert address is not None
        inputs = array_type.from_address(address)
        self.sent_inputs.extend(
            (
                item.mouse_input.flags,
                ctypes.c_long(item.mouse_input.mouse_data).value,
                item.mouse_input.delta_x,
                item.mouse_input.delta_y
            )
            for item in inputs
        )
        return count

    def GetCursorPos(self, pointer):
        point = ctypes.cast(pointer, ctypes.POINTER(mouse_backend._Point)).contents
        point.x, point.y = self.cursor_position

    def SetCursorPos(self, x, y): self.set_positions.append((x, y))

def test_windows_backend_platform_guard_rejects_non_windows(monkeypatch):
    modules = ("_mouse", "_keyboard", "_screen", "_sound", "_system", "_windows_backend_utilities")
    items = []
    for module in modules:
        path = Path(f"advanced_automation_utilities/backend/windows/{module}.py")
        lines = []
        for line in path.read_text(encoding = "utf-8").splitlines():
            lines.append(line)
            if line.strip() == "_ensure_windows()": break
        items.append((str(path.resolve()), "\n".join(lines)))
    monkeypatch.setattr(os, "name", "posix")
    for file_path, header in items:
        with pytest.raises(NotImplementedError, match = "only supported on Windows"):
            exec(
                compile(header, file_path, "exec"),
                {"__package__": "advanced_automation_utilities.backend.windows"}
            )

def test_ensure_windows_raises_on_non_windows(monkeypatch):
    monkeypatch.setattr(windows_backend_utilities.os, "name", "posix")
    with pytest.raises(NotImplementedError, match = "only supported on Windows"):
        windows_backend_utilities._ensure_windows()

def test_screen_dpi_awareness_is_marked_initialized_when_api_fails(monkeypatch):
    monkeypatch.setattr(windows_backend_utilities, "_dpi_initialized", False)
    failing_user32 = SimpleNamespace(
        SetProcessDPIAware = lambda: (_ for _ in ()).throw(RuntimeError("no DPI API"))
    )
    monkeypatch.setattr(windows_backend_utilities, "_user32", failing_user32)
    windows_backend_utilities._ensure_dpi_aware()
    assert windows_backend_utilities._dpi_initialized is True

def test_mouse_backend_translates_every_supported_command(monkeypatch):
    user32 = _MouseUser32()
    monkeypatch.setattr(mouse_backend, "_user32", user32)
    for button in ("left", "right", "middle"): mouse_backend._mouse_down(button)
    for button in ("left", "right", "middle"): mouse_backend._mouse_up(button)
    with pytest.raises(KeyError): mouse_backend._mouse_down("unsupported")
    with pytest.raises(KeyError): mouse_backend._mouse_up("unsupported")
    assert mouse_backend._get_cursor_position() == (17, -4)
    mouse_backend._set_cursor_position(3.9, -2.8)
    for direction in ("up", "down", "right", "left"): mouse_backend._scroll(4.9, direction)
    with pytest.raises(KeyError): mouse_backend._scroll(4.9, "unsupported")
    assert user32.sent_inputs == [
        (mouse_backend._LEFT_BUTTON_DOWN, 0, 0, 0),
        (mouse_backend._RIGHT_BUTTON_DOWN, 0, 0, 0),
        (mouse_backend._MIDDLE_BUTTON_DOWN, 0, 0, 0),
        (mouse_backend._LEFT_BUTTON_UP, 0, 0, 0),
        (mouse_backend._RIGHT_BUTTON_UP, 0, 0, 0),
        (mouse_backend._MIDDLE_BUTTON_UP, 0, 0, 0),
        (mouse_backend._WHEEL, 4, 0, 0),
        (mouse_backend._WHEEL, -4, 0, 0),
        (mouse_backend._HORIZONTAL_WHEEL, 4, 0, 0),
        (mouse_backend._HORIZONTAL_WHEEL, -4, 0, 0)
    ]
    assert user32.set_positions == [(3, -2)]

def test_mouse_cursor_position_calls_ensure_dpi_aware(monkeypatch):
    dpi_calls = []
    monkeypatch.setattr(mouse_backend, "_ensure_dpi_aware", lambda: dpi_calls.append("dpi"))
    user32 = _MouseUser32()
    monkeypatch.setattr(mouse_backend, "_user32", user32)
    mouse_backend._get_cursor_position()
    mouse_backend._set_cursor_position(10, 20)
    assert dpi_calls == ["dpi", "dpi"]

def test_mouse_send_input_error_raises_winerror(monkeypatch):
    failing_user32 = SimpleNamespace(SendInput = lambda count, pointer, size: 0)
    monkeypatch.setattr(mouse_backend, "_user32", failing_user32)
    monkeypatch.setattr(mouse_backend.ctypes, "get_last_error", lambda: 5)
    with pytest.raises(OSError): mouse_backend._mouse_down("left")

class _KeyboardUser32:
    def __init__(self):
        self.sent_inputs = []
        self.key_states = {}
        self.virtual_key_result = 0
        self.next_hook = 99
        self.hook_calls = []
        self.message_results = []
        self.translate_calls = 0
        self.dispatch_calls = 0

    def SendInput(self, count, pointer, _size):
        array_type = keyboard_backend._Input * count
        address = ctypes.cast(pointer, ctypes.c_void_p).value
        assert address is not None
        inputs = array_type.from_address(address)
        self.sent_inputs.extend(
            (
                item.keyboard_input.virtual_key_code,
                item.keyboard_input.scan_code,
                item.keyboard_input.flags
            )
            for item in inputs
        )
        return count

    def GetAsyncKeyState(self, key): return self.key_states.get(key, 0)

    def VkKeyScanW(self, _code): return self.virtual_key_result

    def SetWindowsHookExW(self, *arguments):
        self.hook_calls.append(arguments)
        return self.next_hook

    def CallNextHookEx(self, *arguments):
        self.hook_calls.append(arguments)
        return 71

    def GetMessageW(self, *_): return self.message_results.pop(0) if self.message_results else 0

    def TranslateMessage(self, *_): self.translate_calls += 1

    def DispatchMessageW(self, *_): self.dispatch_calls += 1

def test_keyboard_backend_sends_keys_unicode_and_tracks_state(monkeypatch):
    user32 = _KeyboardUser32()
    monkeypatch.setattr(keyboard_backend, "_user32", user32)
    keyboard_backend._send_key("not-a-key")
    monkeypatch.setattr(keyboard_backend, "_get_virtual_key_code", lambda _: (0x41, 7))
    keyboard_backend._send_key("A")
    keyboard_backend._send_key("A", key_released = True)
    assert user32.sent_inputs[:7] == [
        (keyboard_backend._SHIFT_VIRTUAL_KEY, 0, 0),
        (keyboard_backend._CONTROL_VIRTUAL_KEY, 0, 0),
        (keyboard_backend._ALT_VIRTUAL_KEY, 0, 0),
        (0x41, 0, 0),
        (0x41, 0, keyboard_backend._KEY_UP),
        (keyboard_backend._SHIFT_VIRTUAL_KEY, 0, keyboard_backend._KEY_UP),
        (keyboard_backend._CONTROL_VIRTUAL_KEY, 0, keyboard_backend._KEY_UP)
    ]
    assert user32.sent_inputs[7] == (keyboard_backend._ALT_VIRTUAL_KEY, 0, keyboard_backend._KEY_UP)
    user32.sent_inputs.clear()
    monkeypatch.setattr(keyboard_backend, "_get_virtual_key_code", lambda _: (0x41, 1))
    keyboard_backend._send_key("A")
    assert user32.sent_inputs == [
        (keyboard_backend._SHIFT_VIRTUAL_KEY, 0, 0),
        (0x41, 0, 0)
    ]
    user32.sent_inputs.clear()
    keyboard_backend._send_unicode("A😀")
    assert [(key, scan, flags) for key, scan, flags in user32.sent_inputs] == [
        (0, 0x41, keyboard_backend._UNICODE),
        (0, 0x41, keyboard_backend._UNICODE | keyboard_backend._KEY_UP),
        (0, 0xD83D, keyboard_backend._UNICODE),
        (0, 0xD83D, keyboard_backend._UNICODE | keyboard_backend._KEY_UP),
        (0, 0xDE00, keyboard_backend._UNICODE),
        (0, 0xDE00, keyboard_backend._UNICODE | keyboard_backend._KEY_UP)
    ]
    monkeypatch.undo()
    monkeypatch.setattr(keyboard_backend, "_user32", user32)
    user32.virtual_key_result = 0x0201
    assert keyboard_backend._get_virtual_key_code("SHIFT") == (keyboard_backend._SHIFT_VIRTUAL_KEY, 0)
    assert keyboard_backend._get_virtual_key_code("?") == (1, 2)
    user32.virtual_key_result = -1
    assert keyboard_backend._get_virtual_key_code("?") is None
    assert keyboard_backend._get_virtual_key_code("not-a-key") is None
    monkeypatch.setattr(
        keyboard_backend, "_get_virtual_key_code", lambda key: None if key == "bad" else (42, 0)
    )
    monkeypatch.setattr(keyboard_backend, "_key_states", {})
    assert keyboard_backend._is_pressed("bad") is False
    keyboard_backend._key_states[42] = True
    assert keyboard_backend._is_pressed("key") is True
    keyboard_backend._key_states[42] = False
    user32.key_states[42] = keyboard_backend._KEY_PRESSED
    assert keyboard_backend._is_pressed("key") is True
    user32.key_states[42] = 0
    assert keyboard_backend._is_pressed("key") is False

def test_keyboard_send_input_error_raises_winerror(monkeypatch):
    calls = []

    def fake_send_input(count, pointer, size):
        calls.append(True)
        return 1 if len(calls) == 1 else 0

    failing_user32 = SimpleNamespace(SendInput = fake_send_input, VkKeyScanW = lambda code: 0x41)
    monkeypatch.setattr(keyboard_backend, "_user32", failing_user32)
    monkeypatch.setattr(keyboard_backend.ctypes, "get_last_error", lambda: 5)
    with pytest.raises(OSError): keyboard_backend._send_unicode("a")
    monkeypatch.setattr(failing_user32, "SendInput", lambda count, pointer, size: 0)
    with pytest.raises(OSError): keyboard_backend._send_key("a")
    with pytest.raises(OSError): keyboard_backend._send_unicode("a")

def test_keyboard_backend_blocking_kill_switch_and_hook_lifecycle(monkeypatch):
    user32 = _KeyboardUser32()
    real_ensure_hook = keyboard_backend._ensure_hook
    monkeypatch.setattr(keyboard_backend, "_user32", user32)
    monkeypatch.setattr(keyboard_backend, "_blocked_keys", set())
    ensure_calls = []
    monkeypatch.setattr(keyboard_backend, "_ensure_hook", lambda: ensure_calls.append("ensure"))
    monkeypatch.setattr(
        keyboard_backend,
        "_get_virtual_key_code",
        lambda key: {"a": (65, 0), "ctrl": (17, 0), "bad": None}.get(key)
    )
    keyboard_backend._block_key("a")
    keyboard_backend._block_key("bad")
    keyboard_backend._unblock_key("a")
    keyboard_backend._unblock_key("a")
    keyboard_backend._unblock_key("bad")
    assert ensure_calls == ["ensure"]
    assert keyboard_backend._blocked_keys == set()
    monkeypatch.setattr(keyboard_backend, "_kill_switch_enabled", False)
    monkeypatch.setattr(keyboard_backend, "_kill_switch_key", 0)
    monkeypatch.setattr(keyboard_backend, "_kill_switch_modifiers", [])
    keyboard_backend._enable_kill_switch([])
    keyboard_backend._enable_kill_switch(["bad"])
    keyboard_backend._enable_kill_switch(["ctrl", "bad", "a"])
    assert keyboard_backend._kill_switch_enabled is True
    assert keyboard_backend._kill_switch_key == 65
    assert keyboard_backend._kill_switch_modifiers == [17]
    assert ensure_calls == ["ensure", "ensure"]
    keyboard_backend._disable_kill_switch()
    assert keyboard_backend._kill_switch_enabled is False

    class FakeEvent:
        def __init__(self):
            self.clear_calls = 0
            self.wait_calls = 0

        def clear(self): self.clear_calls += 1

        def wait(self): self.wait_calls += 1

        def set(self): pass

    class FakeThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon
            self.started = False

        def start(self): self.started = True

        def is_alive(self): return False

    event = FakeEvent()
    monkeypatch.setattr(keyboard_backend, "_ensure_hook", real_ensure_hook)
    monkeypatch.setattr(keyboard_backend, "_hook_ready_event", event)
    monkeypatch.setattr(keyboard_backend.threading, "Thread", FakeThread)
    monkeypatch.setattr(keyboard_backend, "_hook_thread", None)
    monkeypatch.setattr(keyboard_backend, "_hook_id", 100)
    keyboard_backend._ensure_hook()
    hook_thread = keyboard_backend._hook_thread
    assert isinstance(hook_thread, FakeThread)
    assert hook_thread.started is True
    assert (event.clear_calls, event.wait_calls) == (1, 1)
    monkeypatch.setattr(keyboard_backend, "_hook_thread", None)
    monkeypatch.setattr(keyboard_backend, "_hook_id", 0)
    monkeypatch.setattr(keyboard_backend, "_hook_error", 1460)
    with pytest.raises(OSError, match = "Failed to install low-level keyboard hook") as exc_info:
        keyboard_backend._ensure_hook()
    assert exc_info.value.args[0] == 1460

    class LiveThread:
        def is_alive(self): return True

    monkeypatch.setattr(keyboard_backend, "_hook_thread", LiveThread())
    keyboard_backend._ensure_hook()
    assert (event.clear_calls, event.wait_calls) == (2, 2)

def test_keyboard_hook_worker_records_error_when_installation_fails(monkeypatch):
    user32 = SimpleNamespace(SetWindowsHookExW = lambda *args: 0)
    fake_event = SimpleNamespace(set = lambda: None)
    monkeypatch.setattr(keyboard_backend, "_user32", user32)
    monkeypatch.setattr(keyboard_backend, "_HookProcedure", lambda function: function)
    monkeypatch.setattr(keyboard_backend, "_hook_ready_event", fake_event)
    monkeypatch.setattr(keyboard_backend.ctypes, "get_last_error", lambda: 1234)
    keyboard_backend._hook_error = 0
    keyboard_backend._hook_id = None
    keyboard_backend._hook_worker()
    assert keyboard_backend._hook_id == 0
    assert keyboard_backend._hook_error == 1234

def test_keyboard_hook_worker_handles_down_up_blocked_and_kill_switch_events(monkeypatch):
    user32 = _KeyboardUser32()
    user32.message_results = [1, 0]
    fake_event = SimpleNamespace(set = lambda: None)
    triggered = []
    monkeypatch.setattr(keyboard_backend, "_user32", user32)
    monkeypatch.setattr(keyboard_backend, "_HookProcedure", lambda function: function)
    monkeypatch.setattr(keyboard_backend, "_hook_ready_event", fake_event)
    monkeypatch.setattr(keyboard_backend, "_hook_id", None)
    monkeypatch.setattr(keyboard_backend, "_key_states", {})
    monkeypatch.setattr(keyboard_backend, "_blocked_keys", {8})
    monkeypatch.setattr(keyboard_backend, "_kill_switch_enabled", False)
    monkeypatch.setattr(keyboard_backend, "_kill_switch_key", 9)
    monkeypatch.setattr(keyboard_backend, "_kill_switch_modifiers", [17])
    monkeypatch.setattr(keyboard_backend, "trigger_kill_switch", lambda: triggered.append(True))
    keyboard_backend._hook_worker()
    handler = keyboard_backend._hook_function
    assert handler is not None

    def invoke(hook_code, message, virtual_key, flags = 0):
        hook = keyboard_backend._KeyboardHookStruct(virtual_key_code = virtual_key, flags = flags)
        return handler(hook_code, message, ctypes.byref(hook))

    assert invoke(-1, keyboard_backend._WINDOW_MESSAGE_KEY_DOWN, 1) == 71
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_KEY_DOWN, 7) == 71
    assert keyboard_backend._key_states[7] is True
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_SYSTEM_KEY_UP, 7) == 71
    assert keyboard_backend._key_states[7] is False
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_KEY_DOWN, 8) == 1
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_KEY_DOWN, 8, keyboard_backend._INJECTED) == 71
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_KEY_UP, 8) == 1
    assert invoke(0, 0, 7) == 71
    monkeypatch.setattr(keyboard_backend, "_kill_switch_enabled", True)
    keyboard_backend._key_states[17] = True
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_SYSTEM_KEY_DOWN, 9) == 1
    assert triggered == [True]
    keyboard_backend._key_states[17] = False
    user32.key_states[17] = 0
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_KEY_DOWN, 9) == 71
    user32.key_states[17] = keyboard_backend._KEY_PRESSED
    assert invoke(0, keyboard_backend._WINDOW_MESSAGE_KEY_DOWN, 9) == 1
    assert triggered == [True, True]
    assert user32.translate_calls == 1
    assert user32.dispatch_calls == 1

def test_uninstalling_idle_keyboard_hook_joins_its_worker_thread(monkeypatch):
    class ThreadWithNativeId:
        def __init__(self):
            self.native_id = 1234
            self.joined = False

        def is_alive(self): return True

        def join(self, timeout = None): self.joined = True

    unhook_calls = []
    user32 = SimpleNamespace(
        UnhookWindowsHookEx = lambda hook_id: unhook_calls.append(("unhook", hook_id)) or True,
        PostThreadMessageW = lambda thread_id, message, wparam, lparam: (
            unhook_calls.append(("post", thread_id, message)) or True
        )
    )
    fake_thread = ThreadWithNativeId()
    monkeypatch.setattr(keyboard_backend, "_user32", user32)
    monkeypatch.setattr(keyboard_backend, "_hook_id", 42)
    monkeypatch.setattr(keyboard_backend, "_hook_thread", fake_thread)
    monkeypatch.setattr(keyboard_backend, "_hook_function", "func")
    monkeypatch.setattr(keyboard_backend, "_blocked_keys", set())
    monkeypatch.setattr(keyboard_backend, "_kill_switch_enabled", False)
    monkeypatch.setattr(keyboard_backend, "_key_states", {65: True})
    keyboard_backend._unhook_if_idle()
    assert unhook_calls == [("unhook", 42), ("post", 1234, 0x0012)]
    assert fake_thread.joined is True
    assert keyboard_backend._hook_id is None
    assert keyboard_backend._hook_thread is None
    assert keyboard_backend._hook_function is None
    assert keyboard_backend._key_states == {}

def test_uninstalling_idle_keyboard_hook_without_a_worker_thread(monkeypatch):
    unhook_calls = []
    monkeypatch.setattr(
        keyboard_backend,
        "_user32",
        SimpleNamespace(UnhookWindowsHookEx = lambda hook_id: unhook_calls.append(hook_id))
    )
    monkeypatch.setattr(keyboard_backend, "_hook_id", 99)
    monkeypatch.setattr(keyboard_backend, "_hook_thread", None)
    monkeypatch.setattr(keyboard_backend, "_hook_function", "func")
    monkeypatch.setattr(keyboard_backend, "_blocked_keys", set())
    monkeypatch.setattr(keyboard_backend, "_kill_switch_enabled", False)
    keyboard_backend._unhook_if_idle()
    assert unhook_calls == [99]
    assert keyboard_backend._hook_id is None
    assert keyboard_backend._hook_function is None

def test_failed_keyboard_hook_installation_does_not_start_message_loop(monkeypatch):
    user32 = _KeyboardUser32()
    user32.next_hook = 0
    ready_event = threading.Event()
    monkeypatch.setattr(keyboard_backend, "_user32", user32)
    monkeypatch.setattr(keyboard_backend, "_hook_ready_event", ready_event)
    monkeypatch.setattr(keyboard_backend, "_HookProcedure", lambda function: function)
    monkeypatch.setattr(keyboard_backend, "_hook_id", None)
    keyboard_backend._hook_worker()
    assert keyboard_backend._hook_id == 0
    assert ready_event.is_set()
    assert user32.translate_calls == 0
    assert user32.dispatch_calls == 0

class _Capture:
    def __init__(self, monitors, screenshot = None):
        self.monitors = monitors
        self.screenshot = screenshot if screenshot is not None else object()
        self.grabs = []

    def __enter__(self): return self

    def __exit__(self, *_): return False

    def grab(self, screen):
        self.grabs.append(screen)
        return self.screenshot

def test_screen_backend_reads_pixels_work_areas_and_screenshots(monkeypatch):
    capture = _Capture([
        {"left": -10, "top": 20, "width": 100, "height": 50},
        {"left": 100, "top": 200, "width": 800, "height": 600}
    ])
    calls = []

    def set_work_area(_, __, pointer, ___):
        rectangle = ctypes.cast(pointer, ctypes.POINTER(screen_backend.ctypes.wintypes.RECT)).contents
        rectangle.left, rectangle.top, rectangle.right, rectangle.bottom = (1, 2, 30, 40)

    user32 = SimpleNamespace(
        GetDC = lambda window: calls.append(("get_dc", window)) or 88,
        ReleaseDC = lambda window, context: calls.append(("release_dc", window, context)),
        SystemParametersInfoW = set_work_area
    )
    gdi32 = SimpleNamespace(GetPixel = lambda context, x, y: 0x0032140A)
    monkeypatch.setattr(screen_backend, "mss", SimpleNamespace(MSS = lambda: capture))
    monkeypatch.setattr(screen_backend, "_user32", user32)
    monkeypatch.setattr(screen_backend, "_gdi32", gdi32)
    assert screen_backend._get_screen_resolution() == (800, 600)
    assert screen_backend._get_pixel_color(0, 20) == (10, 20, 50)
    with pytest.raises(ValueError): screen_backend._get_pixel_color(-11, 20)
    with pytest.raises(ValueError): screen_backend._get_pixel_color(0, 70)
    assert screen_backend._get_work_area() == (1, 2, 30, 40)
    assert calls == [("get_dc", 0), ("release_dc", 0, 88)]
    screenshot = screen_backend._take_screenshot(monitor_index = 1)
    assert screenshot is capture.screenshot
    assert capture.grabs[-1] == capture.monitors[1]
    screen_backend._take_screenshot(region = (1.2, 2.8, 10.9, 20.1))
    assert capture.grabs[-1] == {"left": 1, "top": 2, "width": 9, "height": 17}
    image_writes = []
    fake_numpy = SimpleNamespace(array = lambda value: "bgra")
    fake_cv2 = SimpleNamespace(
        COLOR_BGRA2BGR = 4,
        cvtColor = lambda image, conversion: f"bgr:{image}:{conversion}",
        imwrite = lambda path, image: image_writes.append((path, image))
    )
    monkeypatch.setattr(screen_backend, "numpy", fake_numpy)
    monkeypatch.setattr(screen_backend, "cv2", fake_cv2)
    assert screen_backend._take_screenshot(save_path = "screen.png") is capture.screenshot
    assert image_writes == [("screen.png", "bgr:bgra:4")]

def test_screen_backend_adjusts_coordinates_and_locates_image_without_real_files(monkeypatch):
    capture = _Capture([
        {"left": 0, "top": 0, "width": 1, "height": 1},
        {"left": 100, "top": 200, "width": 1, "height": 1}
    ])
    monkeypatch.setattr(screen_backend, "mss", SimpleNamespace(MSS = lambda: capture))
    assert screen_backend._adjust_coordinates_for_region(1.9, 2.1, (10, 20, 30, 40)) == (11, 22)
    assert screen_backend._adjust_coordinates_for_region(1.9, 2.1, None, 1) == (101, 202)
    assert screen_backend._adjust_coordinates_for_region(1.9, 2.1, None) == (1, 2)
    template = numpy.zeros((4, 6, 3), dtype = numpy.uint8)
    result = numpy.array([[0.95, 0.91], [0.99, 0.92]])
    maximum = {"value": 0.95}
    fake_cv2 = SimpleNamespace(
        IMREAD_COLOR = 1,
        COLOR_BGRA2BGR = 2,
        TM_CCOEFF_NORMED = 3,
        imdecode = lambda image, flag: template,
        cvtColor = lambda image, flag: image,
        matchTemplate = lambda image, matched_template, algorithm: result,
        minMaxLoc = lambda matched_result: (0, maximum["value"], (0, 0), (3, 5))
    )
    monkeypatch.setattr(screen_backend, "numpy", numpy)
    monkeypatch.setattr(screen_backend, "cv2", fake_cv2)
    monkeypatch.setattr(
        screen_backend, "open", lambda *_: io.BytesIO(b"not a real png"), raising = False
    )
    monkeypatch.setattr(screen_backend, "_take_screenshot", lambda *_: object())
    monkeypatch.setattr(
        screen_backend,
        "_adjust_coordinates_for_region",
        lambda x, y, region, monitor: (int(x), int(y))
    )
    assert screen_backend._locate_image("ignored.png", 0.9, 1, None, 0) == (6, 7)
    maximum["value"] = 0.89
    assert screen_backend._locate_image("ignored.png", 0.9, 1, None, 0) == (None, None)
    assert screen_backend._locate_image("ignored.png", 0.9, 2, None, 0) == [(3, 2), (4, 2)]
    assert screen_backend._locate_image("ignored.png", 0.9, 0, None, 0) == [
        (3, 2), (4, 2), (3, 3), (4, 3)
    ]
    monkeypatch.setattr(screen_backend.cv2, "imdecode", lambda *_: None)
    with pytest.raises(ValueError, match = "Failed to read image"):
        screen_backend._locate_image("ignored.png", 0.9, 1, None, 0)

def test_screen_backend_runs_ocr_with_fake_winrt_objects(monkeypatch):
    screenshot = SimpleNamespace(width = 2, height = 3)
    copied_buffers = []
    written_bytes = []
    result = object()

    class FakeBitmap:
        def __init__(self, *arguments): self.arguments = arguments

        def copy_from_buffer(self, buffer): copied_buffers.append(buffer)

    class FakeWriter:
        def write_bytes(self, data): written_bytes.append(data)

        def detach_buffer(self): return "buffer"

    class FakeImage:
        def tobytes(self): return b"pixels"

    class FakeEngine:
        async def recognize_async(self, bitmap):
            assert isinstance(bitmap, FakeBitmap)
            return result

    engine = FakeEngine()
    fake_numpy = SimpleNamespace(uint8 = object(), array = lambda *_, **__: FakeImage())
    monkeypatch.setattr(screen_backend, "numpy", fake_numpy)
    monkeypatch.setattr(screen_backend, "_take_screenshot", lambda *_: screenshot)
    monkeypatch.setattr(screen_backend, "SoftwareBitmap", FakeBitmap)
    monkeypatch.setattr(screen_backend, "BitmapPixelFormat", SimpleNamespace(BGRA8 = "bgra8"))
    monkeypatch.setattr(
        screen_backend, "BitmapAlphaMode", SimpleNamespace(PREMULTIPLIED = "premultiplied")
    )
    monkeypatch.setattr(screen_backend, "DataWriter", FakeWriter)
    monkeypatch.setattr(
        screen_backend,
        "OcrEngine",
        SimpleNamespace(try_create_from_user_profile_languages = lambda: engine)
    )
    assert screen_backend._run_ocr_on_region((0, 0, 1, 1), 0) is result
    assert written_bytes == [b"pixels"]
    assert copied_buffers == ["buffer"]
    monkeypatch.setattr(
        screen_backend,
        "OcrEngine",
        SimpleNamespace(try_create_from_user_profile_languages = lambda: None)
    )
    with pytest.raises(SystemError, match = "OCR engine"): screen_backend._run_ocr_on_region()

class _FakeWinMM:
    def __init__(self, open_error = False):
        self.commands = []
        self.open_error = open_error

    def mciSendStringW(self, command, *_):
        self.commands.append(command)
        return int(self.open_error and command.startswith("open "))

def test_sound_backend_uses_safe_win32_commands_and_reports_open_errors(monkeypatch):
    beeps = []
    system_sounds = []
    winsound = SimpleNamespace(
        MB_ICONASTERISK = 1,
        MB_ICONEXCLAMATION = 2,
        MB_ICONHAND = 3,
        MB_ICONQUESTION = 4,
        MB_OK = 5,
        Beep = lambda frequency, duration: beeps.append((frequency, duration)),
        MessageBeep = lambda flag: system_sounds.append(flag)
    )
    winmm = _FakeWinMM()
    process_calls = []
    fake_subprocess = SimpleNamespace(
        CREATE_NO_WINDOW = 73,
        run = lambda arguments, **kwargs: process_calls.append((arguments, kwargs))
    )
    monkeypatch.setattr(sound_backend, "winsound", winsound)
    monkeypatch.setattr(sound_backend, "_winmm", winmm)
    monkeypatch.setattr(sound_backend, "subprocess", fake_subprocess)
    sound_backend._play_beep_sound(440, 0.125)
    sound_backend._play_system_sound("WARNING")
    sound_backend._play_system_sound("not-a-system-sound")
    sound_backend._play_audio("C:/music/test.wav")
    sound_backend._speak("Ada's test")
    assert beeps == [(440, 125)]
    assert system_sounds == [winsound.MB_ICONEXCLAMATION, winsound.MB_OK]
    assert winmm.commands == [
        "close audio",
        "open \"C:/music/test.wav\" alias audio",
        "play audio wait",
        "close audio"
    ]
    encoded = process_calls[0][0][-1]
    decoded = base64.b64decode(encoded).decode("utf-16-le")
    assert "Speak('Ada''s test')" in decoded
    assert process_calls[0][1] == {"creationflags": 73}
    failing_winmm = _FakeWinMM(open_error = True)
    monkeypatch.setattr(sound_backend, "_winmm", failing_winmm)
    with pytest.raises(RuntimeError, match = "Could not play"):
        sound_backend._play_audio("C:/music/unreadable.wav")
    assert failing_winmm.commands == ["close audio", "open \"C:/music/unreadable.wav\" alias audio"]

class _FakeSystemUser32:
    def __init__(self, kernel32):
        self.kernel32 = kernel32
        self.windows = {
            1: ("near match", True), 2: ("wanted", True), 3: ("wanted", False), 4: ("", True)
        }
        self.active_window = 2
        self.clipboard_handle = 0
        self.clipboard_open = False
        self.open_clipboard_results = [True]
        self.create_window_result = 99
        self.empty_clipboard_result = True
        self.set_clipboard_result = True
        self.enum_windows_result = True
        self.foreground_result = True
        self.window_position_result = True
        self.post_message_result = True
        self.calls = []

    def CreateWindowExW(self, *arguments):
        self.calls.append(("create_window", arguments))
        return self.create_window_result

    def DestroyWindow(self, window_handle):
        self.calls.append(("destroy_window", window_handle))
        return True

    def OpenClipboard(self, owner_window):
        self.calls.append(("open_clipboard", owner_window))
        result = self.open_clipboard_results.pop(0) if self.open_clipboard_results else True
        self.clipboard_open = result
        return result

    def CloseClipboard(self):
        self.calls.append(("close_clipboard",))
        self.clipboard_open = False
        return True

    def EmptyClipboard(self):
        self.calls.append(("empty_clipboard",))
        self.clipboard_handle = 0
        return self.empty_clipboard_result

    def GetClipboardData(self, clipboard_format):
        self.calls.append(("get_clipboard_data", clipboard_format))
        return self.clipboard_handle

    def SetClipboardData(self, clipboard_format, memory_handle):
        self.calls.append(("set_clipboard_data", clipboard_format, memory_handle))
        if not self.set_clipboard_result: return 0
        self.clipboard_handle = memory_handle
        return memory_handle

    def EnumWindows(self, callback, parameter):
        for window_handle in self.windows:
            if not callback(window_handle, parameter): return False
        return self.enum_windows_result

    def GetWindowTextLengthW(self, window_handle):
        return len(self.windows[window_handle][0])

    def GetWindowTextW(self, window_handle, buffer, buffer_size):
        buffer.value = self.windows[window_handle][0]
        return len(buffer.value)

    def IsWindowVisible(self, window_handle): return self.windows[window_handle][1]

    def GetForegroundWindow(self): return self.active_window

    def SetForegroundWindow(self, window_handle):
        self.calls.append(("focus_window", window_handle))
        return self.foreground_result

    def SetWindowPos(self, window_handle, insert_after, x, y, width, height, flags):
        self.calls.append(("set_window_position", window_handle, x, y, width, height, flags))
        return self.window_position_result

    def PostMessageW(self, window_handle, message, word_parameter, long_parameter):
        self.calls.append(("post_message", window_handle, message, word_parameter, long_parameter))
        return self.post_message_result

class _FakeSystemKernel32:
    def __init__(self):
        self.memory = {}
        self.freed_handles = []
        self.next_handle = 100
        self.fail_allocation = False
        self.fail_lock = False

    def GlobalAlloc(self, flags, size):
        if self.fail_allocation: return 0
        self.next_handle += 1
        self.memory[self.next_handle] = ctypes.create_string_buffer(size)
        return self.next_handle

    def GlobalLock(self, handle):
        if self.fail_lock or handle not in self.memory: return 0
        return ctypes.addressof(self.memory[handle])

    def GlobalUnlock(self, handle): return 0

    def GlobalFree(self, handle):
        self.freed_handles.append(handle)
        self.memory.pop(handle, None)
        return 0

    def store_text(self, text):
        self.next_handle += 1
        self.memory[self.next_handle] = ctypes.create_unicode_buffer(text)
        return self.next_handle

def _install_fake_system_apis(monkeypatch):
    kernel32 = _FakeSystemKernel32()
    user32 = _FakeSystemUser32(kernel32)
    monkeypatch.setattr(system_backend, "_kernel32", kernel32)
    monkeypatch.setattr(system_backend, "_user32", user32)
    return user32, kernel32

def test_system_backend_retries_opening_a_busy_clipboard(monkeypatch):
    user32, kernel32 = _install_fake_system_apis(monkeypatch)
    user32.open_clipboard_results = [False, True]
    user32.clipboard_handle = kernel32.store_text("available")
    monkeypatch.setattr(system_backend.time, "sleep", lambda duration: None)
    assert system_backend._get_clipboard_text() == "available"
    assert [call[0] for call in user32.calls].count("open_clipboard") == 2

def test_system_backend_returns_empty_text_when_clipboard_has_no_unicode_data(monkeypatch):
    user32, _ = _install_fake_system_apis(monkeypatch)
    assert system_backend._get_clipboard_text() == ""
    assert user32.clipboard_open is False

def test_system_backend_clipboard_read_error_closes_clipboard(monkeypatch):
    user32, kernel32 = _install_fake_system_apis(monkeypatch)
    user32.clipboard_handle = kernel32.store_text("unreadable")
    kernel32.fail_lock = True
    with pytest.raises(OSError, match = "read text"): system_backend._get_clipboard_text()
    assert user32.clipboard_open is False

def test_system_backend_reads_and_writes_unicode_clipboard_text(monkeypatch):
    user32, kernel32 = _install_fake_system_apis(monkeypatch)
    user32.clipboard_handle = kernel32.store_text("initial 日本語")
    assert system_backend._get_clipboard_text() == "initial 日本語"
    assert user32.clipboard_open is False
    system_backend._set_clipboard_text("changed 😀")
    assert system_backend._get_clipboard_text() == "changed 😀"
    system_backend._set_clipboard_text("")
    assert system_backend._get_clipboard_text() == ""
    assert user32.clipboard_open is False
    assert len([call for call in user32.calls if call[0] == "create_window"]) == 2
    assert len([call for call in user32.calls if call[0] == "destroy_window"]) == 2

@pytest.mark.parametrize(
    "failure, message",
    [
        ("create_window", "owner window"),
        ("open_clipboard", "open"),
        ("empty_clipboard", "empty"),
        ("allocate", "allocate"),
        ("lock", "lock"),
        ("set_data", "set text")
    ]
)
def test_system_backend_clipboard_write_errors_release_owned_resources(monkeypatch, failure, message):
    user32, kernel32 = _install_fake_system_apis(monkeypatch)
    match failure:
        case "create_window": user32.create_window_result = 0
        case "open_clipboard":
            user32.open_clipboard_results = [False]
            monkeypatch.setattr(system_backend, "_CLIPBOARD_OPEN_TIMEOUT", 0)
        case "empty_clipboard": user32.empty_clipboard_result = False
        case "allocate": kernel32.fail_allocation = True
        case "lock": kernel32.fail_lock = True
        case "set_data": user32.set_clipboard_result = False
    with pytest.raises(OSError, match = message):
        system_backend._set_clipboard_text("text")
    assert user32.clipboard_open is False
    assert len([call for call in user32.calls if call[0] == "destroy_window"]) == (
        0 if failure == "create_window" else 1
    )
    if failure in {"lock", "set_data"}: assert len(kernel32.freed_handles) == 1

def test_system_window_operations_call_ensure_dpi_aware(monkeypatch):
    dpi_calls = []
    monkeypatch.setattr(system_backend, "_ensure_dpi_aware", lambda: dpi_calls.append("dpi"))
    monkeypatch.setattr(system_backend, "_find_window", lambda title: 1234)
    monkeypatch.setattr(system_backend._user32, "SetWindowPos", lambda *args: 1)
    system_backend._resize_window("title", 800, 600)
    system_backend._move_window("title", 100, 200)
    assert dpi_calls == ["dpi", "dpi"]

def test_system_backend_finds_and_operates_on_exact_visible_window_titles(monkeypatch):
    user32, _ = _install_fake_system_apis(monkeypatch)
    assert system_backend._get_active_window_title() == "wanted"
    user32.active_window = 0
    assert system_backend._get_active_window_title() == ""
    system_backend._focus_window("wanted")
    system_backend._resize_window("wanted", 11.8, 12.2)
    system_backend._move_window("wanted", -3.8, 4.8)
    system_backend._close_window("wanted")
    assert user32.calls == [
        ("focus_window", 2),
        ("set_window_position", 2, 0, 0, 11, 12, system_backend._SWP_NOMOVE),
        ("set_window_position", 2, -3, 4, 0, 0, system_backend._SWP_NOSIZE),
        ("post_message", 2, system_backend._WM_CLOSE, 0, 0)
    ]

def test_system_backend_reports_missing_or_unavailable_windows(monkeypatch):
    user32, _ = _install_fake_system_apis(monkeypatch)
    with pytest.raises(WindowNotFoundError): system_backend._focus_window("Wanted")
    user32.enum_windows_result = False
    with pytest.raises(OSError, match = "enumerate"): system_backend._resize_window("absent", 1, 2)

@pytest.mark.parametrize(
    "operation, result_attribute, message",
    [
        (lambda: system_backend._focus_window("wanted"), "foreground_result", "focus"),
        (lambda: system_backend._resize_window("wanted", 1, 2), "window_position_result", "resize"),
        (lambda: system_backend._move_window("wanted", 1, 2), "window_position_result", "move"),
        (lambda: system_backend._close_window("wanted"), "post_message_result", "close")
    ]
)
def test_system_backend_reports_failed_window_operations(
    monkeypatch, operation, result_attribute, message
):
    user32, _ = _install_fake_system_apis(monkeypatch)
    setattr(user32, result_attribute, False)
    with pytest.raises(OSError, match = message): operation()

class _Process:
    def __init__(self, name = None, error = None):
        self.name = name
        self.error = error
        self.calls = []

    @property
    def info(self):
        if self.error is not None: raise self.error
        return {"name": self.name}

    def kill(self): self.calls.append("kill")

    def terminate(self): self.calls.append("terminate")

def test_system_backend_handles_processes_clipboard_windows_and_launches(monkeypatch):
    class NoSuchProcess(Exception): pass

    class AccessDenied(Exception): pass

    class ZombieProcess(Exception): pass

    processes = []
    fake_psutil = SimpleNamespace(
        NoSuchProcess = NoSuchProcess,
        AccessDenied = AccessDenied,
        ZombieProcess = ZombieProcess,
        process_iter = lambda attributes: processes
    )
    monkeypatch.setattr(system_backend, "psutil", fake_psutil)
    matching = _Process("NOTEPAD.EXE")
    processes[:] = [_Process(None), _Process("else.exe"), _Process(error = NoSuchProcess()), matching]
    assert system_backend._is_process_running("notepad.exe") is True
    processes[:] = [_Process(None), _Process("else.exe"), _Process(error = AccessDenied())]
    assert system_backend._is_process_running("notepad.exe") is False
    matching.calls.clear()
    processes[:] = [_Process(error = ZombieProcess()), matching, _Process("else-after-match.exe")]
    system_backend._kill_process("notepad.exe", force = True)
    system_backend._kill_process("notepad.exe", force = False)
    assert matching.calls == ["kill", "terminate"]
    launches = []
    started = []
    current_path = {"which": None, "is_file": True}
    fake_subprocess = SimpleNamespace(
        Popen = lambda arguments, **kwargs: launches.append((arguments, kwargs))
    )
    monkeypatch.setattr(system_backend, "subprocess", fake_subprocess)
    monkeypatch.setattr(system_backend.shutil, "which", lambda _: current_path["which"])
    monkeypatch.setattr(system_backend.os.path, "abspath", lambda path: f"absolute/{path}")
    monkeypatch.setattr(system_backend.os.path, "isfile", lambda _: current_path["is_file"])
    monkeypatch.setattr(system_backend.os.path, "dirname", lambda path: f"parent/{path}")
    monkeypatch.setattr(system_backend.os, "startfile", lambda path: started.append(path))
    current_path.update(which = "found.EXE", is_file = True)
    system_backend._open_file("tool")
    current_path.update(which = None, is_file = True)
    system_backend._open_file("program.com")
    system_backend._open_file("script.bat")
    system_backend._open_file("script.cmd")
    current_path.update(is_file = False)
    system_backend._open_file("document.txt")
    assert launches == [
        (["found.EXE"], {"cwd": "parent/found.EXE"}),
        (["absolute/program.com"], {"cwd": "parent/absolute/program.com"}),
        (["cmd.exe", "/d", "/c", "absolute/script.bat"], {"cwd": "parent/absolute/script.bat"}),
        (["cmd.exe", "/d", "/c", "absolute/script.cmd"], {"cwd": "parent/absolute/script.cmd"})
    ]
    assert started == ["document.txt"]

def test_system_backend_power_operations_delegate_to_the_expected_windows_api(monkeypatch):
    calls = []
    user32 = SimpleNamespace(LockWorkStation = lambda: calls.append(("lock",)))
    powrprof = SimpleNamespace(
        SetSuspendState = lambda *arguments: calls.append(("sleep", *arguments))
    )
    subprocess_calls = []
    fake_subprocess = SimpleNamespace(
        CREATE_NO_WINDOW = 91,
        run = lambda arguments, **kwargs: subprocess_calls.append((arguments, kwargs))
    )
    monkeypatch.setattr(system_backend, "_user32", user32)
    monkeypatch.setattr(system_backend, "_powrprof", powrprof)
    monkeypatch.setattr(system_backend, "subprocess", fake_subprocess)
    system_backend._lock_screen()
    system_backend._sleep()
    system_backend._sign_out()
    system_backend._hibernate()
    system_backend._shutdown(12)
    system_backend._restart(34)
    assert calls == [("lock",), ("sleep", False, True, False)]
    assert subprocess_calls == [
        (["shutdown", "/l"], {"creationflags": 91}),
        (["shutdown", "/h"], {"creationflags": 91}),
        (["shutdown", "/s", "/t", "12"], {"creationflags": 91}),
        (["shutdown", "/r", "/t", "34"], {"creationflags": 91})
    ]