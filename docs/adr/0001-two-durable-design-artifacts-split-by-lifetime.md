# ADR-0001 — Two durable design artifacts, split by lifetime

**Status**: Accepted
**Date**: 2026-08-12
**Related**: [XAS-027](../backlog/xas-027.md)

## Context

The plugin needed somewhere for design to live. The obvious candidates all
already existed in some form and none of them worked alone:

- Backlog items hold design, but they close. Anything written in one is gone as
  soon as the work is done, which is precisely when someone starts needing it.
- `superpowers:brainstorming` writes a per-story spec to
  `docs/superpowers/specs/`, which duplicates the backlog item that should have
  held that design in the first place.
- `AGENTS.md` paragraphs pasted per repo drift as their wording evolves and only
  protect repos someone remembered to edit.

The framing question — "should design live in the epic, the story, or a separate
document?" — turned out to have no answer because it mixes two different axes.
A.SPICE and the V-Model organise artifacts by **abstraction level**, describing
the product, so they live as long as the product. Scrum organises by
**increment of value**, describing a change to the product, so its artifacts die
at Done. Sorting by lifetime instead of by item size makes the question
answerable.

## Decision

The plugin maintains exactly two durable design artifacts:

- **An ADR log** at `docs/adr/` — why a structural choice was made. Immutable;
  superseded rather than edited.
- **A living `architecture.md`** — what the structure currently is, with
  diagrams inline.

Everything else keeps its existing home. Design local to one change stays in the
backlog item's `Scope Decisions`. Decomposition stays in the epic. How the code
works stays in the code and its tests.

There is deliberately **no third place** for design to live.

## Alternatives considered

- **Add per-epic design documents** (a third artifact, for epics too large to
  describe in the item). Rejected: applying the lifetime test, nearly every such
  document turns out to be either an ADR or an edit to `architecture.md`. Its
  real cost is that every future session must decide which of three places a
  piece of design belongs in, and that decision will not be made consistently.
- **One artifact only** — fold decision rationale into `architecture.md` as a
  Decisions section. Rejected: it loses immutability, and an edited rationale
  silently erases the reasoning it replaced. That erased history is the main
  thing the record exists to keep.
- **Lift requirements into a standing requirements document**, closest to a
  literal A.SPICE SWE.1. Rejected: it duplicates what a story's Summary and
  Acceptance Criteria already say, and staying truthful would require the
  bidirectional traceability machinery deliberately left out of scope.

## Consequences

- The backlog already builds half a V-Model: a story's Summary and Description
  are its requirement, and its Acceptance Criteria and UAT blocks in the same
  file are that requirement's verification mirror. Only the middle band —
  architecture and its rationale — was missing, and these two artifacts are it.
- ADR immutability follows from this choice: a changed mind is a new ADR, and
  the only permitted edit to an accepted one is its status line at supersede
  time.
- `superpowers:brainstorming`'s spec-writing step now conflicts with this
  structure by design. Resolving that conflict is what
  [ADR-0004](0004-always-on-rule-is-orientation-not-enforcement.md) addresses.
- Repos that adopt the plugin but have no architecture yet documented start with
  an empty record, which is what
  [ADR-0005](0005-bootstrap-architecture-never-reconstruct-adrs.md) addresses.
- The rule is easy to state and therefore easy to follow: if it outlives the
  work, it does not go in the backlog item.
