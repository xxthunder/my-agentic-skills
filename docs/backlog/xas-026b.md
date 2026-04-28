# [XAS-026b] Coverage upload + JUnit test report

**Status**: In Progress
**Priority**: Medium
**Component**: `.github/workflows/test.yml`, `pyproject.toml`

**Summary**:
As a reviewer, I want PRs to surface code coverage and a structured test report so that I can assess test impact without re-running tests locally.

**Description**:
Extend the workflow from XAS-026a to publish coverage and JUnit XML on every run, mirroring the shortcuts-repo pattern:

- Add `pytest-cov` to the dev dependency group in `pyproject.toml`
- Configure pytest to emit `coverage.xml` (Cobertura) and `junit.xml`
- Upload coverage to Codecov via `codecov/codecov-action@v5`
- Upload test results to Codecov (`report_type: test_results`)
- Publish a JUnit-rendered PR check via `mikepenz/action-junit-report@v6`
- Move pass/fail decision from the test step to the JUnit report step (`continue-on-error: true` on the test step)

**Depends on**: XAS-026a

**Acceptance Criteria**:
- [ ] `pytest-cov` added to `[dependency-groups].dev` in `pyproject.toml`
- [ ] `[tool.coverage.run] source = ["plugins"]` added to `pyproject.toml` so local and CI runs measure the same code (helper scripts under `plugins/*/skills/*/scripts/`)
- [ ] pytest invocation produces `coverage.xml` and `junit.xml` (paths captured as workflow outputs or fixed locations)
- [ ] `codecov/codecov-action@v5` uploads coverage with `fail_ci_if_error: true`
- [ ] `codecov/codecov-action@v5` uploads test results (`report_type: test_results`) with `fail_ci_if_error: true`
- [ ] Codecov flags include the OS leg (`ubuntu`, `windows`) so matrix legs don't clobber each other
- [ ] `mikepenz/action-junit-report@v6` publishes a check (e.g., `Test Results (uv pytest, ubuntu)`) per matrix leg with `fail_on_failure: true`, `fail_on_parse_error: true`, `require_tests: true`, `detailed_summary: true`, `include_passed: false`
- [ ] All reporting steps run under `if: always()` so reports publish even on test failure
- [ ] `CODECOV_TOKEN` repository secret is documented (README or CONTRIBUTING)
- [ ] PR shows a Codecov comment summarizing coverage delta

**Technical Notes**:
- Match shortcuts' pattern: test step is `continue-on-error: true`; the JUnit report step decides PR pass/fail. This produces a single source of truth on the GitHub PR check page.
- Implementation order: `CODECOV_TOKEN` is added to repo secrets BEFORE the workflow PR is opened. With `fail_ci_if_error: true`, a missing token would break every push/PR.
- Coverage thresholds and `codecov.yml` policy are intentionally out of scope here — see XAS-026f. Ship reporting first, let numbers stabilize over a few PRs, then enforce.
