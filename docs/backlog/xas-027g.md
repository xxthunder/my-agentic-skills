# [XAS-027g] Verify in a consuming repo; retire the per-repo `AGENTS.md` text

**Status**: In Progress
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
- **The paragraph must be out of play *during* the test, not after it.** As
  originally written, this story removed the `AGENTS.md` text only once the two
  checks had passed — which would have made those checks meaningless. The
  paragraph is always-on context, exactly like the hook, so a brainstorming
  session that correctly lands its design in the backlog item while the
  paragraph is still present proves nothing about the hook: the two causes are
  confounded, and the paragraph is if anything the stronger signal.
  The sequence is therefore: remove the paragraph on a branch, observe, then
  either keep it removed or restore it. What the original wording was protecting
  against is real but different — *permanently retiring* the safety net before
  its replacement is proven. Removing it for the duration of the experiment does
  not do that.
- **The observation cannot be made from the session that built this.** A
  `SessionStart` hook fires on `startup|clear|compact`, so verifying it requires
  a fresh session started inside the consuming repo by a human. This story
  cannot be closed by the agent alone.
- **The hook replaces only part of the paragraph, and this was not anticipated.**
  The text in `xxthunder/shortcuts` does two jobs. The first is *where design
  lives*: capture it in the item, do not create a separate spec document. The
  hook replaces that. The second is a *gate*: a backlog item MUST exist before
  any design or implementation begins. The hook will never replace that, because
  [ADR-0004](../adr/0004-always-on-rule-is-orientation-not-enforcement.md)
  commits it to orientation rather than enforcement.
  Only the first half was removed for this experiment; the gate stays.
  This qualifies the epic's acceptance criterion "No repo needs an `AGENTS.md`
  paragraph to get the behaviour" — true for the design-location behaviour,
  false for the gate. A repo that wants the gate still needs to say so locally,
  and that is a consequence of ADR-0004 rather than a defect.
- `xxthunder/shortcuts` is the verification repo — it is where the rule was
  first written, so it is the fairest test of whether the plugin replaces it.
- If the hook does **not** reliably outrank `brainstorming`, the per-repo
  paragraph stays and the observed failure is written up rather than worked
  around silently. A rule that only works sometimes is worse than one that is
  honestly documented as needing local reinforcement.

**Acceptance Criteria**:
- [ ] The `AGENTS.md` paragraph is removed on a branch **before** the
      observation, so the hook is the only always-on instruction in play.
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
