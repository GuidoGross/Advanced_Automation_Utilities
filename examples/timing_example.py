import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory in sys.path: sys.path.remove(script_directory)
parent_directory = os.path.dirname(script_directory)
if parent_directory not in sys.path: sys.path.insert(0, parent_directory)

from examples.examples_utilities import start_stop_script
from advanced_automation_utilities import KeyboardInfo, Timing, TimingInfo, measure_time
from tui_utilities import (
    set_window_title,
    maximize_window,
    menu,
    confirm_exit,
    print,
    header,
    wait_for_key,
    decimal_format,
    success_message,
    error_message
)

def main():
    set_window_title("Timing Test")
    maximize_window()
    while True:
        selection = menu(
            title = "Timing Test",
            options = {
                "1": "Wait",
                "2": "Wait randomly",
                "3": "Wait by condition",
                "4": "Get execution time of a function",
                "E": "Exit"
            }
        )
        match selection:
            case "1": test_wait()
            case "2": test_wait_random()
            case "3": test_wait_until()
            case "4": test_measure_time()
            case "E": confirm_exit()

def test_wait():
    timing = Timing()
    header("Wait")
    waiting_time = 3
    print(
        [("Waiting ", {}), (f"{waiting_time}", {"color": "#00bfff"}), (" seconds...\n", {})],
        alignment = "center"
    )
    timing.wait(waiting_time)
    print("\nWait finished", alignment = "center")
    wait_for_key()

def test_wait_random():
    timing = Timing()
    timing_info = TimingInfo()
    header("Wait randomly")
    lower_waiting_time = 1
    upper_waiting_time = 5
    print([
        ("Waiting randomly between ", {}),
        (f"{lower_waiting_time}", {"color": "#00bfff"}),
        (" and ", {}),
        (f"{upper_waiting_time}", {"color": "#00bfff"}),
        (" seconds...\n", {})
    ], alignment = "center")
    start_time = timing_info.time
    timing.wait_random(lower_waiting_time, upper_waiting_time)
    end_time = timing_info.time
    print([
        ("\nWait finished in ", {}),
        (f"{decimal_format((end_time - start_time) * 1000, decimals = 0)}ms", {"color": "#00bfff"})
    ], alignment = "center")
    wait_for_key()

def test_wait_until():
    def _test():
        timing = Timing()
        keyboard_info = KeyboardInfo()
        header("Wait by condition")
        print([
            ("Waiting up to a maximum of 5 seconds for you to press the ", {}),
            ("Space", {"color": "#00bfff"}),
            (" key...\n", {})
        ], alignment = "center")

        def condition(): return keyboard_info.is_pressed("space")

        success = timing.wait_until(condition, timeout = 5)
        if success:
            wait_for_key(text = "")
            success_message("You pressed the \"Space\" key in time")
        else: error_message("You didn't press the \"Space\" key in time")
        while keyboard_info.is_pressed("space"): timing.wait(0.01)
    start_stop_script(_test, "Wait by condition")

def test_measure_time():
    timing = Timing()
    header("Measure execution time of a function")

    @measure_time
    def simulated_task():
        print("Starting a simulated task...\n", alignment = "center")
        timing.wait_random(1, 3)

    simulated_task()
    wait_for_key()

if __name__ == "__main__": main()