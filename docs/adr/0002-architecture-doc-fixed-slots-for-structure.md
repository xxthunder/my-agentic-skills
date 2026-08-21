# ADR-0002 — `architecture.md` uses fixed slots for structure, free-form for behaviour

**Status**: Accepted
**Date**: 2026-08-12
**Related**: [XAS-027](../backlog/xas-027.md), [XAS-027b](../backlog/xas-027b.md)

## Context

`architecture.md` is the artifact most prone to silent drift, and a stale
architecture document is worse than none because it lies with authority.

Two failure modes drive that drift, and they pull in opposite directions. With
no prescribed structure, each session has to decide whether to edit an existing
diagram or add another — and it will add, which is how a document becomes twelve
overlapping diagrams nobody trusts. With a rigid structure, things that are
genuinely flows get forced into box-and-line component diagrams and the insight
worth documenting is lost.

The target repos are also heterogeneous. C4's container concept fits a
multi-service system such as `xxthunder/homesmarthome` well, and barely applies
to `xxthunder/xxthunder-agentic-skills` itself — a marketplace whose plugins are
largely markdown. Any convention has to degrade gracefully rather than demand
empty sections.

## Decision

Structure gets **fixed, named slots** in a canonical order — Purpose, System
context, Containers, Components — so that a structural update is an *edit to a
known diagram* rather than an addition. Behaviour gets a **free-form** `Key
flows` slot where sequence, state or flow diagrams are added as the subject
demands.

New diagrams may only be added under `Key flows`. Structural slots are edited,
never appended to.

A slot with nothing to say carries an explicit one-line note — "Single
container; see Components" — never an empty heading and never a fabricated box.
Omission beats invention.

Diagrams are mermaid, inline in the document. `Decisions` links to the ADR index
and contains nothing else.

## Alternatives considered

- **Strict C4-lite** — context, container and component diagrams only, no
  behavioural views. Maximum consistency and the least to decide, but some
  things are genuinely flows, and forcing them into a component diagram loses
  what was worth writing down.
- **Purpose-driven, no fixed hierarchy** — whatever diagram each concern needs.
  Most expressive and adapts best to heterogeneous repos, but with no stable
  slot the append-instead-of-edit failure is close to certain.
- **Full C4, all four levels** including code-level diagrams. Rejected outright:
  they duplicate what the code and the IDE already show, drift within days, and
  carry the most maintenance for the least insight.
- **Diagrams as separate `.mmd` files.** Rejected: a single document that reads
  top to bottom serves the human-readable-record goal better, and inline mermaid
  is diffable and editable without a toolchain.

## Consequences

- `design-record` can target a named slot, which makes "update the architecture"
  a well-defined operation instead of a judgement call about where text goes.
- `architecture-scan` has a fixed shape to diff against, which is what makes a
  drift report possible at all.
- The honest-degradation rule means a thin repo produces a short document rather
  than a padded one, so the format stays usable in repos where C4 barely
  applies.
- `Key flows` is where entropy will accumulate, since it is the one slot without
  a stable identity. If the document ever becomes untrustworthy, that is where
  to look first.
