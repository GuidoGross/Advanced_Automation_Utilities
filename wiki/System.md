**[Home](Home)** ➔ **[System](System)**

<div align = "center">

# **System**

**High-level operating system actions and process management. This module provides a robust interface to manage the Windows clipboard, window states, process termination, and power options like sleeping, hibernating, and system reboots.**

</div>

---

### **`System().set_clipboard_text()`**

Sets the text content of the Windows clipboard.

**Description:**

Sets the text content of the Windows clipboard. This is extremely useful for automating copy-paste workflows or seamlessly transferring data from your script to other applications.

**Arguments:**

- **`text` (`str`)**

**Returns:**

**`Self`**

**Example:**

```python
System().set_clipboard_text(text = "Text to paste later.")
```

---

### **`System().open_file()`**

Opens a file or starts an executable.

**Description:**

Starts `.exe` and `.com` files with `subprocess.Popen`, and `.bat` and `.cmd` files through `cmd.exe`. Each uses the file's directory as the working directory. Other files are opened with their default program through `os.startfile`.

**Arguments:**

- **`file_path` (`str`)**

**Returns:**

**`Self`**

**Example:**

```python
System().open_file(file_path = "notepad.exe")
```

---

### **`System().kill_process()`**

Terminates an active process by its name.

**Description:**

Terminates an active process by its name. This provides a robust way to clean up applications after an automation task finishes, or to forcefully close unresponsive programs.

**Arguments:**

- **`process` (`str`)**
- **`force` (`bool`)**

**Returns:**

**`Self`**

**Example:**

```python
System().kill_process(process = "notepad.exe", force = True)
```

---

### **`System().focus_window()`**

Brings a specific window to the foreground by its title.

**Description:**

Brings a specific window to the foreground by its title. This is essential for ensuring that subsequent mouse clicks and keyboard strokes are sent to the correct application, avoiding accidental interactions with background apps.

**Arguments:**

- **`window_title` (`str`)**

**Returns:**

**`Self`**

**Example:**

```python
System().focus_window(window_title = "Untitled - Notepad")
```

---

### **`System().resize_window()`**

Resizes a specific window to the specified dimensions by its title.

**Description:**

Resizes a specific window to the specified dimensions by its title. This is extremely useful for automating GUI applications or ensuring that a window occupies the exact screen space required for subsequent automation steps.

**Arguments:**

- **`window_title` (`str`)**
- **`width` (`int`):** Must be > 0.
- **`height` (`int`):** Must be > 0.

**Returns:**

**`Self`**

**Example:**

```python
System().resize_window(window_title = "Untitled - Notepad", width = 800, height = 600)
```

---

### **`System().move_window()`**

Moves a specific window to the specified coordinates by its title.

**Description:**

Moves a specific window to the specified coordinates by its title. Similar to `resize_window()`, this helps guarantee that your automation target is perfectly positioned before executing coordinate-based mouse interactions.

**Arguments:**

- **`window_title` (`str`)**
- **`x` (`int`)**
- **`y` (`int`)**

**Returns:**

**`Self`**

**Example:**

```python
System().move_window(window_title = "Untitled - Notepad", x = 250, y = 500)
```

---

### **`System().close_window()`**

Gently closes a specific window by its title.

**Description:**

Sends a graceful WM_CLOSE signal to a specific window by its title.

**Arguments:**

- **`window_title` (`str`)**

**Returns:**

**`Self`**

**Example:**

```python
System().close_window(window_title = "Untitled - Notepad")
```

---

### **`System().lock_screen()`**

Locks the Windows session (Win+L).

**Description:**

Locks the Windows session (equivalent to pressing Win+L). This is ideal for scripts that handle sensitive information and need to secure the computer immediately after the automated task finishes.

**Returns:**

**`Self`**

**Example:**

```python
System().lock_screen()
```

---

### **`System().sign_out()`**

Signs out the current Windows user.

**Description:**

Signs out the current Windows user. This gently closes all running applications and returns to the Windows login screen, making it useful for gracefully ending a day's worth of automated tasks.

**Returns:**

**`Self`**

**Example:**

```python
System().sign_out()
```

---

### **`System().sleep()`**

Puts the computer into sleep mode.

**Description:**

Puts the computer into sleep mode (suspend to RAM). This is a great way to save energy when an automation task finishes running overnight without completely turning off the machine.

**Returns:**

**`Self`**

**Example:**

```python
System().sleep()
```

---

### **`System().hibernate()`**

Puts the computer into hibernation mode.

**Description:**

Puts the computer into hibernation mode (suspend to disk). This completely powers off the machine while saving the exact state of all open applications, allowing you to seamlessly resume your work later.

**Returns:**

**`Self`**

**Example:**

```python
System().hibernate()
```

---

### **`System().shutdown()`**

Turns off the computer.

**Description:**

Turns off the computer, optionally waiting for a specified delay before powering down. This is perfect for cleanly shutting down a remote or unattended machine after a long-running automation process finishes.

**Arguments:**

- **`delay` (`int`):** Seconds. Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
System().shutdown(delay = 60)
```

---

### **`System().restart()`**

Restarts the computer.

**Description:**

Restarts the computer, optionally waiting for a specified delay before rebooting. This is useful for applying system updates or resetting the environment before starting a fresh automation cycle.

**Arguments:**

- **`delay` (`int`):** Seconds. Must be ≥ 0.

**Returns:**

**`Self`**

**Example:**

```python
System().restart(delay = 60)
```

---

### **`System().enable_kill_switch()`**

Enables a global kill switch to abort execution instantly.

**Description:**

Injects a high-priority hardware hook to listen for the abort shortcut.

**Arguments:**

- **`*keys` (`str`)**

**Returns:**

**`Self`**

**Example:**

```python
System().enable_kill_switch("ctrl", "shift", "alt", "k")
```

> [!IMPORTANT]
> When triggered, an asynchronous `KillSwitchTriggered` exception is raised in all automation threads, completely aborting execution safely.

---

### **`System().disable_kill_switch()`**

Disables the global kill switch.

**Description:**

Safely unregisters the hook to disable the kill switch.

**Returns:**

**`Self`**

**Example:**

```python
System().disable_kill_switch()
```

---

### **`SystemInfo().clipboard_text`**

Gets the current text content of the Windows clipboard.

**Description:**

Gets the current text content of the Windows clipboard. This allows your scripts to seamlessly read and process text that the user or other applications have recently copied.

**Returns:**

**`str`**

**Example:**

```python
text = SystemInfo().clipboard_text
```

---

### **`SystemInfo().active_window_title`**

Gets the title of the currently focused/active window.

**Description:**

Gets the title of the currently focused/active window. This allows your scripts to interact with the active window or to determine which application the user is currently using.

**Returns:**

**`str`**

**Example:**

```python
title = SystemInfo().active_window_title
```

---

### **`SystemInfo().is_process_running()`**

Checks if a specific process is currently running.

**Description:**

Checks if a specific process is currently running. This allows your scripts to determine if an application is active or not.

**Arguments:**

- **`process` (`str`)**

**Returns:**

**`bool`**

**Example:**

```python
is_running = SystemInfo().is_process_running(process = "notepad.exe")
```