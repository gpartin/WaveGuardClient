# WaveGuardClient PyPI Release Checklist (Target: v3.3.0)

## One-command prep

From `C:\Papers\WaveGuardClient`:

```powershell
./scripts/prepare_pypi_release.ps1 -Version 3.3.0
```

This command validates version/changelog alignment, builds artifacts, runs twine checks, performs local install/import smoke, and writes a release notes file under `artifacts/`.

## Required preconditions

1. `pyproject.toml` has `version = "3.3.0"`.
2. `CHANGELOG.md` contains a `[3.3.0]` section.
3. Python build tooling is available in your active environment.

## Manual finalization (can’t be fully automated here)

1. Commit and push updated files to `main` in `gpartin/WaveGuardClient`.
2. Create GitHub release with tag `v3.3.0`.
3. Let trusted publisher workflow publish to PyPI.
4. Verify `https://pypi.org/project/WaveGuardClient/` shows `3.3.0`.

## Suggested v3.3.0 changelog bullets

### Added
- Compatibility alignment with WaveGuard server `v3.3.0` endpoint surface.
- Release-process tooling for deterministic PyPI prep (`prepare_pypi_release.ps1`).

### Operational
- Packaging sanity checks (`build`, `twine check`, wheel install/import smoke) now standardized.
