from tui_utilities import decimal_format, header, print
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import time
import argparse
import os
import sys
import subprocess
import re
import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HYPOTHESIS_PROFILES = ("development", "pre_commit", "post_commit")
TEST_FILES_BY_MODULE = {
    "asynchrony": ("tests/test_asynchrony.py",),
    "keyboard": ("tests/test_keyboard.py",),
    "mouse": ("tests/test_mouse.py",),
    "screen": ("tests/test_screen.py",),
    "sound": ("tests/test_sound.py",),
    "system": ("tests/test_system.py",),
    "timing": ("tests/test_timing.py",),
    "utilities": ("tests/test_utilities.py",),
    "windows_backend": ("tests/test_windows_backend.py",)
}
COMMON_MODULE_TEST_MODULES = (
    "asynchrony",
    "keyboard",
    "mouse",
    "screen",
    "sound",
    "system",
    "timing",
    "utilities",
    "windows_backend"
)
QUEUEABLE_TEST_MODULES = ("asynchrony", "keyboard", "mouse", "sound", "system")

def main():
    start_time = time.perf_counter()
    header("Unit Tests")
    parser = argparse.ArgumentParser(description = "Run unit tests affected by changed files.")
    parser.add_argument("--hypothesis-profile", choices = HYPOTHESIS_PROFILES, default = "development")
    parser.add_argument("--changed-files", nargs = "*", default = [])
    parser.add_argument(
        "--require-full-suite-on-unpublished",
        action = "store_true",
        help = "Run all tests if the version in pyproject.toml is not yet published on PyPI."
    )
    arguments = parser.parse_args()
    all_test_files = sorted(
        str(test_file.relative_to(PROJECT_ROOT))
        for test_file in (PROJECT_ROOT / "tests").glob("test_*.py")
    )
    selected_tests, run_all_tests = _select_tests(arguments.changed_files)
    if not run_all_tests and arguments.require_full_suite_on_unpublished and not _is_version_published():
        run_all_tests = True
    if run_all_tests: selected_tests = set(all_test_files)
    ordered_test_files = sorted(selected_tests)
    if run_all_tests:
        print(
            f" Running all unit tests with the {arguments.hypothesis_profile} profile.",
            bold = True
        )
    elif ordered_test_files:
        print(
            f" Running selected unit tests with the {arguments.hypothesis_profile} profile:",
            bold = True
        )
        for test_file in ordered_test_files: print(f"    - {test_file}")
    else:
        print("No related unit tests were selected.", bold = True)
        return 0
    environment = os.environ.copy()
    environment["HYPOTHESIS_PROFILE"] = arguments.hypothesis_profile
    sys.stdout.flush()
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *ordered_test_files],
        cwd = PROJECT_ROOT,
        env = environment,
        check = False
    )
    if result.returncode:
        print(
            f"Unit tests failed with exit code: {result.returncode}", color = "#ff0000", bold = True
        )
        return result.returncode
    duration = (time.perf_counter() - start_time) * 1000
    print([
        ("Unit tests completed successfully in:", {"bold": True}),
        (f" {decimal_format(duration, decimals = 0)}ms", {})
    ], color = "#00ff00")
    return 0

def _select_tests(changed_files):
    all_test_files = {
        str(test_file.relative_to(PROJECT_ROOT))
        for test_file in (PROJECT_ROOT / "tests").glob("test_*.py")
    }
    selected_tests = set()
    has_non_test_changes = False
    for changed_file in changed_files:
        normalized_path = changed_file.replace("\\", "/")
        while normalized_path.startswith("./"): normalized_path = normalized_path[2:]
        test_match = re.fullmatch(r"tests/(test_[^/]+\.py)", normalized_path)
        if test_match:
            test_path = f"tests/{test_match.group(1)}"
            if (PROJECT_ROOT / test_path).is_file():
                selected_tests.add(test_path)
                continue
            return all_test_files, True
        if normalized_path in {"tests/conftest.py", "scripts/run_tests.py", "pyproject.toml", ".github/workflows/unit_tests.yml"}:
            return all_test_files, True
        if not normalized_path.startswith("advanced_automation_utilities/"):
            has_non_test_changes = True
            continue
        module_match = re.match(
            r"advanced_automation_utilities/(keyboard|mouse|screen|sound|system|timing)/",
            normalized_path
        )
        if module_match:
            module_name = module_match.group(1)
            _add_module_tests(selected_tests, (module_name,))
            if module_name == "timing": _add_module_tests(selected_tests, QUEUEABLE_TEST_MODULES)
            elif module_name == "screen": _add_module_tests(selected_tests, ("mouse",))
            continue
        backend_match = re.fullmatch(
            r"advanced_automation_utilities/backend/windows/_(keyboard|mouse|screen|sound|system)\.py",
            normalized_path
        )
        if backend_match:
            backend_module = backend_match.group(1)
            _add_module_tests(selected_tests, (backend_module, "windows_backend"))
            if backend_module == "keyboard": _add_module_tests(selected_tests, ("system",))
            elif backend_module == "screen": _add_module_tests(selected_tests, ("mouse",))
            continue
        if normalized_path == "advanced_automation_utilities/backend/windows/_windows_backend_utilities.py":
            return all_test_files, True
        if re.fullmatch(r"advanced_automation_utilities/_(queueable_controller|asynchronous_context|task)\.py", normalized_path):
            _add_module_tests(selected_tests, QUEUEABLE_TEST_MODULES)
            continue
        if normalized_path == "advanced_automation_utilities/_kill_switch_event.py":
            _add_module_tests(
                selected_tests,
                ("asynchrony", "keyboard", "mouse", "sound", "system", "timing", "windows_backend")
            )
            continue
        if normalized_path in {"advanced_automation_utilities/_utilities.py", "advanced_automation_utilities/_typing.py", "advanced_automation_utilities/exceptions.py", "advanced_automation_utilities/__init__.py"}:
            _add_module_tests(selected_tests, COMMON_MODULE_TEST_MODULES)
            continue
        return all_test_files, True
    if selected_tests or has_non_test_changes: return selected_tests, False
    return all_test_files, True

def _add_module_tests(selected_tests, module_names):
    for module_name in module_names: selected_tests.update(TEST_FILES_BY_MODULE[module_name])

def _is_version_published():
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as file: project = tomllib.load(file)["project"]
    package_name = project["name"].replace("-", "_")
    version = project["version"]
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    try:
        with urlopen(url, timeout = 10): return True
    except HTTPError as error:
        if error.code == 404: return False
        print(
            f"Unable to verify whether version {version} is on PyPI (HTTP {error.code}); running all unit tests.",
            color = "#ff0000",
            bold = True
        )
        return False
    except (URLError, TimeoutError, OSError) as error:
        print(
            f"Unable to verify whether version {version} is on PyPI ({error}); running all unit tests.",
            color = "#ff0000",
            bold = True
        )
        return False

if __name__ == "__main__": raise SystemExit(main())