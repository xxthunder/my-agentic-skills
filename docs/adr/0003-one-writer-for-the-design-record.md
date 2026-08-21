# ADR-0003 — The design record has exactly one writer

**Status**: Accepted
**Date**: 2026-08-12
**Related**: [XAS-027](../backlog/xas-027.md), [XAS-027d](../backlog/xas-027d.md)

## Context

Two skills need to interact with the record: one that writes a decision or a
structural change, and one that reads the codebase and reports how far the
document has drifted from it. The obvious shape is for each to write what it
produces — the scanner applies its own bootstrap, the recorder applies its own
ADR — but then two skills hold the format, and formats held in two places
diverge.

There is a countervailing force. The seam already established in
`xxthunder-dev-skills` by XAS-025 splits judgement (`refinement`) from mechanics
(`backlog-ops`), and
`backlog-ops` explicitly refuses to author content. Following that seam strictly
would mean recording a decision always takes two invocations: one skill to write
the prose, another to place it. Recording decisions is the highest-frequency
operation in this whole design, and a two-step ritual on the common path is how
a practice quietly stops being followed.

## Decision

`design-record` is the **only writer** of the design record. It drafts ADR prose
itself and edits `architecture.md` directly.

`architecture-scan` is **read-only**. It derives structure, diffs it against the
document, and proposes; applying anything it proposes routes back through
`design-record`.

The frequency argument decides where the two-step is acceptable. Recording a
decision happens constantly and is one move. A bootstrap or a drift sweep is
occasional and produces a large proposal that should be read before it lands, so
an explicit apply step there is a feature rather than friction.

## Alternatives considered

- **Follow `backlog-ops` strictly** — a mechanics-only `architecture-ops` that
  places content authored elsewhere. Consistent with the existing seam, but it
  makes every ADR a two-skill dance on the highest-frequency path.
- **Let `architecture-scan` write its own output.** Removes the apply step for
  bootstrap, at the cost of two skills owning the format — and bootstrap output
  is inferred, so it is exactly the content that most deserves a review gate.
- **One omnibus skill** with `adr`, `arch`, `bootstrap` and `audit` modes.
  Fewest moving parts, but a description that must trigger on both "document
  this decision" and "is the architecture doc still true" triggers reliably on
  neither, and writing the record and auditing it are different acts sharing
  only a filename.
- **One skill per artifact** — separate `adr` and `architecture` skills. Sharpest
  triggers, but most decisions change both, so the common case becomes two
  skills that must be kept mutually consistent.

## Consequences

- `design-record` deliberately breaks `backlog-ops`' no-content-authoring rule.
  The skill must state that divergence and its reason in its own text, or a
  future session will notice the inconsistency, "fix" it, and reintroduce the
  two-step on the common path.
- The format lives in one place, so `architecture-scan` can be rewritten or
  replaced without touching how the record is written.
- Bootstrap and drift reports cannot land accidentally — nothing inferred
  reaches the document without explicit approval.
- If the apply step for sweeps turns out to be annoying in practice, the cheap
  fix is to let `architecture-scan` call `design-record` directly rather than to
  give it write access.
