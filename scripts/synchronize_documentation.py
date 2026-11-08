from tui_utilities import header, print, decimal_format
from pathlib import Path
import re
import time
import argparse
import ast
import tomllib
import textwrap
import difflib

CLASS_SOURCE_TO_WIKI = {
    "advanced_automation_utilities/mouse/mouse.py": "wiki/Mouse.md",
    "advanced_automation_utilities/mouse/mouse_info.py": "wiki/Mouse.md",
    "advanced_automation_utilities/mouse/mouse_physics.py": "wiki/Physics.md",
    "advanced_automation_utilities/keyboard/keyboard.py": "wiki/Keyboard.md",
    "advanced_automation_utilities/keyboard/keyboard_info.py": "wiki/Keyboard.md",
    "advanced_automation_utilities/keyboard/keyboard_physics.py": "wiki/Physics.md",
    "advanced_automation_utilities/screen/screen.py": "wiki/Screen.md",
    "advanced_automation_utilities/screen/screen_info.py": "wiki/Screen.md",
    "advanced_automation_utilities/sound/sound.py": "wiki/Sound.md",
    "advanced_automation_utilities/system/system.py": "wiki/System.md",
    "advanced_automation_utilities/system/system_info.py": "wiki/System.md",
    "advanced_automation_utilities/timing/timing.py": "wiki/Timing.md",
    "advanced_automation_utilities/timing/timing_info.py": "wiki/Timing.md",
    "advanced_automation_utilities/_task.py": "wiki/Asynchrony.md",
    "advanced_automation_utilities/_queueable_controller.py": "wiki/Asynchrony.md",
}
PRIMARY_CLASS_SOURCE_BY_WIKI = {
    "wiki/Mouse.md": "advanced_automation_utilities/mouse/mouse.py",
    "wiki/Keyboard.md": "advanced_automation_utilities/keyboard/keyboard.py",
    "wiki/Screen.md": "advanced_automation_utilities/screen/screen.py",
    "wiki/Sound.md": "advanced_automation_utilities/sound/sound.py",
    "wiki/System.md": "advanced_automation_utilities/system/system.py",
    "wiki/Timing.md": "advanced_automation_utilities/timing/timing.py",
}
DATACLASS_SOURCE_FILES = {
    "advanced_automation_utilities/mouse/mouse_physics.py",
    "advanced_automation_utilities/keyboard/keyboard_physics.py",
}
FUNCTION_TO_WIKI = {"measure_time": ("wiki/Timing.md", "@measure_time")}
WIKI_EXCLUDED_ENTITIES = {
    "wiki/Asynchrony.md": {"asynchronous()"},
    "wiki/Mouse.md": {"Keyboard Utilities (keyboard)"},
    "wiki/Keyboard.md": {"Screen Utilities (screen)"},
    "wiki/Screen.md": {"Timing Utilities (timing)"},
    "wiki/Sound.md": {"System Utilities (system)"}
}
SOURCE_FILES = [
    "advanced_automation_utilities/mouse/mouse.py",
    "advanced_automation_utilities/mouse/mouse_info.py",
    "advanced_automation_utilities/mouse/mouse_physics.py",
    "advanced_automation_utilities/keyboard/keyboard.py",
    "advanced_automation_utilities/keyboard/keyboard_info.py",
    "advanced_automation_utilities/keyboard/keyboard_physics.py",
    "advanced_automation_utilities/screen/screen.py",
    "advanced_automation_utilities/screen/screen_info.py",
    "advanced_automation_utilities/sound/sound.py",
    "advanced_automation_utilities/system/system.py",
    "advanced_automation_utilities/system/system_info.py",
    "advanced_automation_utilities/timing/timing.py",
    "advanced_automation_utilities/timing/timing_info.py",
    "advanced_automation_utilities/timing/measure_time.py",
    "advanced_automation_utilities/_task.py",
    "advanced_automation_utilities/_queueable_controller.py",
]
README_PATH = "README.md"
CONTRIBUTING_PATH = "CONTRIBUTING.md"
SECURITY_PATH = "SECURITY.md"
WIKI_HOME_PATH = "wiki/Home.md"
WIKI_FOOTER_PATH = "wiki/_Footer.md"
TEST_CONFIGURATION_PATH = "tests/conftest.py"
RUN_TESTS_SCRIPT_PATH = "scripts/run_tests.py"
COVERAGE_ANALYSIS_SCRIPT_PATH = "scripts/run_coverage_analysis.py"
PRE_COMMIT_CONFIGURATION_PATH = ".pre-commit-config.yaml"
UNIT_TESTS_WORKFLOW_PATH = ".github/workflows/unit_tests.yml"
WIKI_URL_PATTERN = re.compile(
    r"\]\(https://github\.com/GuidoGross/Advanced_Automation_Utilities/wiki/([^)]+)\)"
)
WIKI_HEADING_PATTERN = re.compile(r"^###\s+\*\*(?:`(?P<name>[^`]+)`|(?P<plain_name>[^*]+))\*\*\s*$")
SECTION_PATTERN = re.compile(r"^\*\*(?P<name>[A-Za-z][A-Za-z ]*):\*\*$")
TITLE_PATTERN = re.compile(r"^\*\*`(?P<name>[^`]+)`:\*\*\s*(?P<summary>.*)$")
ARGUMENT_PATTERN = re.compile(r"^\s*-\s*\*\*`(?P<name>[^`]+)`\s*\(`[^`]*`\)(?P<suffix>.*)$")
RETURN_PATTERN = re.compile(r"^\*\*`[^`]+`(?P<suffix>.*)$")

