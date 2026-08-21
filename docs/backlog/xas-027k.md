# [XAS-027k] ADRs record decisions, not specifications

**Status**: Open
**Priority**: Medium
**Component**: `plugins/xxthunder-dev-skills/skills/design-record/references/adr-format.md`,
`docs/adr/` (sweep), `plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`

**Related**: Found while reviewing all six ADRs during
[XAS-027j](xas-027j.md). Three of them were factually wrong, and all three by
the same mechanism.

**Summary**:
As a maintainer, I want ADRs to name what they decided and point at whatever
owns the details, so that a specification changing does not silently leave an
immutable document lying about how the system behaves.

**Description**:
Three ADRs were found stating things that were no longer true:

- **ADR-0004** listed the hook's guard paths as `docs/backlog/`, `docs/adr/` and
  `docs/architecture.md`. [XAS-027i](xas-027i.md) added two nested locations; the
  hook guards on five paths and the ADR named three.
- **ADR-0006** gave the discovery order as two locations and never mentioned
  ADR-log discovery at all. Both changed under it in the same story.
- **ADR-0001** restated the immutability rule as status-line-only, which
  XAS-027j's change to `adr-format.md` contradicted the same day.

None of these is drift in the usual sense. Nothing violated a decision. In each
case an ADR **reproduced a specification owned somewhere else**, and the copy
went stale while the original moved.

The distinction the format is missing is between a *decision* and a
*specification*. "Discovered, not hardcoded" is a decision: it survived
XAS-027i untouched, which is exactly why extending the search order counted as
an extension rather than a reversal. The search order itself is a
specification: it changed within days of being written, and will change again.
Freezing a specification inside a document that is never edited guarantees it
goes stale.

This is deliberately **not** an `architecture-scan` story.
[XAS-027d](xas-027d.md) already scoped ADR checking to what is mechanically
verifiable — referenced paths that no longer exist — and said the skill "does
not claim to judge whether a decision is still honoured in general, because it
cannot". That reasoning still holds. None of the three failures would have been
caught by a path check anyway: ADR-0004 named `docs/architecture.md`, which
exists. The defect was an *absent* entry, and no scanner sees an item that was
never added. Prevention by format beats detection that cannot work.

**Scope Decisions**:
- **A format rule, not tooling.** The only mechanical heuristic available is
  "this ADR contains a list of paths, so it might be a specification" — noisy,
  and it would have flagged ADR-0006 while missing ADR-0004 entirely.
- **Name, do not reproduce.** An ADR may say *what* it decided about a list
  ("locations are discovered, first match wins") and must not copy the list.
  Naming the owning artifact in prose is enough; a link is optional, and in a
  consuming repo a link into the plugin directory would dangle.
- **The sweep covers the existing six.** ADR-0006 was corrected during
  XAS-027j — it was rewritten to carry the full current order and then rewritten
  again to delegate, which is itself evidence of how easily this happens.
  ADR-0002 remains to be judged: it enumerates four of the seven canonical slots
  that `architecture-format.md` owns, which may be a specification leaking in or
  may be legitimate illustration of the structure-versus-behaviour split.
- **No supersedes.** Every correction here is meaning-preserving under
  `adr-format.md`'s existing test — a reader does not decide anything
  differently once an ADR points at a list instead of copying it.
- **A related rule is currently mis-placed, and this item should decide where
  it belongs.** [XAS-027](xas-027.md)'s `Scope Decisions` now say that a plan
  reproducing the design is a spec under another name, and that a plan is
  deleted once its stories close. That is a general statement about how plans
  relate to backlog items, not something particular to XAS-027 — but it lives
  in one epic in one repository, binds nothing else, and stops being visible
  when that epic closes. It is the same failure this item exists to prevent,
  one level out: a rule recorded where it cannot reach the thing it governs.
  Candidates are `refinement`'s `backlog-format.md`, which already defines the
  item format and ships to consumers, or an ADR if the plans-versus-items
  boundary is judged to be a decision rather than a format rule. Deciding is in
  scope here; the epic keeps the wording until then.

**Acceptance Criteria**:
- [ ] `adr-format.md` gains a rule distinguishing a decision from a
      specification, stating that anything which can change without the decision
      changing is named rather than reproduced.
- [ ] The rule gives at least one concrete example of each, drawn from the real
      failures above rather than invented.
- [ ] All six existing ADRs are swept against the rule; each is either compliant
      or corrected, and any judged compliant-on-purpose says why.
- [ ] ADR-0002's slot enumeration is explicitly judged — kept as illustration or
      reduced to a pointer — and the reasoning recorded.
- [ ] The plans-reproduce-the-design rule currently in XAS-027's `Scope
      Decisions` is either lifted somewhere that ships, or deliberately left in
      the epic with the reason recorded.
- [ ] `design-record` applies the rule when drafting: it does not copy a list
      into an ADR that another artifact owns.
- [ ] `plugin.json` and `marketplace.json` bumped (minor — behaviour change in
      `design-record`) and in agreement.
- [ ] All existing tests continue to pass.

**Out of scope**:
- Any change to `architecture-scan`. See the Description for why detection is
  the wrong instrument here.
- Enforcing the rule mechanically. It is a review-time and drafting-time rule.
- Re-litigating what the six ADRs decided. This is about how they state it.
