# WaveGuardClient PyPI Release Prep

## Prepared
- Date: 2026-03-01
- Version: 3.3.0
- Tag: v3.3.0
- Repo: WaveGuardClient

## Local validation completed
- python -m build
- python -m twine check dist/*
- local wheel install/import smoke

## Manual finalization (GitHub trusted publisher)
1. Commit and push version/changelog updates to main.
2. Create GitHub release/tag v3.3.0.
3. Wait for publish workflow to complete.
4. Confirm https://pypi.org/project/WaveGuardClient/ shows 3.3.0.

