import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory in sys.path: sys.path.remove(script_directory)
parent_directory = os.path.dirname(script_directory)
if parent_directory not in sys.path: sys.path.insert(0, parent_directory)

from examples.examples_utilities import start_stop_script
from advanced_automation_utilities import Screen, ScreenInfo
from tui_utilities import (
    set_window_title,
    maximize_window,
    menu,
    confirm_exit,
    print,
    header,
    wait_for_key,
    success_message,
    error_message
)

def main():
    set_window_title("Screen Test")
    maximize_window()
    while True:
        selection = menu(
            title = "Screen Test",
            options = {
                "1": "Take and save screenshot",
                "2": "Locate image on screen",
                "3": "Read text from screen",
                "4": "Locate text on screen",
                "5": "Get screen resolution",
                "6": "Check if pixel matches color",
                "7": "Check if coordinates are on screen",
                "E": "Exit"
            }
        )
        match selection:
            case "1": test_take_and_save_screenshot()
            case "2": test_locate_image()
            case "3": test_read_text()
            case "4": test_locate_text()
            case "5": test_get_resolution()
            case "6": test_pixel_matches_color()
            case "7": test_on_screen()
            case "E": confirm_exit()

def test_take_and_save_screenshot():
    def take_and_save_screenshot():
        screen = Screen()
        header("Take and save screenshot")
        try:
            save_path = os.path.join(os.path.expanduser("~"), "Pictures", "test_screenshot.png")
            screen.take_screenshot(save_path = save_path)
            success_message(f"Screenshot saved at: {save_path}")
        except Exception as error: error_message(f"Error taking screenshot: {error}")

    start_stop_script(take_and_save_screenshot, "Take screenshot")

def test_locate_image():
    def locate_image():
        screen = Screen()
        header("Locate image on screen")
        result = screen.locate_image("")
        if result[0] is not None and result[1] is not None:
            success_message(f"Image found at position ({result[0]}; {result[1]})")
        else: error_message("Image not found")

    start_stop_script(locate_image, "Locate image on screen")

def test_read_text():
    def read_text():
        screen = Screen()
        header("Read text from screen")
        text = screen.read_text()
        print([("Text on screen:", {"bold": True}), (f" {text}", {})])
        wait_for_key()

    start_stop_script(read_text, "Read text from screen")

def test_locate_text():
    def locate_text():
        screen = Screen()
        header("Locate text on screen")
        text = "Test"
        x, y = screen.locate_text(text)
        if x is not None and y is not None:
            success_message(f"Text \"{text}\" found at position ({x}; {y})")
        else: error_message(f"Text \"{text}\" not found")

    start_stop_script(locate_text, "Locate text on screen")

def test_get_resolution():
    screen_info = ScreenInfo()
    header("Screen resolution")
    print([
        ("Resolution: ", {"bold": True}),
        (f"{str(screen_info.resolution).replace(",", ";")}", {})
    ])
    print([("Width: ", {"bold": True}), (f"{screen_info.width}", {})])
    print([("Height: ", {"bold": True}), (f"{screen_info.height}", {})])
    print([("Work area: ", {"bold": True}), (f"{str(screen_info.work_area).replace(",", ";")}", {})])
    wait_for_key()

def test_pixel_matches_color():
    def pixel_matches_color():
        screen_info = ScreenInfo()
        header("Check if pixel matches color")
        x = 300
        y = 600
        expected = "#FFFFFF"
        matches = screen_info.pixel_matches_color(x, y, expected_color = expected)
        if matches: success_message(f"Pixel at ({x}; {y}) matches {expected}.")
        else: error_message(f"Pixel at ({x}; {y}) does not match {expected}.")

    start_stop_script(pixel_matches_color, "Check if pixel matches color")

def test_on_screen():
    def on_screen():
        screen_info = ScreenInfo()
        header("Check if coordinates are on screen")
        x = 300
        y = 600
        is_visible = screen_info.on_screen(x, y)
        if is_visible: success_message(f"Coordinates ({x}; {y}) are inside the screen.")
        else: error_message(f"Coordinates ({x}; {y}) are outside the screen.")

    start_stop_script(on_screen, "Check if coordinates are on screen")

if __name__ == "__main__": main()