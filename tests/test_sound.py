from advanced_automation_utilities.sound import Sound
from advanced_automation_utilities.sound._play_system_sound import _PlaySystemSound
from advanced_automation_utilities.sound._play_audio import _PlayAudio
from advanced_automation_utilities.sound._speak import _Speak
import advanced_automation_utilities.sound.sound as sound_module
import advanced_automation_utilities.sound._sound_action as sound_action_module
import advanced_automation_utilities.sound._play_system_sound as _play_system_sound_module
import advanced_automation_utilities.sound._play_audio as _play_audio_module
import advanced_automation_utilities.sound._speak as _speak_module
import advanced_automation_utilities.backend.windows._sound as sound_backend
from types import SimpleNamespace
from hypothesis import strategies, given
import pytest
import base64

def test_sound_facade_delegates_to_actions(monkeypatch):
    recorded_calls = []
    for action_attribute, action_name in (
        ("_PlaySystemSound", "system-sound"),
        ("_PlayAudio", "audio"),
        ("_Speak", "speak")
    ):
        monkeypatch.setattr(
            sound_module,
            action_attribute,
            lambda *arguments, action_name = action_name, **keyword_arguments: SimpleNamespace(
                execute = lambda: recorded_calls.append(
                    (action_name, arguments, keyword_arguments)
                ) or action_name
            )
        )
    sound = sound_module.Sound()
    sound.play_system_sound("ok")
    sound.play_audio("alert.wav")
    sound.speak("hello")
    assert [name for name, _, _ in recorded_calls] == ["system-sound", "audio", "speak"]

def test_abstract_sound_action_probe():
    class SoundActionProbe(sound_action_module._SoundAction):
        def execute(self): return super().execute()

    assert SoundActionProbe().execute() is None

@given(
    frequency = strategies.integers(37, 32767),
    duration = strategies.floats(min_value = 0.001, max_value = 5, allow_nan = False)
)
def test_play_beep_sound_converts_seconds_to_milliseconds(frequency, duration, fake_sound):
    Sound().play_beep_sound(frequency = frequency, duration = duration)
    captured_frequency, captured_duration_ms = fake_sound.beeps[-1]
    assert captured_frequency == frequency
    assert captured_duration_ms == int(duration * 1000)

@given(
    sound_type = strategies.sampled_from(
        ["info", "warning", "error", "question", "ok", "INFO", "Warning"]
    )
)
def test_play_system_sound_accepts_every_valid_type_any_case(sound_type, monkeypatch):
    monkeypatch.setattr(_play_system_sound_module, "_play_system_sound", lambda sound_type: None)
    _PlaySystemSound(sound_type)

def test_play_system_sound_action_calls_backend(monkeypatch):
    recorded_calls = []
    monkeypatch.setattr(
        _play_system_sound_module,
        "_play_system_sound",
        lambda sound_type: recorded_calls.append(sound_type)
    )
    _PlaySystemSound("ok").execute()
    assert recorded_calls == ["ok"]

def test_play_system_sound_rejects_an_invalid_type():
    with pytest.raises(ValueError): _PlaySystemSound("not_a_real_sound")

def test_play_audio_delegates_to_the_backend(tmp_path, monkeypatch):
    audio_file = tmp_path / "sound.wav"; audio_file.write_bytes(b"\x00")
    played = []
    monkeypatch.setattr(_play_audio_module, "_play_audio", lambda path: played.append(path))
    _PlayAudio(str(audio_file)).execute()
    assert played == [str(audio_file)]

def test_play_audio_rejects_a_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError): _PlayAudio(str(tmp_path / "does_not_exist.wav"))

@given(text = strategies.text(min_size = 1, max_size = 100))
def test_speak_passes_the_text_through_untouched(text, monkeypatch):
    spoken = []
    monkeypatch.setattr(_speak_module, "_speak", lambda text: spoken.append(text))
    _Speak(text).execute()
    assert spoken == [text]

@given(spoken_text = strategies.text(min_size = 1, max_size = 200))
def test_speak_quoting_cannot_break_out_of_the_powershell_string_literal(spoken_text, monkeypatch):
    captured = {}

    def fake_run(args, **kwargs): captured["encoded_command"] = args[args.index("-EncodedCommand") + 1]

    monkeypatch.setattr(sound_backend.subprocess, "run", fake_run)
    sound_backend._speak(spoken_text)
    decoded_command = base64.b64decode(captured["encoded_command"]).decode("utf-16-le")
    start = decoded_command.index("Speak('") + len("Speak('")
    end = decoded_command.rindex("')")
    embedded_literal = decoded_command[start:end]
    assert embedded_literal.replace("''", "'") == spoken_text