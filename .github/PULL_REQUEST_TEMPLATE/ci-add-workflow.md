<!-- Title: keep under 72 chars -->
CI: add workflow and import/export tests

## Summary

This PR adds a GitHub Actions workflow (`.github/workflows/ci.yml`) that installs dev
dependencies and runs the test suite on Python 3.11. It also adds additional tests
to improve coverage for the import/export functionality (invalid inputs, large
payloads, and per-field override behavior).

## Changes

- Add CI workflow: `.github/workflows/ci.yml`
- Add tests:
  - `tests/test_import_invalid.py` (malformed / wrong content-type checks)
  - `tests/test_import_edgecases.py` (large payloads, invalid datetimes)
  - `tests/test_import_overrides.py` (per-field override coverage)

## How to test locally

1. Create a virtualenv and install dev dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
pip install --upgrade pip
pip install '.[dev]'
```

2. Run the tests:

```bash
python -m pytest -q
```

## Notes

- The workflow uses the `dev` extras from `pyproject.toml` to install test tools.
- The import endpoints are intentionally permissive in the preview step; hardening
  (auth/rate-limiting) will be added before any public deployment.

If you'd like, I can update this PR body before opening the pull request on GitHub.
