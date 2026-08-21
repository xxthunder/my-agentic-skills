# ADR-0004 — The always-on rule is orientation, not enforcement

**Status**: Accepted
**Date**: 2026-08-12
**Related**: [XAS-027](../backlog/xas-027.md), [XAS-027c](../backlog/xas-027c.md)

## Context

Something has to tell a session that the design record exists, because skills
are pull-based: a skill only shapes behaviour once something invokes it, and
nothing would invoke a "the record lives here" skill at the moment
`superpowers:brainstorming` decides where to write its spec. `AGENTS.md` works
because it is push-based, but it is per-repo, drifts as its wording evolves, and
only protects repos someone remembered to edit.

The mechanism that generalises is a plugin `SessionStart` hook — the same one
`superpowers` uses to inject `using-superpowers` into every session without
anyone invoking it.

That settles the mechanism but not the tone. The original framing of XAS-027 was
enforcement: a backlog item must exist before design begins. Ranking the goals
for this work put a human-readable record first, durable agent context second,
traceability third, and discipline explicitly last — these are single-maintainer
repos with a responsible engineer, not a team needing guardrails.

## Decision

The hook payload is **orientation**: it states what record exists in this repo,
where it lives, and which skill writes it. It contains no refusal or gating
language, and nothing anywhere in this design blocks work because the record is
stale.

The one place the payload is directive is the conflict with
`brainstorming`'s spec-writing step, and there it **names that step explicitly**
rather than stating a general rule.

The hook is guarded on repo shape — silent unless the repo has at least one of
a backlog directory, an ADR log or an architecture document — and lists only the
artifacts actually present. The paths searched for each are given by
[ADR-0006](0006-record-locations-are-discovered.md); this decision deliberately
does not restate them, so that widening the search does not leave this ADR
stating a list that is no longer true.

## Alternatives considered

- **Enforcement** — refuse to design or implement before a backlog item exists,
  as the rule was originally written in `xxthunder/shortcuts`' `AGENTS.md`.
  Rejected: friction on small changes is a worse failure than a slightly stale
  document, because a workflow people route around protects nothing.
- **A general rule in the payload** — "designs live in the backlog". Rejected as
  insufficient: `brainstorming` carries an explicit instruction to write to
  `docs/superpowers/specs/`, and a general rule loses to a specific one. Naming
  the competing step is what makes the redirect operative.
- **Keep the per-repo `AGENTS.md` paragraph.** Rejected as the primary
  mechanism — it is the duplication this work removes — but retained as the
  safety net until the hook is observed working.
- **Fork or vendor `superpowers`** so `brainstorming` writes to the right place
  directly. Rejected: it redirects where output lands, which does not justify
  owning a fork of someone else's skill.

## Consequences

- Nothing in this design can guarantee the record is current. That is accepted:
  the sweep in `architecture-scan` is the only mechanism that reduces drift, and
  it runs when asked.
- Whether hook-injected text reliably outranks a peer plugin's skill instruction
  is unproven. The argument is that it arrives as session context rather than as
  a skill, which is how `superpowers` makes its own rule stick — but it is an
  argument, and [XAS-027g](../backlog/xas-027g.md) is where it gets tested
  against observation.
- If the hook loses to `brainstorming` in practice, the per-repo paragraph stays
  and the failure gets written up. A rule that works sometimes is worse than one
  honestly documented as needing local reinforcement.
- Hooks are Claude Code-specific, so this decision does not carry to the
  multi-agent targets in [XAS-003](../backlog/xas-003.md). The two skills do.
