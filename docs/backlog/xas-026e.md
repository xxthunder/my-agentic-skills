# [XAS-026e] PR title conventional-commit linter

**Status**: Open
**Priority**: Low
**Component**: `.github/workflows/pr-lint.yml`

**Summary**:
As a maintainer, I want PR titles to be validated against the conventional-commits spec so that squash-merge commits land in `develop` already correctly formatted.

**Description**:
The `commit-helper` skill enforces conventional commit format on individual local commits, but PR titles — which become the squash-merge commit message on GitHub — are not currently checked. Without this, a contributor (or a careless rebase) can produce a non-conforming `develop` history even when every local commit was clean.

Add `amannn/action-semantic-pull-request@v5` (or equivalent) to validate the title on `pull_request` events.

**Triggers**:
- `pull_request` types: `[opened, edited, synchronize]`

**Acceptance Criteria**:
- [ ] Workflow file at `.github/workflows/pr-lint.yml`
- [ ] PR title must match conventional-commits format: `type(scope): subject`
- [ ] Allowed types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `build`, `ci`, `style`, `revert` (matches CLAUDE.md's repo-wide convention)
- [ ] Scope is optional but, when present, should match a skill name when the change is skill-specific (per CLAUDE.md)
- [ ] PR check fails with an actionable message when the title is malformed
- [ ] Check tolerates bot-authored PRs (e.g., dependabot) by exempting their conventions

**Related**: `commit-helper` skill — local enforcement of the same format on individual commits. Together they cover both granular and squash-merge paths.
