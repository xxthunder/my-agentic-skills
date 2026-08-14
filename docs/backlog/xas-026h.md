# [XAS-026h] Grant `checks: write` so the JUnit report can publish

**Status**: In Progress
**Priority**: Medium
**Component**: `.github/workflows/test.yml`

**Related**: [XAS-026b](xas-026b.md) added the JUnit reporting step. This item
fixes a defect in that delivery rather than adding new capability.

**Summary**:
As a maintainer reviewing a pull request, I want the JUnit test report to appear
as a check run, so that pass and skip counts are visible on the PR instead of
having to be dug out of raw job logs.

**Description**:
`mikepenz/action-junit-report` is configured with `check_name`, `require_tests`
and `detailed_summary`, but the job grants only `contents: read`. Creating a
check run requires `checks: write`, so the step cannot publish and the
`Test Results (uv pytest, …)` checks never appear on the pull request.

The failure is silent, which is what makes it worth fixing. Nothing errors —
the workflow goes green, the four expected checks (two `Tests` jobs plus two
Codecov) all report success, and the missing fifth and sixth simply are not
there to be noticed.

It surfaced on [PR #12](https://github.com/xxthunder/xxthunder-agentic-skills/pull/12):
confirming that the new ADR tests had actually run on Windows rather than
skipping required fetching per-job logs through the REST API, because the counts
were nowhere on the PR. `0 skipped` was the number that mattered, and it was the
number hardest to reach.

**Scope Decisions**:
- **Add `checks: write` only.** Least privilege. The action can also comment on
  pull requests, which would need `pull-requests: write`, but commenting is not
  enabled in this workflow and an unused grant is still a grant.
- **Keep `contents: read`.** Checkout needs it; nothing here needs more.
- **Job-level, not workflow-level.** The existing `permissions:` block sits on
  the `test` job. Widening it at workflow level would grant the token to any
  future job in this file that has no reason to hold it.

**Acceptance Criteria**:
- [x] The `test` job's `permissions:` block grants `contents: read` and
      `checks: write`, and nothing else.
- [ ] On a pull request, `Test Results (uv pytest, ubuntu)` and
      `Test Results (uv pytest, windows)` appear as check runs.
- [ ] Those check runs carry the pass / fail / skip counts, so a reviewer can
      read them without opening job logs.
- [ ] A failing test still fails the check — `fail_on_failure: true` keeps
      working once the action can publish.
- [ ] Both `Tests` jobs and both Codecov checks still pass.

**Out of scope**:
- Granting `pull-requests: write` or enabling PR comments from the action.
- Changing the Codecov steps, which are token-authenticated and unaffected.
- Coverage thresholds — that is [XAS-026f](xas-026f.md).
