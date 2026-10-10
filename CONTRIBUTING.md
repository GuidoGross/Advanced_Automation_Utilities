<div align = "center">

# **Contributing**

**Thank you for considering a contribution to Advanced Automation Utilities. Contributions can include bug reports, documentation improvements, examples, and code changes.**

</div>

## **Before you start**

- For substantial changes, open an issue or start a discussion before implementation so the approach can be reviewed.
- For bug reports, include the Windows and Python versions, the library version, steps to reproduce the problem, and the expected and actual behavior.
- Remove credentials, personal data, and other sensitive information from reports and examples.

## **Development environment**

The library supports Windows 10 or higher and Python 3.15 or higher. Clone the repository and change to its directory:

```powershell
git clone https://github.com/GuidoGross/Advanced_Automation_Utilities.git
cd Advanced_Automation_Utilities
```

From the repository directory, install the project and its development dependencies in editable mode using your configured Python installation:

```powershell
python -m pip install -e ".[dev]"
```

## **Automated checks**

- **Install:**

    ```powershell
    pre-commit install
    ```

- **Run:**

    ```powershell
    pre-commit run --all-files
    ```

> [!NOTE]
> The configured hooks validate YAML and TOML syntax and reject merge-conflict markers. GitHub Actions also builds the package, installs it on a fresh Windows runner, and verifies that it imports on every push.

## **Changes and pull requests**

- Keep each change focused and consistent with the existing code and documentation style.
- Use English for code, identifiers, and technical documentation, consistent with the project.
- Update the README.md, wiki, or examples when a change affects documented behavior or public APIs.
- Explain the reason for new dependencies and keep compatibility with the supported Windows and Python versions in mind.
- Describe the change, its motivation, and any compatibility impact in the pull request.
- Test the affected behavior on Windows when possible. This repository does not currently define an automated test suite; state which checks or manual steps you performed and their results.

## **Legal**

By submitting a contribution to this repository, you agree that the contribution may be distributed under the GNU Affero General Public License, version 3 or any later version (AGPL-3.0-or-later), the same license as this library. You confirm that you have the right to submit the contribution under these terms. You retain copyright in your contribution; this does not transfer ownership to the project maintainer.