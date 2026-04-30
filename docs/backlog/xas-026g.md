# [XAS-026g] ✅ DONE - Codecov status badge in README

**Status**: Done (2026-04-28)
**Priority**: Low
**Component**: `README.md`

**Summary**:
As a visitor, I want a Codecov status badge in the README so that current coverage is visible at a glance alongside the existing CI/license/Python badges.

**Description**:
Follow-up to XAS-026b — the Codecov upload landed, but the status badge was missed. Add it to the existing badge cluster at the top of the README, linking to the Codecov dashboard.

**Acceptance Criteria**:
- [x] README badge cluster includes a Codecov coverage badge for the `develop` branch, linking to the Codecov dashboard for the repo

**Technical Notes**:
- Badge URL: `https://codecov.io/gh/xxthunder/xxthunder-agentic-skills/branch/develop/graph/badge.svg`
- Link target: `https://codecov.io/gh/xxthunder/xxthunder-agentic-skills`
- Public repo, so the badge SVG works without a token query parameter.

**Follow-up (2026-04-30)**:
Badge cluster reordered to match the `xxthunder/shortcuts` repo convention: CI → license → language → Codecov. Platform badge was considered but dropped — OS is irrelevant here and a Claude Code badge would become incomplete as additional agent targets (e.g. GitHub Copilot) are added. Final order landed in this commit.
