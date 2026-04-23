# [XAS-026a] Pytest workflow on push/PR

**Status**: In Progress
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
- [ ] Workflow file at `.github/workflows/test.yml`
- [ ] Matrix runs on `ubuntu-latest` and `windows-latest`
- [ ] Uses `astral-sh/setup-uv@v6` (or current major) for uv installation, with cache enabled
- [ ] Runs `uv run --group dev pytest` and fails the job on any test failure (until XAS-026b moves the pass/fail decision to the JUnit report step)
- [ ] Workflow completes in under 5 minutes for typical changes on each leg
- [ ] Required status check name(s) appear on PRs to `develop`
- [ ] All 46 existing tests pass on both OSes

**Technical Notes**:
- `permissions: contents: read` for now; XAS-026b will need `checks: write` and `pull-requests: write`.
- `timeout-minutes: 15` is generous for a pytest-only run.
- Use `fail-fast: false` on the matrix so a Windows-only failure doesn't mask Ubuntu results (or vice versa).
