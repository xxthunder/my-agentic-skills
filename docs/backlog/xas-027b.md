# [XAS-027b] ✅ DONE - `design-record` skill — `architecture.md` slots and diagram editing

**Status**: Done (2026-08-14)
**Priority**: High
**Component**: `plugins/xxthunder-dev-skills/skills/design-record/SKILL.md`,
`plugins/xxthunder-dev-skills/skills/design-record/references/architecture-format.md` (new),
`plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`

**Summary**:
As a maintainer, I want the same skill to edit a living architecture document
and its diagrams, so that a decision that moves a boundary updates the picture
of the system in the same breath that records why it moved.

**Description**:
The second half of `design-record`. Independently reviewable and independently
useful — a repo can run on ADRs alone for a while — but the pair is where the
value is, because most decisions worth recording also change the structure.

`architecture.md` uses **fixed slots for structure and free-form for
behaviour**. Structure gets named, stable sections so an update is an edit to a
known diagram; behaviour gets whatever diagram fits, added as needed. Without
stable slots each session has to decide whether to edit or append, and it will
append — which is how a document becomes twelve overlapping diagrams nobody
trusts.

The slots must **degrade honestly** across heterogeneous repos. C4's container
concept fits `homesmarthome` well and barely applies to a marketplace of
markdown skills. A slot with nothing to say gets one line saying so, never an
empty heading and never a fabricated box.

**Scope Decisions**:
- **The document's location is discovered, not hardcoded.** Look for
  `docs/architecture.md`, then root `ARCHITECTURE.md`; adopt whichever exists.
  Create `docs/architecture.md` when neither does. Ask only in the ambiguous
  case where both exist — and never create a second document alongside one that
  is already there, which would reintroduce the "third place for design to hide"
  this epic exists to remove. Root `ARCHITECTURE.md` is a convention in its own
  right and consuming repos will already have it.
  This rule is shared: [XAS-027c](xas-027c.md)'s payload states where the record
  lives and [XAS-027d](xas-027d.md) diffs against whatever the rule resolves to,
  so all three must use the same discovery order.
  **Deliberately not hand-written as an ADR.** It passes the three-part test and
  earns one, but [XAS-027f](xas-027f.md) requires at least one decision recorded
  *through* `design-record` rather than by hand — this is that decision. It
  lives here until the skill can write it.
- Canonical slot order: Purpose, System context, Containers, Components,
  Key flows, Glossary (optional), Decisions.
- Diagrams are mermaid, inline in `architecture.md`. One document that reads top
  to bottom, diffable, and editable by the agent without a toolchain.
- Structural slots are **edited, never appended to**. New diagrams may only be
  added under `Key flows`.
- No code-level diagrams. They duplicate what the code shows, drift within days,
  and cost the most maintenance for the least insight.
- The `Decisions` slot links to `docs/adr/README.md` and contains nothing else.
  A table of ADRs copied into `architecture.md` is a second source of truth that
  drifts the first time an ADR is added without updating the copy.
- Glossary is a slot in this document, not its own artifact — it pays off in
  domain-heavy repos and is dead weight elsewhere.

**Acceptance Criteria**:
- [x] `references/architecture-format.md` documents the slot list, the canonical
      order, the mermaid convention, and the honest-degradation rule.
- [x] The skill resolves the document's location by discovery — `docs/architecture.md`,
      then root `ARCHITECTURE.md` — adopting an existing file over creating a new
      one, and asking only when both exist.
- [x] The skill creates the `architecture.md` skeleton when the file is absent,
      at `docs/architecture.md`.
- [x] The skill edits a named slot in place; when the slot is missing it is
      inserted in canonical order rather than appended at the end of the file.
- [x] Structural slots are edited and never appended to; new diagrams are added
      only under `Key flows`.
- [x] A slot with nothing to say carries an explicit one-line note (e.g.
      "Single container; see Components"), never an empty heading and never a
      fabricated diagram.
- [x] The `Decisions` slot links to the ADR index and does not duplicate it.
- [x] The skill's trigger phrases cover "update the architecture doc", "redraw
      the container diagram", "document this module".
- [x] Stages edits only; never commits.
- [x] `plugin.json` and `marketplace.json` bumped (minor).
- [x] All existing tests continue to pass.
