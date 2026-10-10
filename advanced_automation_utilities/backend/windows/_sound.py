import ctypes
lazy import winsound
lazy import base64
lazy import subprocess

def _play_beep_sound(frequency, duration): winsound.Beep(frequency, int(duration * 1000))

def _play_system_sound(sound_name):
    sounds = {
        "info": winsound.MB_ICONASTERISK,
        "warning": winsound.MB_ICONEXCLAMATION,
        "error": winsound.MB_ICONHAND,
        "question": winsound.MB_ICONQUESTION,
        "ok": winsound.MB_OK
    }
    sound_flag = sounds.get(sound_name.lower(), winsound.MB_OK)
    winsound.MessageBeep(sound_flag)

def _play_audio(audio_path):
    alias = "audio"
    ctypes.windll.winmm.mciSendStringW(f"close {alias}", None, 0, None)
    error = ctypes.windll.winmm.mciSendStringW(f"open \"{audio_path}\" alias {alias}", None, 0, None)
    if error: raise RuntimeError("Could not play the audio file.")
    command = f"play {alias} wait"
    ctypes.windll.winmm.mciSendStringW(command, None, 0, None)
    ctypes.windll.winmm.mciSendStringW(f"close {alias}", None, 0, None)

def _speak(text):
    safe_text = text.replace("'", "''")
    command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{safe_text}')"
    encoded_command = base64.b64encode(command.encode("utf-16-le")).decode("utf-8")
    subprocess.run(
        ["powershell", "-EncodedCommand", encoded_command], creationflags = subprocess.CREATE_NO_WINDOW
    )