def main():
    start_time = time.perf_counter()
    header("Documentation Synchronization")
    parser = argparse.ArgumentParser(
        description = "Synchronize API names, signatures, types and docstring content with the wiki."
    )
    parser.add_argument(
        "--check", action = "store_true", help = "Verify synchronization without writing changes."
    )
    parsed_arguments = parser.parse_args()
    changed_files_paths = _sync_all(check_mode = parsed_arguments.check)
    if parsed_arguments.check:
        if changed_files_paths:
            print(
                f"{len(changed_files_paths)} files need synchronization:",
                color = "#ff0000",
                bold = True
            )
            _print_changed_files(changed_files_paths)
            return 1
        print("All docstrings and wiki files are already synchronized.", color = "#00ff00", bold = True)
        return 0
    else:
        if not changed_files_paths:
            print(
                "All docstrings and wiki files are already synchronized.",
                color = "#00ff00",
                bold = True
            )
            return 0
        print(f"Synchronized {len(changed_files_paths)} files:", bold = True)
        _print_changed_files(changed_files_paths)
    duration = (time.perf_counter() - start_time) * 1000
    print([
        ("Documentation synchronization completed successfully in:", {"bold": True}),
        (f" {decimal_format(duration, decimals = 0)}ms", {})
    ], color = "#00ff00")
    return 0

def _sync_all(check_mode = False, repository_root = Path.cwd()):
    changed_files = {}
    wiki_entities = {}
    source_updates = []
    for source_relative_path in SOURCE_FILES:
        source_path = repository_root / source_relative_path
        if not source_path.exists(): continue
        source = source_path.read_text(encoding = "utf-8")
        syntax_tree = ast.parse(source)
        line_offsets = _line_offsets(source)
        source_edits = []
        for node in syntax_tree.body:
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                wiki_relative_path = CLASS_SOURCE_TO_WIKI.get(source_relative_path)
                if wiki_relative_path is None: continue
                fields = _class_fields(node)
                class_docstring = ast.get_docstring(node, clean = False)
                updated_class_docstring = class_docstring
                if class_docstring:
                    updated_class_docstring = _sync_docstring(class_docstring, class_name, fields, None)
                    if updated_class_docstring != class_docstring:
                        source_edits.append(
                            _docstring_edit(node, updated_class_docstring, line_offsets, source)
                        )
                class_methods = wiki_entities.setdefault(wiki_relative_path, [])
                if PRIMARY_CLASS_SOURCE_BY_WIKI.get(wiki_relative_path) == source_relative_path and class_docstring:
                    class_methods.append(
                        {
                            "kind": "class_intro",
                            "name": class_name,
                            "docstring": updated_class_docstring
                        }
                    )
                elif source_relative_path in DATACLASS_SOURCE_FILES and class_docstring:
                    class_methods.append({
                        "kind": "class",
                        "name": class_name,
                        "docstring": updated_class_docstring,
                        "fields": fields,
                        "wiki_name": class_name,
                        "alias": _docstring_name(class_docstring) or class_name
                    })
                for member_node in node.body:
                    if not isinstance(member_node, (ast.FunctionDef, ast.AsyncFunctionDef)): continue
                    if member_node.name.startswith("_") and member_node.name != "__init__": continue
                    docstring = ast.get_docstring(member_node, clean = False)
                    if not docstring: continue
                    parameters = _function_parameters(member_node.args)
                    return_type = _type_to_string(member_node.returns)
                    updated_docstring = _sync_docstring(
                        docstring,
                        _api_name(class_name, member_node),
                        parameters,
                        return_type,
                        ensure_title = member_node.name != "__init__"
                    )
                    if updated_docstring != docstring:
                        source_edits.append(
                            _docstring_edit(member_node, updated_docstring, line_offsets, source)
                        )
                    if member_node.name == "__init__": continue
                    class_methods.append({
                        "kind": "function",
                        "name": member_node.name,
                        "docstring": updated_docstring,
                        "parameters": parameters,
                        "return_type": return_type,
                        "wiki_name": _api_name(class_name, member_node),
                        "alias": _docstring_name(docstring) or _api_name(class_name, member_node)
                    })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_mapping = FUNCTION_TO_WIKI.get(node.name)
                docstring = ast.get_docstring(node, clean = False)
                if function_mapping is None or not docstring: continue
                wiki_relative_path, wiki_name = function_mapping
                parameters = _function_parameters(node.args)
                return_type = _type_to_string(node.returns)
                updated_docstring = _sync_docstring(
                    docstring, wiki_name, parameters, return_type, ensure_title = True
                )
                if updated_docstring != docstring:
                    source_edits.append(_docstring_edit(node, updated_docstring, line_offsets, source))
                wiki_entities.setdefault(wiki_relative_path, []).append({
                    "kind": "function",
                    "name": node.name,
                    "docstring": updated_docstring,
                    "parameters": parameters,
                    "return_type": return_type,
                    "wiki_name": wiki_name,
                    "alias": _docstring_name(docstring) or wiki_name
                })
        if source_edits:
            updated_source = _apply_edits(source, source_edits)
            if updated_source != source:
                relative_path = source_path.relative_to(repository_root)
                changed_files[str(relative_path)] = _changed_line_numbers(source, updated_source)
                source_updates.append((source_path, updated_source))
    for wiki_relative_path, entities in wiki_entities.items():
        wiki_path = repository_root / wiki_relative_path
        if not wiki_path.exists(): continue
        original_wiki = wiki_path.read_text(encoding = "utf-8")
        updated_wiki = _sync_wiki_file(original_wiki, wiki_relative_path, entities)
        updated_wiki = _remove_excluded_wiki_sections(
            updated_wiki, WIKI_EXCLUDED_ENTITIES.get(wiki_relative_path, set())
        )
        if updated_wiki != original_wiki:
            relative_path = wiki_path.relative_to(repository_root)
            changed_files[str(relative_path)] = _changed_line_numbers(original_wiki, updated_wiki)
            if not check_mode: wiki_path.write_text(updated_wiki, encoding = "utf-8")
    if not check_mode:
        for source_path, updated_source in source_updates:
            source_path.write_text(updated_source, encoding = "utf-8")
    _sync_project_documentation(repository_root, check_mode, changed_files)
    return dict(sorted(changed_files.items()))

