from tui_utilities import header, print, decimal_format
from pathlib import Path
import time
import shutil
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPORARY_DIRECTORY_NAMES = {"__pycache__", ".pytest_cache", ".hypothesis", "build"}

def main():
    start_time = time.perf_counter()
    header("Temporary Folder Cleanup")
    cleanup_errors = []
    try: directories_to_remove = _temporary_directories()
    except OSError as error:
        print([
            ("Could not inspect project folders:", {"bold": True}), (f" {error}", {})
        ], color = "#ff0000")
        return 1
    for directory_path in directories_to_remove:
        try:
            if directory_path.is_symlink(): directory_path.unlink()
            else: shutil.rmtree(directory_path)
        except OSError as error: cleanup_errors.append((directory_path, error))
    coverage_file = PROJECT_ROOT / ".coverage"
    if coverage_file.is_file():
        try: coverage_file.unlink()
        except OSError as error:  cleanup_errors.append((coverage_file, error))
    if cleanup_errors:
        for path, error in cleanup_errors:
            print([
                ("Could not remove:", {"bold": True}), (f" {path}. {error}", {})
            ], color = "#ff0000")
        return 1
    duration = (time.perf_counter() - start_time) * 1000
    print([
        ("Folder cleanup completed in:", {"bold": True}),
        (f" {decimal_format(duration, decimals = 0)}ms", {})
    ], color = "#00ff00")
    return 0

def _temporary_directories():
    directories = []
    for current_directory, child_directories, _ in os.walk(PROJECT_ROOT, topdown = True, onerror = _raise_walk_error):
        child_directories[:] = [
            directory_name for directory_name in child_directories if directory_name != ".git"
        ]
        matching_directories = [
            directory_name for directory_name in child_directories
            if directory_name in TEMPORARY_DIRECTORY_NAMES or directory_name.endswith(".egg-info")
        ]
        for directory_name in matching_directories:
            directories.append(Path(current_directory) / directory_name)
        child_directories[:] = [
            directory_name for directory_name in child_directories
            if directory_name not in matching_directories
        ]
    return directories

def _raise_walk_error(error): raise error

if __name__ == "__main__": raise SystemExit(main())