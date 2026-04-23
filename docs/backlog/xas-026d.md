# [XAS-026d] JSON schema validation for `marketplace.json` and `plugin.json`

**Status**: Open
**Priority**: Medium
**Component**: `.github/workflows/`, `schemas/`, helper script

**Summary**:
As a maintainer, I want CI to validate `marketplace.json` and every `plugins/*/.claude-plugin/plugin.json` against a JSON schema so that malformed manifests can't ship to the marketplace.

**Description**:
Plugin and marketplace manifests are hand-edited and easy to break (typo in a version, missing required field, mistyped author block, version drift between `plugin.json` and the matching `marketplace.json` entry). A schema check on every PR catches these before they reach users.

Two schemas needed:

1. `schemas/marketplace.schema.json` — for `.claude-plugin/marketplace.json`
2. `schemas/plugin.schema.json` — for `plugins/*/.claude-plugin/plugin.json`

Validate via a small Python step using `jsonschema` (added to the dev group). Keeps the toolchain consistent with the rest of the repo (uv + Python). Can run as an extra step inside `test.yml` or as a separate `validate.yml` — implementation choice deferred.

**Acceptance Criteria**:
- [ ] `schemas/marketplace.schema.json` present and matches the upstream Claude Code marketplace shape (required fields, plugin entry shape)
- [ ] `schemas/plugin.schema.json` present and matches the upstream plugin manifest shape (`name`, `description`, `version`, `author`, `repository`, `license`)
- [ ] CI step validates `.claude-plugin/marketplace.json` against the marketplace schema
- [ ] CI step validates each `plugins/*/.claude-plugin/plugin.json` against the plugin schema
- [ ] CI step asserts that `marketplace.json` `plugins[].version` matches the corresponding `plugin.json` `version` (catches the dual-bump-skipped class of mistakes)
- [ ] Failure messages name the offending file and the offending field/path
- [ ] A deliberately broken manifest (in a throwaway branch or via a unit test) demonstrates the check fails as expected

**Related**: XAS-004b (auto-sync version between plugin.json and marketplace.json) — 026d *detects* mismatches; 004b *prevents* them. They're complementary; the CI check stays useful as a safety net even after auto-sync ships.

**Technical Notes**:
- `jsonschema` library handles draft 2020-12; pin a major version in the dev group.
- Schema files can later be reused by IDE JSON-schema features (VS Code `json.schemas` setting) for inline editor validation.