def _sync_project_documentation(repository_root, check_mode, changed_files):
    profiles, default_profile, pre_commit_profile, post_commit_profile = (
        _sync_hypothesis_profiles(repository_root, check_mode, changed_files)
    )
    configuration_path = repository_root / "pyproject.toml"
    configuration = tomllib.loads(configuration_path.read_text(encoding = "utf-8"))
    project = configuration["project"]
    readme_path = repository_root / README_PATH
    original_readme = readme_path.read_text(encoding = "utf-8")
    updated_readme = _sync_readme_requirements(original_readme, project, configuration)
    if updated_readme != original_readme:
        _record_file_update(
            repository_root, readme_path, original_readme, updated_readme, check_mode, changed_files
        )
    updated_home = _home_from_readme(updated_readme)
    home_path = repository_root / WIKI_HOME_PATH
    original_home = home_path.read_text(encoding = "utf-8")
    if updated_home != original_home:
        _record_file_update(
            repository_root, home_path, original_home, updated_home, check_mode, changed_files
        )
    footer_path = repository_root / WIKI_FOOTER_PATH
    original_footer = footer_path.read_text(encoding = "utf-8")
    updated_footer = _extract_markdown_section(updated_readme, "## **Support**")
    if updated_footer != original_footer:
        _record_file_update(
            repository_root, footer_path, original_footer, updated_footer, check_mode, changed_files
        )
    security_path = repository_root / SECURITY_PATH
    original_security = security_path.read_text(encoding = "utf-8")
    updated_security = _sync_security_email(original_security, project)
    if updated_security != original_security:
        _record_file_update(
            repository_root,
            security_path,
            original_security,
            updated_security,
            check_mode,
            changed_files
        )
    contributing_path = repository_root / CONTRIBUTING_PATH
    original_contributing = contributing_path.read_text(encoding = "utf-8")
    updated_contributing = _sync_contributing(
        original_contributing,
        updated_readme,
        profiles,
        default_profile,
        pre_commit_profile,
        post_commit_profile
    )
    if updated_contributing != original_contributing:
        _record_file_update(
            repository_root,
            contributing_path,
            original_contributing,
            updated_contributing,
            check_mode,
            changed_files
        )

def _class_fields(class_node):
    fields = {}
    for member_node in class_node.body:
        if isinstance(member_node, ast.AnnAssign) and isinstance(member_node.target, ast.Name):
            fields[member_node.target.id] = _type_to_string(member_node.annotation)
    return fields

def _function_parameters(arguments):
    parameters = {}
    positional_arguments = arguments.posonlyargs + arguments.args
    for argument in positional_arguments:
        if argument.arg not in ("self", "cls"):
            parameters[argument.arg] = _type_to_string(argument.annotation)
    if arguments.vararg is not None:
        parameters[f"*{arguments.vararg.arg}"] = _type_to_string(arguments.vararg.annotation)
    for argument in arguments.kwonlyargs:
        parameters[argument.arg] = _type_to_string(argument.annotation)
    if arguments.kwarg is not None:
        parameters[f"**{arguments.kwarg.arg}"] = _type_to_string(arguments.kwarg.annotation)
    return parameters

def _type_to_string(annotation_node):
    if annotation_node is None: return "Any"
    return ast.unparse(annotation_node)

def _api_name(class_name, function_node):
    is_property = any(
        isinstance(decorator, ast.Name) and decorator.id == "property"
        for decorator in function_node.decorator_list
    )
    if class_name == "_QueueableController": return f"{function_node.name}()"
    if is_property: return f"{class_name}().{function_node.name}"
    return f"{class_name}().{function_node.name}()"

def _normalized_docstring_lines(docstring):
    lines = docstring.splitlines()
    while lines and not lines[0].strip(): lines.pop(0)
    while lines and not lines[-1].strip(): lines.pop()
    if not lines: return []
    indentation_candidates = [len(line) - len(line.lstrip()) for line in lines[1:] if line.strip()]
    if indentation_candidates:
        indentation = min(indentation_candidates)
        if indentation:
            lines = [
                line[indentation:] if line.startswith(" " * indentation) else line for line in lines
            ]
    else: lines = [line.lstrip() for line in lines]
    return lines

def _trim_blank_lines(lines):
    start_index = 0
    end_index = len(lines)
    while start_index < end_index and not lines[start_index].strip(): start_index += 1
    while end_index > start_index and not lines[end_index - 1].strip(): end_index -= 1
    return lines[start_index:end_index]

def _docstring_name(docstring):
    lines = _normalized_docstring_lines(docstring)
    if not lines: return None
    title_match = TITLE_PATTERN.match(lines[0].strip())
    return title_match.group("name") if title_match else None

def _parse_docstring(docstring):
    lines = _normalized_docstring_lines(docstring)
    title = None
    summary = None
    if lines:
        title_match = TITLE_PATTERN.match(lines[0].strip())
        if title_match:
            title = title_match.group("name")
            summary = title_match.group("summary")
            lines = lines[1:]
    sections = []
    section_name = None
    section_lines = []
    preamble = []
    for line in lines:
        section_match = SECTION_PATTERN.match(line.strip())
        if section_match:
            if section_name is not None:
                sections.append((section_name, _trim_blank_lines(section_lines)))
            elif _trim_blank_lines(section_lines): preamble = _trim_blank_lines(section_lines)
            section_name = section_match.group("name")
            section_lines = []
        else: section_lines.append(line)
    if section_name is not None: sections.append((section_name, _trim_blank_lines(section_lines)))
    elif _trim_blank_lines(section_lines): preamble = _trim_blank_lines(section_lines)
    return title, summary, preamble, sections

