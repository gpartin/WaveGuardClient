param(
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$root = Get-Location
$today = Get-Date -Format "yyyy-MM-dd"
$tag = "v$Version"
$notesDir = Join-Path $root "artifacts"
$notesFile = Join-Path $notesDir "pypi_release_${Version}_$today.md"

New-Item -ItemType Directory -Force -Path $notesDir | Out-Null

if (-not (Test-Path "pyproject.toml")) {
    throw "pyproject.toml not found. Run from WaveGuardClient repository."
}

$pyprojectRaw = Get-Content "pyproject.toml" -Raw
$versionLine = Get-Content "pyproject.toml" | Where-Object { $_ -match '^version\s*=' } | Select-Object -First 1
if (-not $versionLine -or -not ($versionLine -match [regex]::Escape($Version))) {
    throw "pyproject.toml version does not match $Version. Update project version first."
}

if (-not (Test-Path "CHANGELOG.md")) {
    throw "CHANGELOG.md not found."
}

$changelogRaw = Get-Content "CHANGELOG.md" -Raw
if ($changelogRaw -notmatch [regex]::Escape("[$Version]")) {
    throw "CHANGELOG.md does not contain section [$Version]."
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
$wheelPath = Get-ChildItem -Path "dist" -Filter "*.whl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $wheelPath) {
    throw "No wheel found in dist/. Build failed to produce a wheel artifact."
}
python -m pip install --force-reinstall --no-deps "$($wheelPath.FullName)"
python -c "import waveguard,sys; print('import_ok', getattr(waveguard, '__name__', 'unknown')); print('python', sys.version.split()[0])"

@"
# WaveGuardClient PyPI Release Prep

## Prepared
- Date: $today
- Version: $Version
- Tag: $tag
- Repo: WaveGuardClient

## Local validation completed
- python -m build
- python -m twine check dist/*
- local wheel install/import smoke

## Manual finalization (GitHub trusted publisher)
1. Commit and push version/changelog updates to main.
2. Create GitHub release/tag $tag.
3. Wait for publish workflow to complete.
4. Confirm https://pypi.org/project/WaveGuardClient/ shows $Version.

"@ | Set-Content -Encoding UTF8 $notesFile

Write-Host "Release prep complete."
Write-Host "Notes file: $notesFile"
Write-Host "Next: create GitHub release/tag $tag"
