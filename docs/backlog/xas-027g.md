# [XAS-027g] Verify in a consuming repo; retire the per-repo `AGENTS.md` text

**Status**: Open
**Priority**: Medium
**Component**: `xxthunder/shortcuts` — `AGENTS.md` (external repo)

**Depends on**: [XAS-027c](xas-027c.md), [XAS-027f](xas-027f.md)

**Summary**:
As a maintainer, I want the hook observed working in a repo that is not this
one, so that the per-repo `AGENTS.md` paragraph can be deleted knowing what
replaces it actually fires.

**Description**:
The per-repo text is the current safety net. It stays until its replacement
demonstrably works — removing it first would mean discovering the hook does not
outrank a peer plugin's skill instruction by losing the behaviour in a live
repo.

This substory also settles the epic's main open question. The reasoning is that
hook-injected text arrives as session context rather than as a skill, which is
how `superpowers` makes its own rule stick, and that a payload naming
`brainstorming`'s spec-writing step directly beats one stating a general rule.
Both are arguments, not evidence. This is where they get tested.

**Scope Decisions**:
- `xxthunder/shortcuts` is the verification repo — it is where the rule was
  first written, so it is the fairest test of whether the plugin replaces it.
- If the hook does **not** reliably outrank `brainstorming`, the per-repo
  paragraph stays and the observed failure is written up rather than worked
  around silently. A rule that only works sometimes is worse than one that is
  honestly documented as needing local reinforcement.

**Acceptance Criteria**:
- [ ] A fresh session in the consuming repo shows the orientation text present
      without anything being invoked.
- [ ] A brainstorming session in that repo produces a backlog item and, where
      the decision earns one, an ADR — not a `docs/superpowers/specs/` file.
- [ ] The observation is recorded against the epic's open question, stating what
      was actually seen rather than what was expected.
- [ ] The `AGENTS.md` paragraph in `xxthunder/shortcuts` is removed and the repo
      left relying on the plugin — **only if** the two checks above passed.
- [ ] If they did not pass: the failure mode is written up, the fallback is
      documented, and the paragraph stays.