def _sync_docstring(docstring, api_name, parameters, return_type, ensure_title = False):
    title, summary, preamble, sections = _parse_docstring(docstring)
    updated_title = api_name if title is not None or ensure_title else None
    updated_sections = []
    found_arguments = False
    found_returns = False
    for section_name, section_lines in sections:
        if section_name == "Arguments":
            found_arguments = True
            section_lines = _sync_argument_lines(section_lines, parameters)
        elif section_name == "Returns":
            found_returns = True
            section_lines = _sync_return_lines(section_lines, return_type)
        updated_sections.append((section_name, section_lines))
    if parameters and not found_arguments:
        arguments_section = ("Arguments", _sync_argument_lines([], parameters))
        insertion_index = next(
            (index + 1 for index, (name, _) in enumerate(updated_sections) if name == "Description"),
            len(updated_sections)
        )
        updated_sections.insert(insertion_index, arguments_section)
    if return_type is not None and not found_returns:
        returns_section = ("Returns", [f"**`{return_type}`**"])
        insertion_index = next(
            (index for index, (name, _) in enumerate(updated_sections) if name == "Example"),
            len(updated_sections)
        )
        updated_sections.insert(insertion_index, returns_section)
    rendered_lines = []
    if updated_title is not None:
        rendered_lines.append(f"**`{updated_title}`:** {summary or ""}".rstrip())
    if preamble:
        if rendered_lines: rendered_lines.append("")
        rendered_lines.extend(preamble)
    for section_name, section_lines in updated_sections:
        if rendered_lines: rendered_lines.append("")
        rendered_lines.append(f"**{section_name}:**")
        if section_lines:
            rendered_lines.append("")
            rendered_lines.extend(section_lines)
    return "\n".join(rendered_lines)

def _sync_argument_lines(lines, parameters):
    descriptions = {}
    for line in lines:
        argument_match = ARGUMENT_PATTERN.match(line)
        if argument_match: descriptions[argument_match.group("name")] = argument_match.group("suffix")
    updated_lines = []
    for parameter_name, parameter_type in parameters.items():
        suffix = descriptions.get(parameter_name, "")
        updated_lines.append(
            f"- **`{parameter_name}` (`{parameter_type}`){_format_argument_suffix(suffix)}"
        )
    return updated_lines

def _format_argument_suffix(suffix):
    if suffix.startswith(":**"): return suffix
    if suffix.startswith("**"): return suffix
    description = suffix.strip()
    if description: return f":** {description}"
    return "**"

def _sync_return_lines(lines, return_type):
    if not lines: return [f"**`{return_type}`**"]
    return_matches = [(index, RETURN_PATTERN.match(line.strip())) for index, line in enumerate(lines)]
    return_matches = [(index, match) for index, match in return_matches if match]
    if not return_matches: return [f"**`{return_type}`**", *lines]
    descriptive_match = next(
        ((index, match) for index, match in return_matches if match.group("suffix").startswith(":**")),
        return_matches[0]
    )
    _, description_match = descriptive_match
    updated_lines = [f"**`{return_type}`{description_match.group("suffix")}"]
    updated_lines.extend(
        line for index, line in enumerate(lines)
        if index not in {match_index for match_index, _ in return_matches}
    )
    return updated_lines

def _render_docstring(docstring):
    _, summary, preamble, sections = _parse_docstring(docstring)
    rendered_lines = []
    if summary: rendered_lines.append(summary)
    elif preamble: rendered_lines.extend(preamble)
    for section_name, section_lines in sections:
        if rendered_lines: rendered_lines.append("")
        if section_name in ("Note", "Tip", "Warning", "Important", "Caution"):
            rendered_lines.extend(_render_alert(section_name, section_lines))
        else:
            rendered_lines.append(f"**{section_name}:**")
            if section_lines:
                rendered_lines.append("")
                rendered_lines.extend(section_lines)
    return "\n".join(rendered_lines).strip()

def _render_alert(alert_type, lines):
    rendered_lines = [f"> [!{alert_type.upper()}]"]
    rendered_lines.extend(f"> {line}" if line else ">" for line in lines)
    return rendered_lines

def _sync_wiki_file(content, wiki_relative_path, entities):
    lines = content.splitlines()
    sections = _wiki_sections(lines)
    updated_lines = list(lines)
    missing_entities = []
    for entity in entities:
        if entity["kind"] == "class_intro":
            updated_lines = _sync_class_intro(updated_lines, entity)
            continue
        if entity["kind"] == "class":
            updated_lines = _sync_dataclass_section(updated_lines, entity)
            continue
        matching_sections = _find_entity_sections(sections, entity)
        if not matching_sections:
            missing_entities.append(entity)
            continue
        for duplicate_start, duplicate_end in reversed(matching_sections[1:]):
            removal_start = duplicate_start
            while removal_start > 0 and not updated_lines[removal_start - 1].strip(): removal_start -= 1
            if removal_start > 0 and updated_lines[removal_start - 1].strip() == "---":
                removal_start -= 1
            updated_lines[removal_start:duplicate_end] = []
        sections = _wiki_sections(updated_lines)
        start_index, end_index = _find_entity_sections(sections, entity)[0]
        section = _render_docstring(entity["docstring"])
        replacement = [f"### **`{entity["wiki_name"]}`**"]
        if section: replacement.extend(["", *section.splitlines()])
        updated_lines[start_index:end_index] = replacement
        sections = _wiki_sections(updated_lines)
    for entity in missing_entities:
        section = _render_docstring(entity["docstring"])
        block = [f"### **`{entity["wiki_name"]}`**"]
        if section: block.extend(["", *section.splitlines()])
        if updated_lines and updated_lines[-1].strip(): updated_lines.extend(["", "---", ""])
        updated_lines.extend(block)
    updated_lines = _collapse_blank_lines(updated_lines)
    while updated_lines and not updated_lines[-1].strip(): updated_lines.pop()
    return "\n".join(updated_lines) + ("\n" if content.endswith("\n") else "")

def _wiki_sections(lines):
    sections = []
    for line_index, line in enumerate(lines):
        heading_match = WIKI_HEADING_PATTERN.match(line)
        if heading_match is None: continue
        end_index = line_index + 1
        while end_index < len(lines) and not lines[end_index].startswith(("### ", "## ")):
            end_index += 1
        content_end_index = end_index
        while content_end_index > line_index + 1 and not lines[content_end_index - 1].strip():
            content_end_index -= 1
        if content_end_index > line_index + 1 and lines[content_end_index - 1].strip() == "---":
            content_end_index -= 1
            while content_end_index > line_index + 1 and not lines[content_end_index - 1].strip():
                content_end_index -= 1
        section_name = heading_match.group("name") or heading_match.group("plain_name")
        sections.append((line_index, content_end_index, section_name))
    return sections

