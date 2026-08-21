# [XAS-027j] Correct the lifetime wording; lift durable design at close

**Status**: In Progress
**Priority**: High
**Component**: `plugins/xxthunder-dev-skills/hooks/session-start`,
`plugins/xxthunder-dev-skills/skills/design-record/references/architecture-format.md`,
`plugins/xxthunder-dev-skills/skills/backlog-ops/SKILL.md`,
`tests/dev/hooks/test_session_start.py`, `docs/backlog/xas-027.md`,
`plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`

**Related**: Closes a gap in [ADR-0001](../adr/0001-two-design-artifacts-split-by-lifetime.md)'s
lifetime rule. Extends the wire-up pattern from [XAS-027e](xas-027e.md) to a
fourth moment.

**Summary**:
As a maintainer, I want the lifetime rule stated in words that do not suggest
deletion, and I want the moment an item closes to ask whether anything inside it
outlives the item, so that design which still binds reaches the ADR log instead of being
left in a file nobody keeps current.

**Description**:
Two defects, one cause.

**The wording misleads.** The epic, the hook payload and
`architecture-format.md` all say a backlog item's design "dies at Done". Nothing
is deleted — the file stays in the repo forever. What ends at Done is the item's
authority about the present: nothing keeps it current afterwards. Read as
written, "dies" implies the repo throws work away, and it prompted exactly that
question in a live session.

**Nothing performs the lift.** ADR-0001 splits design by lifetime: what outlives
the work goes to the record, what is local to the change stays in the item. The
wire-up from [XAS-027e](xas-027e.md) covers three moments — `refinement` at
decision time, `tdd-workflow` and `commit-helper` at a boundary move. None of
them is the moment the split actually has to happen, which is when the item
closes. `backlog-ops` closes items and mentions neither `design-record` nor
ADRs.

The failure is already in this epic. [XAS-027g](xas-027g.md) records that the
hook replaces only the design-location half of the per-repo `AGENTS.md`
paragraph, and never the gate half, because
[ADR-0004](../adr/0004-always-on-rule-is-orientation-not-enforcement.md) commits
the hook to orientation. That constrains every repo that adopts the plugin. It
has no ADR. When 027g closes, it stops being findable.

**Scope Decisions**:
- **A closed item is history, not reference.** That is the replacement framing.
  The file is accurate about the change it describes, forever; it is not
  maintained, so it is not where a session looks for what is currently true.
- **The check prompts, it never authors and never blocks.** `backlog-ops` keeps
  its mechanics-only contract from [ADR-0003](../adr/0003-one-writer-for-the-design-record.md):
  it names what still looks binding and hands off to `design-record`. Declining
  closes the item anyway. A gate here would contradict
  [ADR-0004](../adr/0004-always-on-rule-is-orientation-not-enforcement.md).
- **No new ADR for this item.** The lifetime rule is unchanged — ADR-0001 stands
  as written. This corrects wording that describes it and adds a fourth wire-up
  point to an established pattern. Neither is a decision a competent engineer
  could have made otherwise.
- **ADR-0001's wording is corrected, and the immutability rule is scoped to
  match.** An earlier draft claimed the ADR never used the word. That was wrong:
  its Context said "its artifacts die at Done" — the authoritative statement of
  the lifetime rule carried the very metaphor this item removes, and the hook
  points sessions straight at `docs/adr/`.
  The old rule permitted only a `**Status**` edit, so correcting it required
  deciding what immutability actually protects. It protects *substance*: the
  decision, the alternatives, the consequences. It was never meant to preserve
  a misleading phrase. `adr-format.md` now permits exactly two edits — the
  status line at supersede time, and corrections that change no meaning — with
  the test being whether a reader would decide anything differently afterwards.
  A changed mind is still a new ADR. This correction is noted here so it is
  traceable to a reason rather than looking like silent drift.

- **The XAS-027a/b plan is deleted, not left alone.** An earlier draft left it
  under the epic's standing decision that plans are working documents. That
  decision has been tightened: the plan reproduced the finished text of three
  files rather than breaking work into tasks, so it was a spec under another
  name — and it was the last place still carrying the wording this item
  corrects. Its stories are closed, so it stopped binding when they landed.
- **The 027g ADR is not written here.** Recording that finding is the first real
  use of the new check and belongs with closing
  [XAS-027g](xas-027g.md), not with building the check.

**Acceptance Criteria**:
- [x] The hook payload states that a closed item stays as history and is not
      kept current, without implying anything is deleted.
- [x] `architecture-format.md` states the same, in the same terms.
- [x] [XAS-027](xas-027.md)'s lifetime table and surrounding prose use the
      corrected wording.
- [x] `backlog-ops`' Complete operation checks the item's Description and Scope
      Decisions for statements that outlive the item, names them, and offers to
      hand off to `design-record` before closing.
- [x] Declining the offer still closes the item. The check never blocks.
- [x] `backlog-ops`' Integration Points names `design-record`.
- [x] A test asserts the payload carries the history framing and not the death
      metaphor; it fails before the fix.
- [x] All existing tests pass.
- [x] `plugin.json` and `marketplace.json` bumped (minor) and in agreement.

**Out of scope**:
- Any enforcement. The check asks; it has no power to refuse.
- Inferring which ADR to write, or drafting it. `backlog-ops` names the
  candidate; `design-record` writes.
- Sweeping already-closed items for still-binding design left behind. Worth a separate
  item if the loss turns out to matter.
