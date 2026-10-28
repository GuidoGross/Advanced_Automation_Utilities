param(
    [ValidateSet("development", "pre_commit", "post_commit")]
    [string]$HypothesisProfile = "development"
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
$test_files = @(
    Get-ChildItem -Path (Join-Path $project_root "tests") -Filter "test_*.py" | ForEach-Object {"tests/$($_.Name)"}
)

function main {
    $total_start_time = Get-Date
    Write-Host "${bold}${italic}Starting coverage analysis...${reset_style}" -ForegroundColor White
    separator
    run_coverage_analysis
    finish $total_start_time
}

function separator {
    $width = $Host.UI.RawUI.WindowSize.Width
    if ($null -eq $width) {$width = 125}
    $separator = "${bold}/" + ("-" * ($width - 3)) + "/${reset_style}"
    Write-Host $separator -ForegroundColor White
}

function run_coverage_analysis {
    Write-Host "${bold}${italic}[1/1]${/italic} Running all tests with coverage analysis and the $HypothesisProfile profile...${reset_style}" -ForegroundColor White
    $current_step_start_time = Get-Date
    $env:HYPOTHESIS_PROFILE = $HypothesisProfile
    python -m pytest --cov=advanced_automation_utilities --cov-branch --cov-report=term-missing @test_files
    $exit_code = $LASTEXITCODE
    $duration = (Get-Date) - $current_step_start_time
    if ($exit_code -ne 0) {
        Write-Host "${bold}Coverage analysis failed with exit code:${/bold} $exit_code${reset_style}" -ForegroundColor Red
        exit $exit_code
    }
    Write-Host "${bold}Coverage analysis completed in:${/bold} $($duration.TotalMilliseconds.ToString("N0", [cultureinfo]::GetCultureInfo("es-ES")))ms${reset_style}" -ForegroundColor Green
    separator
}

function finish($total_start_time) {
    $total_duration = (Get-Date) - $total_start_time
    Write-Host "${bold}Coverage analysis completed successfully in:${/bold} $($total_duration.TotalMilliseconds.ToString("N0", [cultureinfo]::GetCultureInfo("es-ES")))ms${reset_style}" -ForegroundColor Green
}

main