def _find_entity_sections(sections, entity):
    possible_names = {
        _normalize_entity_name(entity["wiki_name"]),  _normalize_entity_name(entity["alias"])
    }
    return [
        (start_index, end_index) for start_index, end_index, section_name in sections
        if _normalize_entity_name(section_name) in possible_names
    ]

def _normalize_entity_name(entity_name): return re.sub(r"(?<=[A-Za-z0-9_])\(\)\.", ".", entity_name)

def _remove_excluded_wiki_sections(content, excluded_names):
    if not excluded_names: return content
    lines = content.splitlines()
    normalized_excluded_names = {_normalize_entity_name(name) for name in excluded_names}
    for start_index, end_index, section_name in reversed(_wiki_sections(lines)):
        if _normalize_entity_name(section_name) not in normalized_excluded_names: continue
        removal_start = start_index
        while removal_start > 0 and not lines[removal_start - 1].strip(): removal_start -= 1
        if removal_start > 0 and lines[removal_start - 1].strip() == "---": removal_start -= 1
        lines[removal_start:end_index] = []
    while lines and not lines[-1].strip(): lines.pop()
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

def _sync_class_intro(lines, entity):
    _, _, _, sections = _parse_docstring(entity["docstring"])
    description = next(
        (section_lines for section_name, section_lines in sections if section_name == "Description"), []
    )
    if not description: return lines
    try:
        container_start = next(index for index, line in enumerate(lines) if line.startswith("<div"))
        container_end = next(
            index for index in range(container_start + 1, len(lines))
            if lines[index].startswith("</div>")
        )
    except StopIteration: return lines
    for line_index in range(container_start + 1, container_end):
        if lines[line_index].startswith("# **"):
            lines[line_index] = f"# **{entity["name"]}**"
            break
    for line_index in range(container_start + 1, container_end):
        if lines[line_index].startswith("**") and lines[line_index].endswith("**"):
            lines[line_index] = f"**{" ".join(description)}**"
            break
    return lines

def _sync_dataclass_section(lines, entity):
    existing_sections = [
        index for index, line in enumerate(lines)
        if line in {f"## **{entity["name"]}**", f"## **{entity["alias"]}**"}
    ]
    section_lines = _render_docstring(entity["docstring"])
    replacement = [f"## **{entity["name"]}**"]
    if section_lines: replacement.extend(["", *section_lines.splitlines()])
    if existing_sections:
        start_index = existing_sections[0]
        end_index = next(
            (index for index in range(start_index + 1, len(lines)) if lines[index].startswith("## ")),
            len(lines)
        )
        replacement_end_index = end_index
        while replacement_end_index > start_index and not lines[replacement_end_index - 1].strip():
            replacement_end_index -= 1
        if replacement_end_index > start_index and lines[replacement_end_index - 1].strip() == "---":
            replacement_end_index -= 1
            while replacement_end_index > start_index and not lines[replacement_end_index - 1].strip():
                replacement_end_index -= 1
        lines[start_index:replacement_end_index] = replacement
    else:
        if lines and lines[-1].strip(): lines.extend(["", "---", ""])
        lines.extend(replacement)
    return lines

def _collapse_blank_lines(lines):
    collapsed_lines = []
    for line in lines:
        if not line.strip() and collapsed_lines and not collapsed_lines[-1].strip(): continue
        collapsed_lines.append(line)
    return collapsed_lines

def _sync_readme_requirements(readme, project, configuration):
    operating_system_heading = "### **Operating System**"
    operating_system_requirements = _markdown_section_body(readme, operating_system_heading)
    dependency_note = _extract_dependency_note(readme)
    python_version = _minimum_python_version(project["requires-python"])
    requirements = "\n\n".join([
        "## **Requirements**",
        _render_dependency_sections(project, configuration, dependency_note),
        f"### **Python version**\n\nPython {python_version} or higher",
        f"{operating_system_heading}\n\n{operating_system_requirements}"
    ])
    updated_readme = _replace_markdown_section(
        readme, "## **Requirements**", requirements, stop_at = "## **Installation**"
    )
    return re.sub(
        r"(Python_version-%E2%89%A5_v)\d+(?:\.\d+)*(-blue)",
        rf"\g<1>{python_version}\g<2>",
        updated_readme
    )

def _extract_dependency_note(readme):
    lines = readme.splitlines()
    dependencies_heading = next(
        (index for index, line in enumerate(lines) if line == "### **Dependencies**"), None
    )
    python_version_heading = next(
        (index for index, line in enumerate(lines) if line == "### **Python version**"), None
    )
    if dependencies_heading is None or python_version_heading is None: return []
    note_start = next(
        (
            index for index in range(dependencies_heading + 1, python_version_heading)
            if lines[index] == "> [!NOTE]"
        ),
        None
    )
    if note_start is None: return []
    note_end = note_start + 1
    while note_end < python_version_heading and lines[note_end].startswith(">"): note_end += 1
    return lines[note_start:note_end]

def _render_dependency_sections(project, configuration, dependency_note):
    lines = ["### **Dependencies**", ""]
    lines.extend(
        f"- {_render_requirement(dependency)}" for dependency in project.get("dependencies", [])
    )
    lines.extend(["", "### **Optional dependencies**", ""])
    optional_dependencies = project.get("optional-dependencies", {})
    lines.extend(
        f"- {_render_requirement(dependency)}"
        for dependencies in optional_dependencies.values() for dependency in dependencies
    )
    if dependency_note: lines.extend(["", *dependency_note])
    build_requirements = configuration["build-system"].get("requires", [])
    if build_requirements:
        lines.extend(["", "### **Setuptools version**", ""])
        lines.extend(
            f"Setuptools {_minimum_requirement_version(requirement)}"
            for requirement in build_requirements
        )
    return "\n".join(lines)

