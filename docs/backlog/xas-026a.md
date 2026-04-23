# [XAS-026a] ✅ DONE - Pytest workflow on push/PR

**Status**: Done (2026-04-23)
**Priority**: High
**Component**: `.github/workflows/test.yml`

**Summary**:
As a maintainer, I want pytest to run automatically on every push to `develop` and every PR targeting `develop` so that regressions are caught before merge.

**Description**:
Add a GitHub Actions workflow that runs the existing pytest suite (46 tests under `tests/`) via `uv run --group dev pytest` on a matrix of `ubuntu-latest` and `windows-latest`.

- **Ubuntu** is the cheap/fast default and exercises the pure-Python plugin scripts.
- **Windows** verifies compatibility with the user's primary daily-driver platform — NAPS2-based plugins target Windows, so any latent path/encoding/line-ending issue surfaces here.

**Triggers**:
- `push` to `develop`
- `pull_request` targeting `develop`
- `workflow_dispatch` (manual)

**Acceptance Criteria**:
- [x] Workflow file at `.github/workflows/test.yml`
- [x] Matrix runs on `ubuntu-latest` and `windows-latest`
- [x] Uses `astral-sh/setup-uv@v6` (or current major) for uv installation, with cache enabled
- [x] Runs `uv run --group dev pytest` and fails the job on any test failure (until XAS-026b moves the pass/fail decision to the JUnit report step)
- [x] Workflow completes in under 5 minutes for typical changes on each leg
- [x] Required status check name(s) appear on PRs to `develop`
- [x] All 46 existing tests pass on both OSes

**Technical Notes**:
- `permissions: contents: read` for now; XAS-026b will need `checks: write` and `pull-requests: write`.
- `timeout-minutes: 15` is generous for a pytest-only run.
- Use `fail-fast: false` on the matrix so a Windows-only failure doesn't mask Ubuntu results (or vice versa).

## Implementation Plan

### Files
- **Create**: `.github/workflows/test.yml` — only file in scope. `pyproject.toml` stays as-is; `pytest-cov` and JUnit XML config are XAS-026b's job.

### Workflow shape

```yaml
name: CI

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop]
  workflow_dispatch:

jobs:
  test:
    name: Tests (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Run pytest
        run: uv run --group dev pytest -q
```

### Steps

1. Write `.github/workflows/test.yml` per above.
2. Lint YAML locally with `actionlint` (if installed) — otherwise rely on GitHub's parse-on-push.
3. Push branch — observe both matrix legs run.
4. Triage any Windows-only failure (most likely culprit: path/encoding differences in PDF-fixture handling). Fix in plugin scripts or test fixtures; **do not** add Windows-skips that mask real bugs.
5. Confirm all 46 tests pass on both legs.
6. Post-merge, manually require both checks (`Tests (ubuntu-latest)`, `Tests (windows-latest)`) in branch protection — outside the scope of this code change.

### Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Python version | Pin 3.12, single (no Python matrix) | Avoid 4-leg matrix on day one; `requires-python = ">=3.11"` already declared in pyproject. |
| uv setup action | `astral-sh/setup-uv@v6` with `enable-cache: true` | Current major; built-in cache keyed on `uv.lock` removes need for manual `actions/cache`. |
| Matrix `fail-fast` | `false` | A Windows-only failure shouldn't cancel Ubuntu (or vice versa) — full signal preferred. |
| Status check names | `Tests (ubuntu-latest)`, `Tests (windows-latest)` | Predictable; ready to register in branch protection. |
| Test step behavior | Hard-fail on test failure | XAS-026b will flip this to `continue-on-error: true` once the JUnit reporter takes over the pass/fail decision; not earlier. |

### Risks

- **Windows-only failures.** Real risk: PDF-fixture creation (reportlab) and pdfminer text extraction can vary subtly between OSes. Mitigation: use `pathlib`, `tmp_path`, and explicit text encodings. If a fixture is CRLF-sensitive, normalize in the test, not the production script.
- **uv cache miss on first run.** Expected — first run on each OS is slower; subsequent runs benefit from the cache.
- **No reporting yet.** Failures show as a red X with pytest output in logs. That's the agreed shape for 026a; richer reporting lands with 026b.

### Out of scope

Coverage & JUnit (→ XAS-026b), schema validation (→ XAS-026d), PR-title lint (→ XAS-026e), Claude bot (→ XAS-026c).
