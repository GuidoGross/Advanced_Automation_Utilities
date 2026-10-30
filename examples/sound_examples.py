import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory in sys.path: sys.path.remove(script_directory)
parent_directory = os.path.dirname(script_directory)
if parent_directory not in sys.path: sys.path.insert(0, parent_directory)

from advanced_automation_utilities import Sound
from tui_utilities import set_window_title, maximize_window, menu, confirm_exit, header, print

def main():
    set_window_title("Sound Test")
    maximize_window()
    while True:
        selection = menu(
            title = "Sound Test",
            options = {
                "1": "Play beep sound",
                "2": "Play audio file",
                "3": "Play system sound",
                "4": "Synthesize text to speech",
                "E": "Exit"
            }
        )
        match selection:
            case "1": test_play_beep_sound()
            case "2": test_play_audio()
            case "3": test_system_sound()
            case "4": test_speak()
            case "E": confirm_exit()

def test_play_beep_sound():
    sound = Sound()
    header("Play beep sound")
    print("Playing beep sound...", alignment = "center")
    sound.play_beep_sound(1000, 0.5)

def test_play_audio():
    sound = Sound()
    header("Play audio file")
    print("Playing audio file...", alignment = "center")
    sound.play_audio("")

def test_system_sound():
    sound = Sound()
    header("Play system sound")
    print("Playing system sound...", alignment = "center")
    sound.play_system_sound("warning")

def test_speak():
    sound = Sound()
    header("Synthesize text to speech")
    print("Playing message...", alignment = "center")
    sound.speak("Hello, world!")

if __name__ == "__main__": main()