def _render_requirement(requirement):
    requirement_match = re.fullmatch(
        r"\s*(?P<name>[A-Za-z0-9._-]+)\s*>=\s*(?P<version>[^\s;]+)\s*", requirement
    )
    if requirement_match is None: raise ValueError(f"Unsupported requirement format: {requirement}")
    return f"`{requirement_match.group("name")}` (v{requirement_match.group("version")} or higher)"

def _minimum_requirement_version(requirement):
    requirement_match = re.fullmatch(
        r"\s*setuptools\s*>=\s*(?P<version>[^\s;]+)\s*", requirement, re.IGNORECASE
    )
    if requirement_match is None:
        raise ValueError(f"Unsupported build requirement format: {requirement}")
    return f"{requirement_match.group("version")} or higher"

def _minimum_python_version(requires_python):
    version_match = re.fullmatch(r">=\s*(\d+(?:\.\d+)*)", requires_python)
    if version_match is None: raise ValueError(f"Unsupported requires-python value: {requires_python}")
    return version_match.group(1)

def _sync_contributing(
    contributing, readme, profiles, default_profile, pre_commit_profile, post_commit_profile
):
    contributing = _remove_lines_starting_with(
        contributing, "For questions about contributing, contact "
    )
    contributing = _remove_extra_blank_lines_after(contributing, "</div>")
    operating_system = _markdown_section_body(readme, "### **Operating System**").rstrip(".")
    python_version = _markdown_section_body(readme, "### **Python version**")
    support_sentence = (
        f"The library supports {operating_system} and {python_version}. Clone the repository and change to its directory:"
    )
    contributing = _replace_line_starting_with(contributing, "The library supports ", support_sentence)
    profile_names = tuple(profiles)
    profile_note = (
        f"> The test runner uses the `{default_profile}` profile by default ({decimal_format(profiles[default_profile], decimals = 0)} examples). The pre-commit hook uses the `{pre_commit_profile}` profile ({decimal_format(profiles[pre_commit_profile], decimals = 0)} examples). The GitHub Actions workflow uses the `{post_commit_profile}` profile ({decimal_format(profiles[post_commit_profile], decimals = 0)} examples)."
    )
    contributing = _replace_line_starting_with(
        contributing, "> The test runner uses the ", profile_note
    )
    contributing = _replace_profile_instructions(
        contributing, tuple(dict.fromkeys(profile_names)), default_profile
    )
    return contributing

def _sync_security_email(security, project):
    author_email = next(
        (author["email"] for author in project.get("authors", []) if author.get("email")), None
    )
    if author_email is None: raise ValueError("The project must declare an author email.")
    lines = security.splitlines()
    reporting_line_index = next(
        (
            index for index, line in enumerate(lines)
            if line.startswith("Please do not report security vulnerabilities in a public")
        ),
        None
    )
    if reporting_line_index is None:
        raise ValueError("Could not find the vulnerability reporting contact in SECURITY.md.")
    updated_line, replacements = re.subn(
        r"\[[^\]]+\]\(mailto:[^)]+\)",
        f"[{author_email}](mailto:{author_email})",
        lines[reporting_line_index]
    )
    if replacements != 1:
        raise ValueError("Expected one maintainer email in SECURITY.md vulnerability reporting text.")
    lines[reporting_line_index] = updated_line
    return "\n".join(lines) + ("\n" if security.endswith("\n") else "")

def _hypothesis_profiles(configuration_path):
    syntax_tree = ast.parse(configuration_path.read_text(encoding = "utf-8"))
    profiles = {}
    calls = sorted(ast.walk(syntax_tree), key = lambda node: getattr(node, "lineno", 0))
    for node in calls:
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "register_profile" or not isinstance(node.func.value, ast.Name) or node.func.value.id != "settings" or not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        profile_name = node.args[0].value
        maximum_examples = next(
            (keyword.value for keyword in node.keywords if keyword.arg == "max_examples"), None
        )
        if not isinstance(profile_name, str) or maximum_examples is None: continue
        profiles[profile_name] = ast.literal_eval(maximum_examples)
    return profiles

def _default_hypothesis_profile(configuration_path):
    syntax_tree = ast.parse(configuration_path.read_text(encoding = "utf-8"))
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "load_profile" and isinstance(node.func.value, ast.Name) and node.func.value.id == "settings" and node.args and isinstance(node.args[0], ast.Call) and isinstance(node.args[0].func, ast.Attribute) and node.args[0].func.attr == "getenv" and len(node.args[0].args) > 1 and isinstance(node.args[0].args[1], ast.Constant) and isinstance(node.args[0].args[1].value, str):
            return node.args[0].args[1].value
    raise ValueError(f"Could not determine the default Hypothesis profile in {configuration_path}.")

def _configured_hypothesis_profile(configuration_path):
    configuration = configuration_path.read_text(encoding = "utf-8")
    profile_match = re.search(r"--hypothesis-profile\s+([A-Za-z0-9_-]+)", configuration)
    if profile_match is None:
        raise ValueError(f"Could not find a configured Hypothesis profile in {configuration_path}.")
    return profile_match.group(1)

