from ._play_beep_sound import _PlayBeepSound
from ._play_system_sound import _PlaySystemSound
from ._play_audio import _PlayAudio
from ._speak import _Speak
from .._queueable_controller import _QueueableController
from .._typing import SystemSound
from typing import Self

class Sound(_QueueableController):
    """
    **Description:**

    Audio playback and text-to-speech features. Easily integrate audible alerts using motherboard beeps, play local audio files, trigger native Windows notification sounds, or use the built-in Text-To-Speech engine without external dependencies.
    """
    def __init__(self) -> None:
        """
        **Description:**

        Initializes the Sound controller.

        **Returns:**

        **`None`**
        """
        super().__init__()

    def play_beep_sound(self, frequency: int, duration: float) -> Self:
        """
        **`Sound().play_beep_sound()`:** Plays a motherboard beep with a specific frequency and duration.

        **Description:**

        Plays a beep sound using the Windows API. Useful for audible notifications.

        **Arguments:**

        - **`frequency` (`int`):** Must be between 37 and 32767.
        - **`duration` (`float`):** Seconds. Must be > 0.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Sound().play_beep_sound(frequency = 1000, duration = 0.5)
        ```
        """
        return self._execute_or_queue(_PlayBeepSound(frequency = frequency, duration = duration))

    def play_system_sound(self, sound_type: SystemSound) -> Self:
        """
        **`Sound().play_system_sound()`:** Plays a default Windows system sound.

        **Description:**

        Plays a default Windows system sound between the given options.

        **Arguments:**

        - **`sound_type` (`str`):** Valid options: "info", "warning", "error", "question", "ok". Matching is case-insensitive.

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Sound().play_system_sound(sound = "warning")
        ```
        """
        return self._execute_or_queue(_PlaySystemSound(sound_type = sound_type))

    def play_audio(self, file_path: str) -> Self:
            """
            **`Sound().play_audio()`:** Plays an audio file from the file system.

            **Description:**

            Uses the native Windows MCI API for lightweight audio playback.

            **Arguments:**

            - **`file_path` (`str`)**

            **Returns:**

            **`Self`**

            **Example:**

            ```python
            Sound().play_audio(file_path = "alert.wav")
            ```
            """
            return self._execute_or_queue(_PlayAudio(file_path = file_path))

    def speak(self, text: str) -> Self:
        """
        **`Sound().speak()`:** Synthesizes text to speech using the default Windows voice.

        **Description:**

        Uses native PowerShell SAPI integration for zero-dependency TTS to synthesize text to speech.

        **Arguments:**

        - **`text` (`str`)**

        **Returns:**

        **`Self`**

        **Example:**

        ```python
        Sound().speak(text = "Automation task completed successfully.")
        ```

        ### **System Utilities (system)**

        **High-level operating system actions and process management:**
        """
        return self._execute_or_queue(_Speak(text = text))