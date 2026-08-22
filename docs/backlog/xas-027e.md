# [XAS-027e] ✅ DONE - Wire-up: `refinement`, `tdd-workflow`, `commit-helper`

**Status**: Done (2026-08-15)
**Priority**: Medium
**Component**: `plugins/xxthunder-dev-skills/skills/refinement/SKILL.md`,
`plugins/xxthunder-dev-skills/skills/tdd-workflow/SKILL.md`,
`plugins/xxthunder-dev-skills/skills/commit-helper/SKILL.md`,
`plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`

**Depends on**: [XAS-027a](xas-027a.md), [XAS-027b](xas-027b.md)

**Summary**:
As a maintainer, I want the existing skills to point at `design-record` at the
moments that actually produce record changes, so that decisions and structural
moves get captured when they happen rather than when someone remembers.

**Description**:
Three of the four capture moments are covered by skills that already exist and
already sit at the right boundary — they simply do not know about the record
yet:

- **A decision is made.** `refinement`'s Architecture topic currently ends with
  "document decisions in the backlog item's Scope Decisions field". That is
  right for decisions local to one change and wrong for decisions that outlive
  it, so it should apply the three-part test and hand off to `design-record`
  when the decision passes.
- **Structure changes.** A TDD cycle that moves a module boundary, or a
  pre-commit check on a diff that adds or removes one, is the moment
  `architecture.md` becomes stale.
- **On demand** is `design-record` invoked directly and needs no wiring.

All three **suggest and never block**. Gating was ranked last among the goals
for this epic; friction on small changes is a worse failure than a slightly
stale document, because a workflow people route around protects nothing.

**Scope Decisions**:
- Suggestions only. No skill refuses to proceed because the record is stale.
- `refinement` keeps `Scope Decisions` for change-local rationale — the
  escalation ladder is: trivial → nothing; local to this change → `Scope
  Decisions`; outlives the change → ADR.
- Detection of "structure changed" stays deliberately crude — added, deleted or
  moved directories and manifest entries. Chasing a precise definition of a
  boundary change is not worth it for a suggestion that a human confirms.

**Superseded in part by [XAS-030](xas-030.md)** (2026-08-22). The
`tdd-workflow` half of this wire-up is gone with the skill. Its acceptance
criterion was met when written; `commit-helper` now carries the design-record
suggestion alone, and covers it better — it fires on every commit rather than
only at the end of a cycle someone chose to run. `refinement`'s hand-off is
unaffected.

**Acceptance Criteria**:
- [x] `refinement`'s Architecture topic applies the three-part test and hands
      off to `design-record` for decisions that pass it, keeping `Scope
      Decisions` for those that do not.
- [x] `tdd-workflow` suggests `design-record` at cycle end when the cycle moved
      a module boundary, and does not block the cycle.
- [x] `commit-helper` suggests `design-record` during pre-commit checks when the
      staged diff adds, removes or moves a module, and does not block the
      commit.
- [x] None of the three skills introduces a refusal or gate.
- [x] `plugin.json` and `marketplace.json` bumped (minor — behaviour change in
      three skills).
- [x] All existing tests continue to pass.
