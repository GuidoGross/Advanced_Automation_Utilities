import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory in sys.path: sys.path.remove(script_directory)
parent_directory = os.path.dirname(script_directory)
if parent_directory not in sys.path: sys.path.insert(0, parent_directory)

from examples.examples_utilities import start_stop_script
from advanced_automation_utilities import Mouse, Keyboard, KeyboardPhysics, Timing, Sound, MOUSE_NORMAL
from tui_utilities import set_window_title, maximize_window, menu, confirm_exit, header, print

def main():
    set_window_title("Asynchrony Test")
    maximize_window()
    while True:
        selection = menu(
            title = "Asynchrony Test",
            options = {
                "1": "Test asynchronous execution",
                "2": "Wait for task",
                "3": "Cancel task",
                "E": "Exit"
            }
        )
        match selection:
            case "1": test_asynchronous_execution()
            case "2": test_wait_task()
            case "3": test_cancel_task()
            case "E": confirm_exit()

def test_asynchronous_execution():
    def asynchrony():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        keyboard_physics = KeyboardPhysics(
            press_delay = 0.15,
            press_delay_variation = 0.5,
            press_duration = 0.05,
            press_duration_variation = 0.1,
            typing_error_chance = 0.025,
            typing_error_correction_delay = 0.25,
            typing_error_correction_delay_variation = 0.5,
            typing_error_delayed_realization_chance = 0.5
        )
        keyboard = Keyboard(keyboard_physics)
        timing = Timing()
        sound = Sound()
        header("Asynchronous execution")
        print("Mouse, Keyboard and Sound actions are running concurrently...", alignment = "center")
        with keyboard.asynchronous() as keyboard_task: keyboard.write("Running asynchronous actions...")
        with mouse.asynchronous() as mouse_task:
            mouse.wander_until(condition_function = lambda: keyboard_task.is_done)
        with sound.asynchronous() as sound_task: sound.speak("Running asynchronous actions...")
        mouse_task.wait()
        keyboard_task.wait()
        sound_task.wait()

    start_stop_script(asynchrony, "Asynchronous execution test")

def test_wait_task():
    def wait_task():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        header("Wait for task")
        print([
            ("Starting a ", {}),
            ("5", {"color": "#00bfff"}),
            (" second mouse wander...", {})
        ], alignment = "center")
        with mouse.asynchronous() as mouse_task: mouse.wander(duration = 5)
        print("\nNow waiting for the task to finish...", alignment = "center")
        mouse_task.wait()

    start_stop_script(wait_task, "Wait for task")

def test_cancel_task():
    def cancel_task():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        timing = Timing()
        header("Cancel task")
        print([
            ("Starting a ", {}),
            ("10", {"color": "#00bfff"}),
            (" second mouse wander...", {})
        ], alignment = "center")
        with mouse.asynchronous() as mouse_task: mouse.wander(duration = 10)
        print([
            ("\nTask is running. Waiting ", {}),
            ("5", {"color": "#00bfff"}),
            (" seconds before cancelling...", {})
        ], alignment = "center")
        timing.wait(5)
        mouse_task.cancel()

    start_stop_script(cancel_task, "Cancel task")

if __name__ == "__main__": main()