def _sync_hypothesis_profiles(repository_root, check_mode, changed_files):
    test_configuration_path = repository_root / TEST_CONFIGURATION_PATH
    profiles = _hypothesis_profiles(test_configuration_path)
    default_profile = _default_hypothesis_profile(test_configuration_path)
    if default_profile not in profiles:
        raise ValueError(
            f"Default Hypothesis profile {default_profile!r} is missing from {test_configuration_path}."
        )
    hook_path = repository_root / PRE_COMMIT_CONFIGURATION_PATH
    workflow_path = repository_root / UNIT_TESTS_WORKFLOW_PATH
    configured_hook_profile = _configured_hypothesis_profile(hook_path)
    configured_workflow_profile = _configured_hypothesis_profile(workflow_path)
    pre_commit_profile = (
        configured_hook_profile if configured_hook_profile in profiles else None
    )
    post_commit_profile = (
        configured_workflow_profile if configured_workflow_profile in profiles else None
    )
    remaining_profiles = [
        profile for profile in profiles
        if profile != default_profile and profile not in {pre_commit_profile, post_commit_profile}
    ]
    if pre_commit_profile is None and remaining_profiles:
        pre_commit_profile = remaining_profiles.pop(0)
    if post_commit_profile is None and remaining_profiles:
        post_commit_profile = remaining_profiles.pop()
    if pre_commit_profile is None or post_commit_profile is None or pre_commit_profile == post_commit_profile:
        raise ValueError(
            f"Expected a default, pre-commit, and workflow Hypothesis profile in {test_configuration_path}; found {list(profiles)}."
        )
    _sync_profile_argument(
        repository_root, PRE_COMMIT_CONFIGURATION_PATH, pre_commit_profile,
        r"(--hypothesis-profile\s+)[A-Za-z0-9_-]+", check_mode, changed_files
    )
    for relative_path in (RUN_TESTS_SCRIPT_PATH, COVERAGE_ANALYSIS_SCRIPT_PATH):
        _sync_profile_runner(
            repository_root, relative_path, profiles, default_profile, check_mode, changed_files
        )
    workflow_path = repository_root / UNIT_TESTS_WORKFLOW_PATH
    original_workflow = workflow_path.read_text(encoding = "utf-8")
    updated_workflow, profile_replacements = re.subn(
        r"(--hypothesis-profile\s+)[A-Za-z0-9_-]+",
        lambda match: f"{match.group(1)}{post_commit_profile}",
        original_workflow,
        count = 1
    )
    updated_workflow, count_replacements = re.subn(
        r"(?m)^([ \t]*-[ \t]*name: Run unit tests with ).* Hypothesis examples$",
        lambda match: (
            f"{match.group(1)}{decimal_format(profiles[post_commit_profile], decimals = 0)} Hypothesis examples"
        ),
        updated_workflow
    )
    if profile_replacements != 1 or count_replacements != 1:
        raise ValueError(f"Could not update the Hypothesis profile in {workflow_path}.")
    if updated_workflow != original_workflow:
        _record_file_update(
            repository_root,
            workflow_path,
            original_workflow,
            updated_workflow,
            check_mode,
            changed_files
        )
    return profiles, default_profile, pre_commit_profile, post_commit_profile

def _sync_profile_argument(
    repository_root, relative_path, profile, pattern, check_mode, changed_files
):
    configuration_path = repository_root / relative_path
    original_configuration = configuration_path.read_text(encoding = "utf-8")
    updated_configuration, replacements = re.subn(
        pattern,
        lambda match: f"{match.group(1)}{profile}",
        original_configuration,
        count = 1
    )
    if replacements != 1:
        raise ValueError(f"Could not find a Hypothesis profile argument in {configuration_path}.")
    if updated_configuration != original_configuration:
        _record_file_update(
            repository_root,
            configuration_path,
            original_configuration,
            updated_configuration,
            check_mode,
            changed_files
        )

def _sync_profile_runner(
    repository_root, relative_path, profiles, default_profile, check_mode, changed_files
):
    runner_path = repository_root / relative_path
    original_runner = runner_path.read_text(encoding = "utf-8")
    profile_tuple = "(" + ", ".join(f'"{profile}"' for profile in profiles)
    if len(profiles) == 1: profile_tuple += ","
    profile_tuple += ")"
    updated_runner, profile_replacements = re.subn(
        r"(?m)^HYPOTHESIS_PROFILES = \([^\n]*\)$",
        f"HYPOTHESIS_PROFILES = {profile_tuple}",
        original_runner
    )
    updated_runner, default_replacements = re.subn(
        r'(parser\.add_argument\("--hypothesis-profile", choices = HYPOTHESIS_PROFILES, default = ")[^"]+("\))',
        lambda match: f"{match.group(1)}{default_profile}{match.group(2)}",
        updated_runner
    )
    if profile_replacements != 1 or default_replacements != 1:
        raise ValueError(f"Could not update Hypothesis profile options in {runner_path}.")
    if updated_runner != original_runner:
        _record_file_update(
            repository_root, runner_path, original_runner, updated_runner, check_mode, changed_files
        )

def _replace_profile_instructions(content, profiles, default_profile):
    lines = content.splitlines()
    heading = "**To run each profile locally:**"
    stop_heading = "**To run the full test suite with line and branch coverage:**"
    start_index = next((index for index, line in enumerate(lines) if line == heading), None)
    if start_index is None: raise ValueError(f"Could not find CONTRIBUTING.md heading: {heading}")
    end_index = next(
        (index for index in range(start_index + 1, len(lines)) if lines[index] == stop_heading), None
    )
    if end_index is None: raise ValueError(f"Could not find CONTRIBUTING.md heading: {stop_heading}")
    profile_lines = []
    for profile in profiles:
        profile_lines.extend([
            f"- **`{profile}`:**",
            "",
            "    ```powershell",
            (
                "    python .\\scripts\\run_tests.py"
                if profile == default_profile
                else f"    python .\\scripts\\run_tests.py --hypothesis-profile {profile}"
            ),
            "    ```",
        ])
    lines[start_index + 1:end_index] = ["", *profile_lines, ""]
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

def _replace_line_starting_with(content, prefix, replacement):
    lines = content.splitlines()
    line_index = next((index for index, line in enumerate(lines) if line.startswith(prefix)), None)
    if line_index is None:
        raise ValueError(f"Could not find CONTRIBUTING.md line starting with: {prefix}")
    lines[line_index] = replacement
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

def _remove_lines_starting_with(content, prefix):
    lines = content.splitlines()
    matching_line = next((index for index, line in enumerate(lines) if line.startswith(prefix)), None)
    if matching_line is not None:
        del lines[matching_line]
        while matching_line < len(lines) and matching_line > 0 and not lines[matching_line].strip() and not lines[matching_line - 1].strip():
            del lines[matching_line]
    while lines and not lines[-1].strip(): lines.pop()
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

def _remove_extra_blank_lines_after(content, preceding_line):
    lines = content.splitlines()
    for line_index, line in enumerate(lines):
        if line.strip() != preceding_line: continue
        blank_line_index = line_index + 1
        while blank_line_index + 1 < len(lines) and not lines[blank_line_index].strip() and not lines[blank_line_index + 1].strip():
            del lines[blank_line_index]
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

