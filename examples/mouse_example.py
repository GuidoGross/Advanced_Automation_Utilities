import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory in sys.path: sys.path.remove(script_directory)
parent_directory = os.path.dirname(script_directory)
if parent_directory not in sys.path: sys.path.insert(0, parent_directory)

from examples.examples_utilities import start_stop_script
from advanced_automation_utilities import Mouse, MouseInfo, MOUSE_NORMAL
from tui_utilities import (
    set_window_title, maximize_window, menu, confirm_exit, print, header, wait_for_key
)

def main():
    set_window_title("Mouse Test")
    maximize_window()
    while True:
        selection = menu(
            title = "Mouse Test",
            options = {
                "1": "Click",
                "2": "Double click",
                "3": "Right click",
                "4": "Middle click",
                "5": "Drag",
                "7": "Scroll until a condition is met",
                "9": "Wander until a condition is met",
                "8": "Get pointer coordinates and pixel color",
                "9": "Check if pointer is inside the screen",
                "E": "Exit"
            }
        )
        match selection:
            case "1": test_click()
            case "2": test_double_click()
            case "3": test_right_click()
            case "4": test_middle_click()
            case "5": test_drag()
            case "6": test_scroll_until()
            case "7": test_wander_until()
            case "8": test_get_pointer_info()
            case "9": test_is_pointer_on_screen()
            case "E": confirm_exit()

def test_click():
    def click():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        mouse.click(300, 600)

    start_stop_script(click, "Click")

def test_double_click():
    def double_click():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        mouse.double_click(300, 600)

    start_stop_script(double_click, "Double click")

def test_right_click():
    def right_click():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        mouse.right_click(300, 600)

    start_stop_script(right_click, "Right click")

def test_middle_click():
    def middle_click():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        mouse.middle_click(300, 600)

    start_stop_script(middle_click, "Middle click")

def test_drag():
    def drag():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        mouse.drag_and_drop(300, 600, 600, 600)

    start_stop_script(drag, "Drag")

def test_scroll_until():
    def scroll_until():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        mouse.scroll_until(condition_function = lambda: False, direction = "down", timeout = 2.5)
        mouse.scroll_until(condition_function = lambda: False, direction = "up", timeout = 2.5)
        mouse.scroll_until(condition_function = lambda: False, direction = "right", timeout = 2.5)
        mouse.scroll_until(condition_function = lambda: False, direction = "left", timeout = 2.5)

    start_stop_script(scroll_until, "Scroll until a condition is met")

def test_wander_until():
    def wander_until():
        mouse_physics = MOUSE_NORMAL
        mouse = Mouse(mouse_physics)
        mouse.wander_until(condition_function = lambda: False, timeout = 10)

    start_stop_script(wander_until, "Wander until a condition is met")

def test_get_pointer_info():
    def get_pointer_info():
        mouse_info = MouseInfo()
        header("Pointer information")
        coordinates = mouse_info.coordinates
        x = mouse_info.x
        y = mouse_info.y
        pixel_color = mouse_info.pixel_color()
        hexadecimal_pixel_color = mouse_info.pixel_color(format = "hexadecimal")
        print([("Pointer coordinates: ", {"bold": True}), (str(coordinates).replace(",", ";"), {})])
        print([("    - x coordinate: ", {"bold": True}), (f"{x}", {})])
        print([("    - y coordinate: ", {"bold": True}), (f"{y}", {})])
        print("\nPixel color under pointer:", bold = True)
        print([("    - RGB: ", {"bold": True}), (f"■ {pixel_color}", {"color": hexadecimal_pixel_color})])
        print([
            ("    - Hexadecimal: ", {"bold": True}),
            (f"■ {hexadecimal_pixel_color}", {"color": hexadecimal_pixel_color})
        ])
        wait_for_key()

    start_stop_script(get_pointer_info, "Get pointer information")

def test_is_pointer_on_screen():
    def is_pointer_on_screen():
        mouse_info = MouseInfo()
        header("Is the pointer inside the screen?")
        is_on_screen = mouse_info.on_screen(monitor_index = 0)
        print([
            ("The pointer ", {}),
            (
                f"{"is" if is_on_screen else "is not"}",
                {"color": f"{"#00ff00" if is_on_screen else "#ff0000"}"}
            ),
            (" inside the screen", {})
        ], alignment = "center")
        wait_for_key()

    start_stop_script(is_pointer_on_screen, "Check if pointer is inside the screen")

if __name__ == "__main__": main()