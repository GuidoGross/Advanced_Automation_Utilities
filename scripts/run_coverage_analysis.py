from tui_utilities import header, print, decimal_format
from pathlib import Path
import argparse
import time
import os
import sys
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HYPOTHESIS_PROFILES = ("development", "pre_commit", "post_commit")

def main():
    start_time = time.perf_counter()
    header("Coverage Analysis")
    parser = argparse.ArgumentParser(description = "Run unit tests with line and branch coverage.")
    parser.add_argument("--hypothesis-profile", choices = HYPOTHESIS_PROFILES, default = "development")
    arguments = parser.parse_args()
    test_files = sorted((PROJECT_ROOT / "tests").glob("test_*.py"))
    environment = os.environ.copy()
    environment["HYPOTHESIS_PROFILE"] = arguments.hypothesis_profile
    command = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=advanced_automation_utilities",
        "--cov-branch",
        "--cov-report=term-missing",
        *(str(test_file.relative_to(PROJECT_ROOT)) for test_file in test_files)
    ]
    sys.stdout.flush()
    result = subprocess.run(command, cwd = PROJECT_ROOT, env = environment, check = False)
    if result.returncode:
        print(
            f"Coverage analysis failed with exit code: {result.returncode}",
            color = "#ff0000",
            bold = True
        )
        return result.returncode
    duration = (time.perf_counter() - start_time) * 1000
    print([
        ("Coverage analysis completed successfully in:", {"bold": True}),
        (f" {decimal_format(duration, decimals = 0)}ms", {})
    ], color = "#00ff00")
    return 0

if __name__ == "__main__": raise SystemExit(main())