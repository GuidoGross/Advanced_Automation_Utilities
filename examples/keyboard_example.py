import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory in sys.path: sys.path.remove(script_directory)
parent_directory = os.path.dirname(script_directory)
if parent_directory not in sys.path: sys.path.insert(0, parent_directory)

from examples.examples_utilities import start_stop_script
from advanced_automation_utilities import Keyboard, KeyboardInfo, KEYBOARD_NORMAL
from tui_utilities import (
    set_window_title, maximize_window, menu, confirm_exit, print, header, wait_for_key
)

def main():
    set_window_title("Keyboard Test")
    maximize_window()
    while True:
        selection = menu(
            title = "Keyboard Test",
            options = {
                "1": "Press key",
                "2": "Hold and release key",
                "3": "Execute hotkey",
                "4": "Write text",
                "5": "Check if a key is pressed",
                "E": "Exit"
            }
        )
        match selection:
            case "1": test_press_key()
            case "2": test_hold_and_release_key()
            case "3": test_hotkey()
            case "4": test_write()
            case "5": test_is_key_pressed()
            case "E": confirm_exit()

def test_press_key():
    def press_key():
        keyboard_physics = KEYBOARD_NORMAL
        keyboard = Keyboard(keyboard_physics)
        keyboard.press_key("a")

    start_stop_script(press_key, "Press key")

def test_hold_and_release_key():
    def hold_key():
        keyboard_physics = KEYBOARD_NORMAL
        keyboard = Keyboard(keyboard_physics)
        keyboard.hold_key("a")
        keyboard.release_key("a")

    start_stop_script(hold_key, "Hold and release key")

def test_hotkey():
    def hotkey():
        keyboard_physics = KEYBOARD_NORMAL
        keyboard = Keyboard(keyboard_physics)
        keyboard.hotkey("ctrl", "c")

    start_stop_script(hotkey, "Execute hotkey")

def test_write():
    def write():
        keyboard_physics = KEYBOARD_NORMAL
        keyboard = Keyboard(keyboard_physics)
        keyboard.write("By writing this text, very advanced simulated errors will be generated.")

    start_stop_script(write, "Write text")

def test_is_key_pressed():
    def is_key_pressed():
        keyboard_info = KeyboardInfo()
        header("Is \"space\" key pressed?")
        is_pressed = keyboard_info.is_pressed("space")
        print([
            ("The \"space\" key ", {}),
            (
                f"{"is" if is_pressed else "is not"}",
                {"color": f"{"#00ff00" if is_pressed else "#ff0000"}"}
            ),
            (" pressed", {})
        ], alignment = "center")
        wait_for_key()

    start_stop_script(is_key_pressed, "Check if a key is pressed")

if __name__ == "__main__": main()