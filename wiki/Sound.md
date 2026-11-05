**[Home](Home)** ➔ **[Sound](Sound)**

<div align = "center">

# **Sound**

**Audio playback and text-to-speech features. Easily integrate audible alerts using motherboard beeps, play local audio files, trigger native Windows notification sounds, or use the built-in Text-To-Speech engine without external dependencies.**

</div>

---

### **`Sound().play_beep_sound()`**

Plays a motherboard beep with a specific frequency and duration.

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

---

### **`Sound().play_system_sound()`**

Plays a default Windows system sound.

**Description:**

Plays a default Windows system sound between the given options.

**Arguments:**

- **`sound_type` (`SystemSound`):** Valid options: "info", "warning", "error", "question", "ok". Matching is case-insensitive.

**Returns:**

**`Self`**

**Example:**

```python
Sound().play_system_sound(sound_type = "warning")
```

---

### **`Sound().play_audio()`**

Plays an audio file from the file system.

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

---

### **`Sound().speak()`**

Synthesizes text to speech using the default Windows voice.

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