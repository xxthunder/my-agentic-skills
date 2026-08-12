# ADR-0005 — Bootstrap architecture from code; never reconstruct ADRs

**Status**: Accepted
**Date**: 2026-08-12
**Related**: [XAS-027](../backlog/xas-027.md), [XAS-027d](../backlog/xas-027d.md)

## Context

Every repo this plugin targets already exists and already has an architecture —
it just has no `architecture.md`. The capture triggers only fire on change, so
without a bootstrap those repos would accrete documentation piecemeal and stay
incoherent for a long time, in exactly the repos where durable context is worth
the most.

The same argument appears to apply to decisions: the repos have a history of
choices, and reconstructing them would populate the ADR log immediately. It does
not actually apply, and the difference is what this decision turns on.

Structure is **present in the code** and can be derived from it. Rationale is
**not** — code shows what was chosen and never what was rejected or why. A
reconstructed ADR is therefore inference presented as history.

## Decision

`architecture-scan` bootstraps `architecture.md` from an existing codebase, and
does **not** reconstruct ADRs for past decisions.

A past decision earns an ADR when something revisits it — at which point there
is a real conversation to source the rationale from.

Where the scan cannot derive a slot, it says "not yet documented" rather than
guessing. Omission beats invention.

## Alternatives considered

- **Bootstrap both**, harvesting rationale from git history and from the `Scope
  Decisions` field that backlog items already carry. Defensible in this
  repository specifically, because those fields hold real rationale written at
  the time — they are genuine proto-ADRs. Rejected because the plugin must work
  in repos without that history, where the same mechanism degrades into
  plausible fiction, and a log that is trustworthy in some repos and not others
  is not trustworthy.
- **Forward-only, no bootstrap at all.** Cheapest and most honest: everything in
  the record was written by someone who knew. Rejected because
  `architecture.md` would stay a stub for months in every existing repo, which
  undercuts the durable-context goal precisely where it would be felt most.
- **Bootstrap later, once the format has proven itself.** Avoids bootstrapping
  into a shape later regretted, at the cost of leaving existing repos
  undocumented in the meantime. Rejected as unnecessary sequencing caution — the
  format is cheap to change and the proposals require approval anyway.

## Consequences

- The ADR log starts empty in adopted repos and fills only with decisions made
  from that point on. That is the correct shape: every entry was written by
  someone who actually knew.
- `architecture.md` and the ADR log will be out of step for a while — a
  documented structure whose rationale is largely unrecorded. Acceptable, and
  self-correcting as decisions get revisited.
- The rule generalises beyond bootstrap: it is the same principle that stops
  `design-record` from filling in an "Alternatives considered" section the
  conversation did not supply.
- Bootstrap and drift detection are the same capability — bootstrap is the diff
  against an empty baseline — so this decision costs one skill rather than two.
