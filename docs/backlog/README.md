# Backlog

## Status Legend

- **Open** - Ready to be picked up
- **In Progress** - Currently being worked on
- **Done** - Completed

## Table of Contents

### Open

**Epics**
- [XAS-003 — Multi-agent skill authoring (single source, multi-target)](xas-003.md)
- [XAS-004 — Marketplace tooling and CI](xas-004.md)
- [XAS-015 — Launch xxthunder-paperless-skills plugin](xas-015.md)

**Stories under XAS-003**
- [XAS-008 — Define canonical skill source format](xas-008.md)
- [XAS-009 — Build generator that emits Claude Code plugin artifacts](xas-009.md)
- [XAS-010 — Document how to add a new agent target](xas-010.md)

**Stories under XAS-004**
- [XAS-011 — Pre-commit validation of canonical source format](xas-011.md)
- [XAS-012 — Auto-sync version between plugin.json and marketplace.json](xas-012.md)
- [XAS-013 — CI check that generated artifacts match canonical sources](xas-013.md)

**Stories under XAS-015**
- [XAS-016 — Scaffold xxthunder-paperless-skills plugin and register in marketplace](xas-016.md)
- [XAS-017 — Migrate simplex-merge from user-global skills into the plugin](xas-017.md)
- [XAS-018 — Add naps2-scan skill (scan → OCR → merge → filename proposal)](xas-018.md)
- [XAS-019 — Add auto-file skill (sort into configurable folder structure)](xas-019.md)

### In Progress
- [XAS-001 — Backlog refinement](xas-001.md)

### Done
- [XAS-002 — Rename repo and restructure as agentic-skills marketplace](xas-002.md)
- [XAS-005 — Phase 1 — Rename GitHub repo and update URL references](xas-005.md)
- [XAS-006 — Phase 2 — Rename marketplace registry and update manifest descriptions](xas-006.md)
- [XAS-007 — Phase 2 — Rewrite README to describe marketplace purpose](xas-007.md)
- [XAS-014 — Phase 2 — Restructure to multi-plugin marketplace layout](xas-014.md)

---

## Notes

- **ID prefix**: `XAS` (xxthunder-agentic-skills)
- Epics group related stories; child stories reference their parent via the `**Epic**` field.
- Keep items actionable with clear acceptance criteria
- Do NOT list commit hashes in backlog entries — the backlog is part of the commit itself, so hashes are circular and go stale after squash/rebase
