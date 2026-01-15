<!-- Title: keep under 72 chars -->
CI: add workflow and import/export tests

## Summary

This PR adds a GitHub Actions workflow (`.github/workflows/ci.yml`) that installs
development dependencies and runs the full test suite on Python 3.11. It also
introduces a set of targeted tests that improve coverage around the import/export
feature (validation, edge cases, and per-field merge overrides).

## Motivation

- Ensure the repository runs tests automatically on push/PRs to catch regressions.
- Add safety checks around the import/export feature so future changes are
  verified by CI before merging.

## Changes

- Add CI workflow: `.github/workflows/ci.yml` — installs `.[dev]` and runs `pytest`.
- Add tests to broaden coverage for import/export:
  - `tests/test_import_invalid.py` — rejects wrong content types and malformed JSON.
  - `tests/test_import_edgecases.py` — large payload handling and invalid datetime parsing.
  - `tests/test_import_overrides.py` — verifies per-field override merge semantics.

## Security & Deployment Notes

- The import endpoints currently accept JSON uploads and perform `merge` semantics.
  They are intentionally permissive for local-first workflows. Before making the
  service publicly accessible, add authentication, authorization, and rate-limiting
  (e.g., token-based auth or reverse-proxy protections) to avoid accidental or
  malicious data imports.

## How to test locally

1. Create a virtualenv and install dev dependencies:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install '.[dev]'
```

2. Run the tests:

```bash
python -m pytest -q
```

## Review checklist

- [ ] CI passes on this branch
- [ ] Tests added are clear and maintainable
- [ ] Import/export behavior is acceptable for local workflows
- [ ] Plan for hardening import endpoint before public hosting is documented

## Files changed (high level)

- `.github/workflows/ci.yml` — CI workflow
- `tests/test_import_invalid.py`
- `tests/test_import_edgecases.py`
- `tests/test_import_overrides.py`

If you'd like a different PR description or additions to the checklist, tell me
what to include and I will update this file and push the change to the branch.