def _replace_markdown_section(content, heading, replacement, stop_at = None):
    lines = content.splitlines()
    start_index = next((index for index, line in enumerate(lines) if line == heading), None)
    if start_index is None: raise ValueError(f"Could not find Markdown section: {heading}")
    heading_level = len(heading) - len(heading.lstrip("#"))
    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if stop_at is not None and line == stop_at:
            end_index = index
            break
        if line.startswith("#"):
            next_heading_level = len(line) - len(line.lstrip("#"))
            if next_heading_level <= heading_level:
                end_index = index
                break
    replacement_lines = replacement.splitlines()
    if end_index < len(lines): replacement_lines.append("")
    lines[start_index:end_index] = replacement_lines
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

def _extract_markdown_section(content, heading):
    lines = content.splitlines()
    start_index = next((index for index, line in enumerate(lines) if line == heading), None)
    if start_index is None: raise ValueError(f"Could not find Markdown section: {heading}")
    heading_level = len(heading) - len(heading.lstrip("#"))
    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= heading_level:
            end_index = index
            break
    while end_index > start_index + 1 and not lines[end_index - 1].strip(): end_index -= 1
    return "\n".join(lines[start_index:end_index])

def _markdown_section_body(content, heading):
    lines = content.splitlines()
    start_index = next((index for index, line in enumerate(lines) if line == heading), None)
    if start_index is None: raise ValueError(f"Could not find Markdown section: {heading}")
    heading_level = len(heading) - len(heading.lstrip("#"))
    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= heading_level:
            end_index = index
            break
    body_start_index = start_index + 1
    while body_start_index < end_index and not lines[body_start_index].strip(): body_start_index += 1
    while end_index > start_index + 1 and not lines[end_index - 1].strip(): end_index -= 1
    return "\n".join(lines[body_start_index:end_index])

def _home_from_readme(readme):
    home = _remove_markdown_section(readme, "## **Support**")
    home = re.sub(
        r"^The full documentation, API references, and examples are in the \*\*\[GitHub Wiki\]\(https://github\.com/GuidoGross/Advanced_Automation_Utilities/wiki\)\*\*\.\n(?:\n)?",
        "",
        home,
        flags = re.MULTILINE
    )
    return WIKI_URL_PATTERN.sub(r"](\1)", home)

def _remove_markdown_section(content, heading):
    lines = content.splitlines()
    start_index = next((index for index, line in enumerate(lines) if line == heading), None)
    if start_index is None: raise ValueError(f"Could not find Markdown section: {heading}")
    heading_level = len(heading) - len(heading.lstrip("#"))
    end_index = len(lines)
    for index in range(start_index + 1, len(lines)):
        line = lines[index]
        if line.startswith("#") and len(line) - len(line.lstrip("#")) <= heading_level:
            end_index = index
            break
    removal_start = start_index
    while removal_start > 0 and not lines[removal_start - 1].strip(): removal_start -= 1
    lines[removal_start:end_index] = []
    return "\n".join(lines) + ("\n" if content.endswith("\n") else "")

def _docstring_edit(node, updated_docstring, line_offsets, source):
    expression = node.body[0]
    literal_node = expression.value
    start_offset = line_offsets[literal_node.lineno - 1] + literal_node.col_offset
    end_offset = line_offsets[literal_node.end_lineno - 1] + literal_node.end_col_offset
    literal = source[start_offset:end_offset]
    quote_match = re.match(r"(?i:[rub]*)('''|\"\"\"|'|\")", literal)
    if quote_match is None:
        raise ValueError(f"Unsupported docstring literal at line {literal_node.lineno}.")
    quote = quote_match.group(1)
    prefix = literal[:len(literal) - len(literal.lstrip("rRuUbB"))]
    indentation = " " * literal_node.col_offset
    updated_literal = prefix + _render_docstring_literal(updated_docstring, indentation, quote)
    return start_offset, end_offset, updated_literal

def _render_docstring_literal(docstring, indentation, quote):
    normalized_docstring = textwrap.dedent(docstring).strip()
    docstring_lines = normalized_docstring.splitlines()
    indented_lines = [f"{indentation}{line}" if line else "" for line in docstring_lines]
    return f"{quote}\n" + "\n".join(indented_lines) + f"\n{indentation}{quote}"

def _line_offsets(source):
    offsets = [0]
    for line in source.splitlines(keepends = True): offsets.append(offsets[-1] + len(line))
    return offsets

def _apply_edits(source, edits):
    for start_offset, end_offset, replacement in sorted(edits, reverse = True):
        source = source[:start_offset] + replacement + source[end_offset:]
    return source

def _record_file_update(
    repository_root, path, original_content, updated_content, check_mode, changed_files
):
    changed_files[str(path.relative_to(repository_root))] = _changed_line_numbers(
        original_content, updated_content
    )
    if not check_mode: path.write_text(updated_content, encoding = "utf-8")

def _changed_line_numbers(original_content, updated_content):
    original_lines = original_content.splitlines()
    updated_lines = updated_content.splitlines()
    changed_lines = set()
    matcher = difflib.SequenceMatcher(a = original_lines, b = updated_lines, autojunk = False)
    for operation, original_start, original_end, updated_start, updated_end in matcher.get_opcodes():
        if operation == "equal": continue
        if updated_start != updated_end:
            changed_lines.update((line_number, False) for line_number in range(
                updated_start + 1, updated_end + 1
            ))
        else:
            changed_lines.update((line_number, True) for line_number in range(
                original_start + 1, original_end + 1
            ))
    return sorted(changed_lines)

def _print_changed_files(changed_files):
    for changed_file_path, changed_lines in changed_files.items():
        print(f"  - {changed_file_path}", bold = True)
        for line_number, was_removed in changed_lines:
            suffix = " (removed)" if was_removed else ""
            print(f"    - {line_number}{suffix}")

if __name__ == "__main__": raise SystemExit(main())