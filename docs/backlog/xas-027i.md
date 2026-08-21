# [XAS-027i] ✅ DONE - Widen record discovery to nested layouts

**Status**: Done (2026-08-19)
**Priority**: High
**Component**: `plugins/xxthunder-dev-skills/hooks/session-start`,
`plugins/xxthunder-dev-skills/skills/design-record/references/architecture-format.md`,
`plugins/xxthunder-dev-skills/skills/architecture-scan/SKILL.md`,
`tests/dev/hooks/test_session_start.py`,
`plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`

**Related**: Found by [XAS-027g](xas-027g.md) on first contact with a real
consuming repo. Extends [ADR-0006](../adr/0006-record-locations-are-discovered.md)
rather than reversing it.

**Summary**:
As a maintainer of a repo that keeps its design record under a nested
`docs/architecture/` directory, I want the hook and the skills to find it, so
that the record I already keep is recognised instead of being reported as
absent.

**Description**:
The discovery order shipped in 1.11.0 looks for an ADR log at `docs/adr/` and an
architecture document at `docs/architecture.md` or root `ARCHITECTURE.md`.

`xxthunder/shortcuts` keeps neither. It has:

```
docs/architecture/
├── README.md
├── wsl-manager-c4.md
└── adr/
    └── 0001-lib-powershell-5.1-compatibility.md
```

So the hook told a live session that the repo has a backlog and stayed silent
about an ADR log and an architecture document that both exist. The failure is
worse than a missed mention: the hook's guard fires on *any* of the three
artifacts, so a repo keeping only `docs/architecture/adr/` and no
`docs/backlog/` would get complete silence — the hook concluding the
conventions are not in use, in a repo that demonstrably uses them.

The two-location rule was derived from this repository plus a convention read
about elsewhere, not from surveying real consumers. One consumer was enough to
break it.

**Scope Decisions**:
- **This extends ADR-0006, it does not supersede it.** That ADR's Consequences
  already name this exact escape: "If the two-location rule proves insufficient
  — a repo keeping the document somewhere else entirely — the cheap escape is to
  extend the search order, not to add configuration." The decision (discovered,
  not configured) stands unchanged; only the search list grows. No new ADR and
  no supersede.
- **Search order, first match wins.** ADR log: `docs/adr/`, then
  `docs/architecture/adr/`. Architecture document: `docs/architecture.md`, then
  root `ARCHITECTURE.md`, then `docs/architecture/README.md`.
- **`docs/architecture/README.md` counts as the architecture document.** A
  directory-based record uses its README as the entry point, the same way this
  repo's `docs/adr/README.md` is the ADR index.
- **Still no configuration.** Adding a per-repo setting would solve this case
  and reintroduce the per-repo upkeep the epic exists to remove.
- **The triplication gets worse, and that is acknowledged.** ADR-0006 already
  flagged that one rule living in three places is a drift risk. This widens the
  rule without fixing the duplication. Consolidating it is out of scope here and
  worth a separate item if it bites again.

**Acceptance Criteria**:
- [x] The hook finds an ADR log at `docs/architecture/adr/` when `docs/adr/` is
      absent, and reports the discovered path rather than a hardcoded one.
- [x] The hook finds `docs/architecture/README.md` as the architecture document
      when neither `docs/architecture.md` nor root `ARCHITECTURE.md` exists.
- [x] `docs/adr/` still wins over `docs/architecture/adr/` when both exist;
      `docs/architecture.md` still wins over the other two.
- [x] The guard fires for a repo whose *only* record artifact is a nested one —
      no backlog, no top-level ADR log — instead of staying silent.
- [x] `architecture-scan` and `design-record`'s `architecture-format.md` state
      the same widened order, so the three do not diverge.
- [x] Tests cover each new location and each precedence case; they fail before
      the fix.
- [x] Verified against the real `xxthunder/shortcuts` clone: the payload names
      `docs/architecture/adr/` and `docs/architecture/README.md`.
- [x] `plugin.json` and `marketplace.json` bumped (minor) and in agreement.
- [x] All existing tests continue to pass on both platforms.

**Observed** (2026-08-19), fixed hook against the real `xxthunder/shortcuts`
clone — all three artifacts now named, with discovered paths:

    - Backlog: docs/backlog/ — items are SC-###, substories SC-###a
    - Decisions: docs/architecture/adr/
    - Architecture: docs/architecture/README.md

Before the fix the last two were reported as absent.

**Out of scope**:
- Consolidating the discovery rule so it lives in one place instead of three.
- Any further location. Two ADR paths and three document paths cover what has
  actually been observed; adding speculative ones is how a search order becomes
  a guessing game.
