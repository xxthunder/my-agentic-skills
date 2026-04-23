# [XAS-004b] Auto-sync version between plugin.json and marketplace.json

**Status**: Open
**Priority**: Medium
**Component**: scripts/, .claude-plugin/

**Summary**:
As a maintainer, I want the version field in plugin.json and marketplace.json to stay in sync automatically so that releases don't ship with mismatched versions.

**Description**:
Today the version must be bumped in two places manually (per CLAUDE.md). Automate via a bump script that updates both atomically, plus a pre-commit or CI check that fails on mismatch.

**Acceptance Criteria**:
- [ ] A single command bumps both version fields
- [ ] Pre-commit or CI check fails on version mismatch
- [ ] CLAUDE.md instructions updated to reflect the new workflow
