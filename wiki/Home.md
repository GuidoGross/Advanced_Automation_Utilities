<div align = "center">

# **Advanced Automation Utilities**

[![Version](https://img.shields.io/pypi/v/advanced_automation_utilities?color=blue&labelColor=grey&label=Version&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTAgODBWMjI5LjVjMCAxNyA2LjcgMzMuMyAxOC43IDQ1LjNsMTc2IDE3NmMyNSAyNSA2NS41IDI1IDkwLjUgMEw0MTguNyAzMTcuM2MyNS0yNSAyNS02NS41IDAtOTAuNWwtMTc2LTE3NmMtMTItMTItMjguMy0xOC43LTQ1LjMtMTguN0g0OEMyMS41IDMyIDAgNTMuNSAwIDgwem0xMTIgMzJhMzIgMzIgMCAxIDEgMCA2NCAzMiAzMiAwIDEgMSAwLTY0eiIvPjwvc3ZnPg==&logoColor=white&style=flat-square)](https://pypi.org/project/advanced_automation_utilities/)
[![Python version](https://img.shields.io/badge/Python_version-%E2%89%A5_v3.10-blue?labelColor=grey&logo=python&logoColor=white&style=flat-square)](https://www.python.org/downloads/)
[![Windows version](https://img.shields.io/badge/Windows_version-%E2%89%A5_10-blue?labelColor=grey&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4OCA4OCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0wIDEyLjQgTDM1LjcgNy42IFY0MS42IEgwIFogTTM5LjYgNyBMODggMCBWNDEuNiBIMzkuNiBaIE0wIDQ2LjQgSDM1LjcgVjgwLjQgTDAgNzUuNiBaIE0zOS42IDQ2LjQgSDg4IFY4OCBMMzkuNiA4MSBaIi8+PC9zdmc+&logoColor=white&style=flat-square)](https://www.microsoft.com/software-download/windows10)
[![Total downloads](https://img.shields.io/pepy/dt/advanced_automation_utilities?color=blue&labelColor=grey&label=Total%20downloads&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MTIgNTEyIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTI4OCAzMmMwLTE3LjctMTQuMy0zMi0zMi0zMnMtMzIgMTQuMy0zMiAzMmwwIDI0Mi43LTczLjQtNzMuNGMtMTIuNS0xMi41LTMyLjgtMTIuNS00NS4zIDBzLTEyLjUgMzIuOCAwIDQ1LjNsMTI4IDEyOGMxMi41IDEyLjUgMzIuOCAxMi41IDQ1LjMgMGwxMjgtMTI4YzEyLjUtMTIuNSAxMi41LTMyLjggMC00NS4zcy0zMi44LTEyLjUtNDUuMyAwTDI4OCAyNzQuNyAyODggMzJ6TTY0IDM1MmMtMzUuMyAwLTY0IDI4LjctNjQgNjRsMCAzMmMwIDM1LjMgMjguNyA2NCA2NCA2NGwzODQgMGMzNS4zIDAgNjQtMjguNyA2NC02NGwwLTMyYzAtMzUuMy0yOC43LTY0LTY0LTY0bC0xMDEuNSAwLTQ1LjMgNDUuM2MtMjUgMjUtNjUuNSAyNS05MC41IDBMMTY1LjUgMzUyIDY0IDM1MnptMzY4IDU2YTI0IDI0IDAgMSAxIDAgNDggMjQgMjQgMCAxIDEgMC00OHoiLz48L3N2Zz4=&logoColor=white&style=flat-square)](https://pepy.tech/project/advanced_automation_utilities)
[![Sponsor](https://img.shields.io/badge/Sponsor-Ko--fi-blue?labelColor=grey&logo=ko-fi&logoColor=white&style=flat-square)](https://ko-fi.com/guidoivangross)

**A powerful, native Python library for Windows automation, featuring Context Manager-based asynchronous chaining, advanced human-like physics, and zero dependence on heavy automation libraries. It leverages native `ctypes` hooks for maximum speed, security, and lower overhead.**

</div>

## **Purpose**

**This library is designed for scripts and applications that need:**

- Reliable, human-like mouse movements natively in Windows.
- Low-level keyboard hooks and precise inputs.
- Fast and accurate screen vision (OCR and image matching).
- Asynchronous execution and method chaining.
- Reliable timing, sound, and system-level operations.

## **Requirements**

### **Dependencies**

> [!NOTE]
> Standard library modules are used where possible; only external dependencies are listed.

- `mss` (v6.1.0 or higher)
- `numpy` (v1.21.0 or higher)
- `opencv-python` (v4.5.5 or higher)
- `psutil` (v5.8.0 or higher)
- `PyGetWindow` (v0.0.9 or higher)
- `pyperclip` (v1.8.2 or higher)
- `tui_utilities` (v1.9.17 or higher)
- `winrt-Windows.Foundation` (v3.0 or higher)
- `winrt-Windows.Foundation.Collections` (v3.0 or higher)
- `winrt-Windows.Graphics.Imaging` (v3.0 or higher)
- `winrt-Windows.Media.Ocr` (v3.0 or higher)
- `winrt-Windows.Storage.Streams` (v3.0 or higher)

### **Python version**

Python (v3.10 or higher)

### **Operating System**

Windows 10 or higher.

## **Installation**

- **Install:**

    ```powershell
    pip install advanced_automation_utilities
    ```

- **Show:**

    ```powershell
    pip show advanced_automation_utilities
    ```

- **Update:**

    ```powershell
    pip install -U advanced_automation_utilities
    ```

- **Uninstall:**

    ```powershell
    pip uninstall -y advanced_automation_utilities
    ```

## **Features**

**Choose a section to explore:**

- **[Mouse](Mouse)**: Clicks, movement, scrolling and physics.
- **[Keyboard](Keyboard)**: Typing, hotkeys, blocking, and modifiers.
- **[Screen](Screen)**: OCR text reading, image location, and pixel colors.
- **[Timing](Timing)**: Smart waits, random delays, and performance measuring.
- **[Sound](Sound)**: System sounds, TTS (Text-to-Speech), and audio files.
- **[System](System)**: Process management, window manipulation, and kill-switch.
- **[Asynchrony](Asynchrony)**: Non-blocking parallel executions.
- **[Physics](Physics)**: Human-like mouse and keyboard behaviors.
- **[Exceptions](Exceptions)**: Library-specific errors.