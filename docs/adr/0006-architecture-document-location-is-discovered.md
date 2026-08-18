# ADR-0006 — The architecture document's location is discovered, not hardcoded

**Status**: Accepted
**Date**: 2026-08-18
**Related**: [XAS-027b](../backlog/xas-027b.md), [XAS-027f](../backlog/xas-027f.md)

## Context

Three components need to find the same file: `design-record` writes it,
`architecture-scan` diffs against it, and the `SessionStart` hook names it when
stating what record exists in a repo. If they disagree about where it lives,
the record silently splits in two.

The obvious answer is to pick one path and hardcode it. That works for this
repository and fails for the ones the plugin is installed into. A root-level
`ARCHITECTURE.md` is a widely used convention in its own right, and a consuming
repo may already keep one. A skill that only knows `docs/architecture.md` would
walk past it and create a second document alongside — which is precisely the
"third place for design to hide" that [ADR-0001](0001-two-durable-design-artifacts-split-by-lifetime.md)
exists to prevent.

The epic already commits to discovery over configuration for the backlog ID
prefix, on the grounds that per-repo hook configuration reintroduces the
per-repo upkeep the epic removes. The same argument applies here.

## Decision

The document's location is resolved by discovery, in this order:

1. `docs/architecture.md` — use it if it exists.
2. Root `ARCHITECTURE.md` — use it if it exists.
3. Neither exists → create `docs/architecture.md`.
4. Both exist → **ask** which is authoritative. Do not guess, and do not merge
   them unprompted.

An existing document is always adopted over creating a new one. All three
components use this same order, and it must stay the same in all three.

## Alternatives considered

- **Hardcode `docs/architecture.md`, no discovery.** One path, no ambiguity,
  nothing to keep in sync. Rejected because a consuming repo with a root
  `ARCHITECTURE.md` would end up with two competing documents — the exact
  failure the record is meant to prevent, reintroduced by the tool meant to
  prevent it.
- **Make root `ARCHITECTURE.md` the default instead**, adopting
  `docs/architecture.md` only when already present. Rejected as a coin-flip on
  convention that would have changed what this repository dogfoods in
  [XAS-027f](../backlog/xas-027f.md) without being better in any way that could
  be articulated. `docs/` already holds `backlog/` and `adr/`, so the record
  stays together.
- **Per-repo configuration** naming the path. Rejected on the epic's standing
  ground: configuration is per-repo upkeep, and per-repo upkeep is what this
  work exists to remove.

## Consequences

- One rule now lives in three places — `design-record`, `architecture-scan` and
  the hook. That is a real duplication and a real drift risk; the mitigation is
  only that the format reference states the order once and the other two point
  at it. If they diverge, the record splits, which is the failure this ADR was
  written to avoid.
- The both-exist case asks rather than resolving. That is friction on a rare
  path, accepted so the skill never silently picks a loser.
- Every invocation pays a small discovery cost — two filesystem checks — rather
  than going straight to a known path.
- A repo that later moves its document from one location to the other needs no
  change to any skill, which is the payoff.
- If the two-location rule proves insufficient — a repo keeping the document
  somewhere else entirely — the cheap escape is to extend the search order, not
  to add configuration.
