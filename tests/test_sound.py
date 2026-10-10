from advanced_automation_utilities.sound import Sound
import advanced_automation_utilities.backend.windows._sound as sound_backend
from hypothesis import strategies, given
import base64

@given(
    frequency = strategies.integers(37, 32767),
    duration = strategies.floats(min_value = 0.001, max_value = 5, allow_nan = False)
)
def test_play_beep_sound_converts_seconds_to_milliseconds(frequency, duration, fake_sound):
    Sound().play_beep_sound(frequency = frequency, duration = duration)
    captured_frequency, captured_duration_ms = fake_sound.beeps[-1]
    assert captured_frequency == frequency
    assert captured_duration_ms == int(duration * 1000)

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