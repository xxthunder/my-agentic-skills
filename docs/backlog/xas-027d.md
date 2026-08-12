# [XAS-027d] `architecture-scan` skill — bootstrap and drift report

**Status**: Open
**Priority**: Medium
**Component**: `plugins/xxthunder-dev-skills/skills/architecture-scan/SKILL.md` (new),
`plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`

**Depends on**: [XAS-027b](xas-027b.md) — applying anything the scan proposes
goes through `design-record`.

**Summary**:
As a maintainer with repos that already have architecture but no
`architecture.md`, I want a skill that derives the real structure from the code
and compares it to what is documented, so that existing repos get a starting
record and documented repos stop drifting away from reality.

**Description**:
Bootstrap and drift detection are the same capability. Both read the codebase,
derive the real structure, and compare it against what is documented — bootstrap
is that comparison with an empty baseline. One skill, not two.

Without it, `architecture.md` in an existing repo only ever grows from the
changes made after adoption, so it stays incoherent for a long time in exactly
the repos where durable context is worth the most.

The skill is **read-only**. It proposes; `design-record` applies. That
reintroduces a two-skill step, and the reason it is acceptable here while it was
not for ADRs is frequency: recording a decision happens constantly and should be
one move, while a bootstrap or a sweep is occasional and produces a large
proposal worth reading before it lands. The payoff is that exactly one skill
knows the format, so conventions cannot diverge.
See [ADR-0003](../adr/0003-one-writer-for-the-design-record.md).

It does **not** reconstruct ADRs for past decisions. Rationale is not recoverable
from code, so an inferred ADR is confident fiction — the opposite of the record
this epic exists to build.
See [ADR-0005](../adr/0005-bootstrap-architecture-never-reconstruct-adrs.md).

**Scope Decisions**:
- Read-only. The skill never writes; approved proposals are applied via
  `design-record`.
- Omission beats invention: a slot the scan cannot derive is reported as "not
  yet documented", never as a plausible guess.
- ADR drift checking is scoped to what can be verified mechanically — ADRs whose
  referenced paths no longer exist. The skill does not claim to judge whether a
  decision is still honoured in general, because it cannot.
- **Deferred, deliberately not filed as a story:** a helper script emitting a
  compact structural inventory (directories, manifests, entry points,
  dependency edges) would cut token cost on large repos. It is speculative until
  the sweep proves too expensive in practice, and filing speculative work is how
  a backlog rots. Revisit only if the sweep is measurably too costly.

**Acceptance Criteria**:
- [ ] `SKILL.md` exists, is read-only by contract, and says so explicitly.
- [ ] The skill derives structure from directories, manifests, entry points and
      dependency edges.
- [ ] No `architecture.md` → produces a bootstrap proposal covering the fixed
      slots, explicitly marked as proposed.
- [ ] Populated `architecture.md` → produces a drift report covering:
      undocumented modules, documented modules that no longer exist, diagram
      nodes with no counterpart in the code, and ADRs whose referenced paths
      have disappeared.
- [ ] A slot the scan cannot derive is reported as "not yet documented"; the
      skill never fabricates structure.
- [ ] The skill explicitly does not reconstruct ADRs for past decisions.
- [ ] Applying a proposal routes through `design-record`; nothing lands without
      user approval.
- [ ] Trigger phrases cover "check the docs against reality", "is the
      architecture doc still true", "bootstrap the architecture doc".
- [ ] `plugin.json` and `marketplace.json` bumped (minor), and `plugin.json`'s
      `description` updated to list the new skill.
- [ ] All existing tests continue to pass.
