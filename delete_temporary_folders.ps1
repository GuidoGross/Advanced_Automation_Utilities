$ErrorActionPreference = "Stop"

chcp 65001 > $null
$utf8_encoding = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = [Console]::OutputEncoding = $OutputEncoding = $utf8_encoding

$project_root = $PSScriptRoot
Set-Location $project_root

$escape = [char]27
$bold = "$escape[1m"
${/bold} = "$escape[22m"
$italic = "$escape[3m"
${/italic} = "$escape[23m"
$reset_style = "$escape[0m"

function separator {
    $width = $Host.UI.RawUI.WindowSize.Width
    if ($null -eq $width) {$width = 125}
    $separator = "${bold}/" + ("-" * ($width - 3)) + "/${reset_style}"
    Write-Host $separator -ForegroundColor White
}

function main {
    $total_start_time = Get-Date
    Write-Host "${bold}${italic}Starting temporary folder cleanup...${reset_style}" -ForegroundColor White
    separator
    clean_pycache_folders
    finish $total_start_time
}

function clean_pycache_folders {
    Write-Host "${bold}${italic}[1/1]${/italic} Removing temporary folders...${reset_style}" -ForegroundColor White
    $current_step_start_time = Get-Date
    $folders_to_delete = @()
    Get-ChildItem -Path $project_root -Filter "__pycache__" -Directory -Recurse | ForEach-Object {$folders_to_delete += $_.FullName}
    Get-ChildItem -Path $project_root -Filter ".pytest_cache" -Directory -Recurse | ForEach-Object {$folders_to_delete += $_.FullName}
    Get-ChildItem -Path $project_root -Filter "*.egg-info" -Directory -Recurse | ForEach-Object {$folders_to_delete += $_.FullName}
    $folders_to_delete | ForEach-Object {if (Test-Path $_) {Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue}}
    $duration = (Get-Date) - $current_step_start_time
    Write-Host "${bold}Temporary folders removed in:${/bold} $($duration.TotalMilliseconds.ToString("N0", [cultureinfo]::GetCultureInfo("es-ES")))ms${reset_style}" -ForegroundColor Green
    separator
}

function finish($total_start_time) {
    $total_duration = (Get-Date) - $total_start_time
    Write-Host "${bold}Folder cleanup completed in:${/bold} $($total_duration.TotalMilliseconds.ToString("N0", [cultureinfo]::GetCultureInfo("es-ES")))ms${reset_style}" -ForegroundColor Green
}

main