import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory in sys.path: sys.path.remove(script_directory)
parent_directory = os.path.dirname(script_directory)
if parent_directory not in sys.path: sys.path.insert(0, parent_directory)

from examples.examples_utilities import start_stop_script
from advanced_automation_utilities import Timing, System, SystemInfo, KillSwitchTriggered
from tui_utilities import (
    set_window_title,
    maximize_window,
    menu,
    confirm_exit,
    header,
    print,
    wait_for_key,
    success_message,
    error_message
)

def main():
    set_window_title("System Test")
    maximize_window()
    while True:
        selection = menu(
            title = "System Test",
            options = {
                "1": "Get clipboard text and modify it",
                "2": "Get active window title",
                "3": "Process and window management",
                "4": "Lock the screen",
                "5": "Sign out",
                "6": "Sleep the device",
                "7": "Hibernate the device",
                "8": "Shutdown the device",
                "9": "Restart the device",
                "10": "Test Kill Switch",
                "E": "Exit"
            }
        )
        match selection:
            case "1": test_get_clipboard_text_and_modify_it()
            case "2": test_get_active_window_title()
            case "3": test_process_and_window_management()
            case "4": test_screen_lock()
            case "5": test_sign_out()
            case "6": test_sleep()
            case "7": test_hibernate()
            case "8": test_shutdown()
            case "9": test_restart()
            case "10": test_kill_switch()
            case "E": confirm_exit()

def test_get_clipboard_text_and_modify_it():
    system = System()
    system_info = SystemInfo()
    header("Current clipboard text")
    print([
        ("Current clipboard text:", {"bold": True}),
        (f" {system_info.clipboard_text}", {"color": "#00bfff"})
    ])
    wait_for_key()
    header("Overwritten clipboard text")
    system.set_clipboard_text("Hello, world!")
    print([
        ("Clipboard has been overwritten with:", {"bold": True}),
        (f" {system_info.clipboard_text}", {"color": "#00bfff"})
    ])
    wait_for_key()

def test_get_active_window_title():
    def get_active_window_title():
        system_info = SystemInfo()
        header("Active window title")
        title = system_info.active_window_title
        print([("Currently focused window is: ", {"bold": True}), (f"{title}", {"color": "#00bfff"})])
        wait_for_key()

    start_stop_script(get_active_window_title, "Get active window title")

def test_process_and_window_management():
    system = System()
    system_info = SystemInfo()
    timing = Timing()
    header("Process and window management")
    process_name = "notepad.exe"
    print([("Opening ", {}), (f"{process_name}", {"color": "#00bfff"})], alignment = "center")
    try:
        system.open_process(process_name)
        success_message(f"{process_name.capitalize()} opened successfully.")
        timing.wait(1)
        window_title = system_info.active_window_title
        system.resize_window(window_title, 500, 500)
        system.move_window(window_title, 100, 100)
        success_message(f"Moved and resized {process_name}")
        wait_for_key()
    except Exception as error: error_message(f"Error opening or manipulating {process_name}: {error}")
    print([("Closing ", {}), (f"{process_name}", {"color": "#00bfff"})], alignment = "center")
    try:
        system.kill_process(process_name, force = True)
        success_message(f"{process_name.capitalize()} closed successfully.")
    except Exception as error: error_message(f"Error closing {process_name}: {error}")

def test_screen_lock():
    system = System()
    header("Lock screen")
    print("Locking screen...", alignment = "center")
    system.lock_screen()

def test_sign_out():
    system = System()
    header("Sign out")
    print("Signing out...", alignment = "center")
    system.sign_out()

def test_sleep():
    system = System()
    header("Sleep the device")
    print("Sleeping the device...", alignment = "center")
    system.sleep()

def test_hibernate():
    system = System()
    header("Hibernate the device")
    print("Hibernating the device...", alignment = "center")
    system.hibernate()

def test_shutdown():
    system = System()
    header("Shutdown the device")
    print("Shutting down the device...", alignment = "center")
    system.shutdown(delay = 15)

def test_restart():
    system = System()
    header("Restart the device")
    print("Restarting the device...", alignment = "center")
    system.restart(delay = 15)

def test_kill_switch():
    timing = Timing()
    system = System()
    header("Test Kill Switch")
    system.enable_kill_switch()
    print([
        ("Kill Switch is enabled. Press ", {}),
        ("Ctrl + Shift + Alt + K", {"color": "#00bfff"}),
        (" to abort, or wait 10 seconds for the test to end normally...", {})
    ], alignment = "center")
    try:
        timing.wait(10)
        system.disable_kill_switch()
        success_message("Test completed without using Kill Switch")
    except KillSwitchTriggered: error_message("Test aborted")
    finally: system.disable_kill_switch()

if __name__ == "__main__": main()