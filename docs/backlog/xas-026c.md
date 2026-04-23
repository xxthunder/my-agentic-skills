# [XAS-026c] Claude Code interactive bot (`@claude` mentions)

**Status**: Open
**Priority**: Medium
**Component**: `.github/workflows/claude.yml`

**Summary**:
As a maintainer, I want to invoke Claude on issues and PRs by mentioning `@claude` in a comment so that I can delegate triage, review, and small edits to the bot directly from GitHub.

**Description**:
Mirror the shortcuts repo's `claude.yml`, with one substantive change: load the **xxthunder-agentic-skills** marketplace and install the `xxthunder-dev-skills` plugin. This makes the bot the first external consumer of our own marketplace — a real-world dogfood test that the install path works.

Behavior:
- Triggers on `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review`
- Filters by author association (`COLLABORATOR`, `MEMBER`, `OWNER`)
- Filters by `@claude` mention in the relevant body/title field
- Parses model alias from the trigger comment:
  - `@claude opus …` → `claude-opus-4-7`
  - `@claude sonnet …` → `claude-sonnet-4-6`
  - default (just `@claude …`) → `claude-sonnet-4-6`
- Uses `anthropics/claude-code-action@v1`

**Acceptance Criteria**:
- [ ] Workflow file at `.github/workflows/claude.yml`
- [ ] `@claude` in an issue comment / PR review / PR review comment / issue body or title triggers the bot
- [ ] Comments from non-collaborators are silently ignored (no run scheduled)
- [ ] `@claude opus <task>` resolves to `claude-opus-4-7`
- [ ] `@claude sonnet <task>` (or just `@claude <task>`) resolves to `claude-sonnet-4-6`
- [ ] Bot has `additional_permissions: actions: read` so it can read CI results on PRs
- [ ] Bot loads marketplace `https://github.com/xxthunder/xxthunder-agentic-skills.git` and installs the `xxthunder-dev-skills` plugin
- [ ] `CLAUDE_CODE_OAUTH_TOKEN` repository secret is documented (README or CONTRIBUTING)
- [ ] End-to-end smoke test: `@claude what files changed?` on a test PR returns a sensible reply that references the actual diff

**Technical Notes**:
- Default model `claude-sonnet-4-6` matches the shortcuts repo for consistency.
- Permissions block: `contents: write`, `pull-requests: write`, `issues: write`, `id-token: write`, `actions: read`.
