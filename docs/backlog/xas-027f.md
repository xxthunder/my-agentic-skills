# [XAS-027f] Dogfood: this repo's own `architecture.md` and ADRs

**Status**: Open
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

**Acceptance Criteria**:
- [ ] `architecture-scan` run against this repo produces a bootstrap proposal.
- [ ] `docs/architecture.md` created via `design-record` from that proposal,
      with every fixed slot either populated honestly or carrying an explicit
      "nothing to say" note.
- [ ] Containers map to the two plugins and components to their skills; no
      fabricated boxes.
- [ ] The hand-written ADRs `0001`–`0005` are compared against what
      `design-record` produces for the same decisions; each discrepancy is
      resolved by fixing the skill, the format reference, or the ADR, and the
      choice is recorded.
- [ ] At least one new decision made during this epic is recorded through the
      skill rather than by hand, exercising the full path.
- [ ] The ADR index at `docs/adr/README.md` matches the files on disk.
