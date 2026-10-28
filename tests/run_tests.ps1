param(
    [ValidateSet("development", "pre_commit", "post_commit")]
    [string]$HypothesisProfile = "development",
    [string[]]$ChangedFiles = @()
)

$ErrorActionPreference = "Stop"

chcp 65001 > $null
$utf8_encoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = $utf8_encoding

$project_root = Split-Path -Parent $PSScriptRoot
Set-Location $project_root

$escape = [char]27
$bold = "$escape[1m"
${/bold} = "$escape[22m"
$italic = "$escape[3m"
${/italic} = "$escape[23m"
$reset_style = "$escape[0m"
$all_test_files = @(
    Get-ChildItem -Path (Join-Path $project_root "tests") -Filter "test_*.py" | ForEach-Object {"tests/$($_.Name)"}
)
$test_files_by_module = @{
    asynchrony = @("tests/test_asynchrony.py")
    keyboard = @("tests/test_keyboard.py")
    mouse = @("tests/test_mouse.py")
    screen = @("tests/test_screen.py")
    sound = @("tests/test_sound.py")
    system = @("tests/test_system.py")
    timing = @("tests/test_timing.py")
    utilities = @("tests/test_utilities.py")
    windows_backend = @("tests/test_windows_backend.py")
}
$queueable_test_modules = @("asynchrony", "keyboard", "mouse", "sound", "system")
$common_module_test_modules = @(
    "asynchrony", "keyboard", "mouse", "screen", "sound", "system", "timing", "utilities"
)
$test_files_to_run = [System.Collections.Generic.HashSet[string]]::new()
$run_all_tests = $ChangedFiles.Count -eq 0

function main {
    $total_start_time = Get-Date
    Write-Host "${bold}${italic}Starting unit tests...${reset_style}" -ForegroundColor White
    separator
    select_tests
    run_unit_tests
    finish $total_start_time
}

function separator {
    $width = $Host.UI.RawUI.WindowSize.Width
    if ($null -eq $width) {$width = 125}
    $separator = "${bold}/" + ("-" * ($width - 3)) + "/${reset_style}"
    Write-Host $separator -ForegroundColor White
}

function add_module_tests($module_names) {
    foreach ($module_name in $module_names) {
        foreach ($test_file in $test_files_by_module[$module_name]) {
            $test_files_to_run.Add($test_file) > $null
        }
    }
}

function select_tests {
    foreach ($changed_file in $ChangedFiles) {
        $normalized_path = $changed_file.Replace("\", "/").TrimStart("./")
        if ($normalized_path -match "^tests/(test_[^/]+\.py)$") {
            $test_path = "tests/$($Matches[1])"
            if (Test-Path (Join-Path $project_root $test_path)) {
                $test_files_to_run.Add($test_path) > $null
            } else {
                $script:run_all_tests = $true
                return
            }
            continue
        }
        if ($normalized_path -eq "tests/conftest.py" -or
            $normalized_path -eq "tests/run_tests.ps1") {
            $script:run_all_tests = $true
            return
        }
        if ($normalized_path -match "^advanced_automation_utilities/(keyboard|mouse|screen|sound|system|timing)/") {
            add_module_tests @($Matches[1])
            continue
        }
        if ($normalized_path -match "^advanced_automation_utilities/backend/windows/_(keyboard|mouse|screen|sound|system)\.py$") {
            $backend_module = $Matches[1]
            add_module_tests @($backend_module, "windows_backend")
            if ($backend_module -eq "keyboard") {add_module_tests @("system")}
            continue
        }
        if ($normalized_path -match "^advanced_automation_utilities/(?:_queueable_controller|_asynchronous_context|_task)\.py$") {
            add_module_tests $queueable_test_modules
            continue
        }
        if ($normalized_path -eq "advanced_automation_utilities/_kill_switch_event.py") {
            add_module_tests @("asynchrony", "keyboard", "mouse", "sound", "system", "timing", "windows_backend")
            continue
        }
        if ($normalized_path -in @("advanced_automation_utilities/_utilities.py", "advanced_automation_utilities/_typing.py", "advanced_automation_utilities/exceptions.py", "advanced_automation_utilities/__init__.py")) {
            add_module_tests $common_module_test_modules
            continue
        }
        $script:run_all_tests = $true
        return
    }
}

function run_unit_tests {
    if ($run_all_tests) {
        $selected_test_files = $all_test_files
        Write-Host "${bold}${italic}Running all unit tests with the $HypothesisProfile profile...${reset_style}" -ForegroundColor White
    } else {
        $selected_test_files = @($test_files_to_run | Sort-Object)
        if ($selected_test_files.Count -eq 0) {
            Write-Host "No related unit tests were selected."
            return
        }
        Write-Host "${bold}${italic}Running selected unit tests with the $HypothesisProfile profile...${reset_style}" -ForegroundColor White
        $selected_test_files | ForEach-Object { Write-Host "  $_" }
    }
    $current_step_start_time = Get-Date
    $env:HYPOTHESIS_PROFILE = $HypothesisProfile
    python -m pytest @selected_test_files
    $exit_code = $LASTEXITCODE
    $duration = (Get-Date) - $current_step_start_time
    if ($exit_code -ne 0) {
        Write-Host "${bold}Unit tests failed with exit code:${/bold} $exit_code${reset_style}" -ForegroundColor Red
        exit $exit_code
    }
    Write-Host "${bold}Unit tests completed in:${/bold} $($duration.TotalMilliseconds.ToString("N0", [cultureinfo]::GetCultureInfo("es-ES")))ms${reset_style}" -ForegroundColor Green
    separator
}

function finish($total_start_time) {
    $total_duration = (Get-Date) - $total_start_time
    Write-Host "${bold}Unit tests completed successfully in:${/bold} $($total_duration.TotalMilliseconds.ToString("N0", [cultureinfo]::GetCultureInfo("es-ES")))ms${reset_style}" -ForegroundColor Green
}

main