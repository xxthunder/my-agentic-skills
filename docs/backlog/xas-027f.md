# [XAS-027f] ✅ DONE - Dogfood: this repo's own `architecture.md` and ADRs

**Status**: Done (2026-08-18)
**Priority**: Medium
**Component**: `docs/architecture.md` (new), `docs/adr/`

**Depends on**: [XAS-027a](xas-027a.md), [XAS-027b](xas-027b.md),
[XAS-027d](xas-027d.md)

**Summary**:
As a maintainer, I want this repository documented by the skills it ships, so
that the tooling is proven on a real repo before it is trusted in others.

**Description**:
The user acceptance test for the epic. Skills are markdown and cannot be unit
tested, so the verification that matters is whether they can document the thing
that produced them. If they cannot, they do not work.

This repo is also a useful hard case for honest degradation: it is a marketplace
of markdown skills, so C4's container concept has to map to something real
rather than be forced. It does — system context is the Claude Code host, the
marketplace, and consuming repos; containers are the two plugins; components are
the skills inside them.

The five ADRs recorded by hand while designing [XAS-027](xas-027.md) —
`0001` through `0005` — were written before `design-record` existed. Comparing
them against what the skill now produces is a direct check on the skill: any
discrepancy is either a defect in the skill or a flaw in the format, and the
resolution belongs in whichever is wrong.

**Observed** (2026-08-18):
- `architecture-scan` run against this repo produced a bootstrap proposal
  covering all seven slots. C4's container concept mapped cleanly — two
  independently installable plugins — so no slot needed a fabricated box, which
  was the hard case this substory existed to test.
- **Reconciliation found no discrepancies.** ADR-0006, written through
  `design-record`, is structurally identical to the hand-written ADR-0003: same
  heading shape, same header block, same four sections. Nothing needed fixing in
  the skill, the format reference, or the ADRs.
- The nominated decision — the architecture-document discovery rule parked in
  [XAS-027b](xas-027b.md)'s Scope Decisions — is now
  [ADR-0006](../adr/0006-architecture-document-location-is-discovered.md),
  recorded through the skill rather than by hand.
- The 24 ADR-log invariant tests from [XAS-027h](xas-027h.md) pass against the
  regenerated index, and every relative link in the ADRs and the architecture
  document resolves.
- Honest degradation was exercised once, on Glossary: only three terms in this
  repo carry explicit definitions, so the slot names those three rather than
  padding. No slot carries a "nothing to say" note, because every slot had
  something real.

**Acceptance Criteria**:
- [x] `architecture-scan` run against this repo produces a bootstrap proposal.
- [x] `docs/architecture.md` created via `design-record` from that proposal,
      with every fixed slot either populated honestly or carrying an explicit
      "nothing to say" note.
- [x] Containers map to the two plugins and components to their skills; no
      fabricated boxes.
- [x] The hand-written ADRs `0001`–`0005` are compared against what
      `design-record` produces for the same decisions; each discrepancy is
      resolved by fixing the skill, the format reference, or the ADR, and the
      choice is recorded.
- [x] At least one new decision made during this epic is recorded through the
      skill rather than by hand, exercising the full path. The nominated
      decision is the architecture-document discovery rule held in
      [XAS-027b](xas-027b.md)'s `Scope Decisions` precisely so that it is
      available for this — it earns an ADR and was left unwritten on purpose.
- [x] The ADR index at `docs/adr/README.md` matches the files on disk.
