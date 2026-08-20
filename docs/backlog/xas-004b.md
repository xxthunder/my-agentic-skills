# [XAS-004b] Auto-sync version between plugin.json and marketplace.json

**Status**: Open
**Priority**: Medium
**Component**: scripts/, .claude-plugin/

**Summary**:
As a maintainer, I want the version field in plugin.json and marketplace.json to stay in sync automatically so that releases don't ship with mismatched versions.

**Description**:
Today the version must be bumped in two places manually (per CLAUDE.md). Automate via a bump script that updates both atomically, plus a pre-commit or CI check that fails on mismatch.

**Superseded by [XAS-029](xas-029.md)** (2026-08-20). Release Please derives the
version from commit messages and writes `plugin.json` itself, so the bump script
this item describes has nothing left to do. The mismatch check it wanted is
moot for a different reason: XAS-029 removes `version` from `marketplace.json`
entirely, since the marketplace schema pins a plugin from *either* location and
one of the two fields was therefore always redundant.

Left Open rather than closed: it is the *decision* that is superseded, and
whoever closes XAS-029 should close this alongside it.

**Acceptance Criteria**:
- [ ] A single command bumps both version fields
- [ ] Pre-commit or CI check fails on version mismatch
- [ ] CLAUDE.md instructions updated to reflect the new workflow
