# Backlog Format Reference

This defines the backlog structure, entry format, and conventions used by the refinement skill. Use this reference when creating a new backlog or adding entries to an existing one.

## File Structure

The backlog uses a flat folder with one file per item. All items live in the same directory regardless of status:

```
docs/backlog/
├── README.md             # Status legend, TOC grouped by status, Notes
├── prefix-001.md         # Each item is a standalone file
├── prefix-002.md
├── prefix-003.md
└── prefix-015.md
```

`README.md` is the **single source of truth for item status** — an item's status is determined by which section its link appears in.

### `README.md`

Contains only metadata and navigation — no item content:

```markdown
# Backlog

## Status Legend

- **IN PROGRESS** - Currently being worked on
- **TODO** - Ready to be picked up
- **DONE** - Completed

## Table of Contents

### In Progress
- [ID — Title](prefix-001.md)

### TODO
- [ID — Title](prefix-002.md)

### Done
- [ID — Title](prefix-003.md)

---

## Notes

- **ID prefix**: `PREFIX` (e.g., `HSH` for HomeSweetHome)
- Keep items actionable with clear acceptance criteria
- Do NOT list commit hashes in backlog entries — the backlog is part of the commit itself, so hashes are circular and go stale after squash/rebase
```

### Item files

Each item is a standalone file in the backlog folder. The heading is `#` (top-level, since it's the only item in the file):

```markdown
# [PREFIX-015] Brief descriptive title

**Status**: Open
**Priority**: Medium
**Component**: `path/to/affected/file.ext`

**Summary**:
As a [user role], I want [feature] so that [benefit].

**Description**:
[Problem statement. Current behavior. Why this matters.]

**Acceptance Criteria**:
- [ ] First verifiable criterion
- [ ] Second verifiable criterion
- [ ] All existing tests continue to pass
```

## Item ID Convention

Format: `[PREFIX-###]` — project prefix + zero-padded sequential number.

- The prefix is a short, memorable abbreviation of the repository/project name (e.g., `HSH` for HomeSweetHome).
- Numbers are **global and sequential** across all items — no per-type numbering, no gaps intentional.
- The prefix is stored in the **Notes** section of `README.md` so it is always discoverable.

Examples: `HSH-001`, `HSH-002`, `HSH-015`

When adding a new item, scan all existing `prefix-*.md` files in the backlog folder to find the highest number, then increment by one.

## Entry Fields

### Required fields (all entries)

| Field                  | Description                                              |
|------------------------|----------------------------------------------------------|
| **Status**             | `Open` (TODO), `Ongoing` (IN PROGRESS), or completed format (see below) |
| **Priority**           | `High`, `Medium`, `Low`, or `—` (none)                  |
| **Component**          | File path(s) affected (e.g., `roles/ssl-certify/`)       |
| **Summary**            | User story: "As a [user], I want [feature] so that [benefit]" |
| **Description**        | Detailed problem statement, current state, rationale     |
| **Acceptance Criteria**| Checkbox list: `- [ ] Criterion` (unchecked) / `- [x] Criterion` (checked) |

### Optional fields

| Field                    | When to include                                     |
|--------------------------|-----------------------------------------------------|
| **Depends on**           | When blocked by another item (e.g., `HSH-006`)     |
| **Related**              | When related to other items (not blocking)           |
| **Scope Decisions**      | When key architectural choices have been made        |
| **Technical Notes**      | Implementation-specific details (socket paths, config snippets) |
| **Dependencies**         | External system prerequisites                        |
| **Related Documentation**| Links to guides or external references               |

### Open / TODO entry

File: `prefix-015.md`

```markdown
# [HSH-015] Brief descriptive title

**Status**: Open
**Priority**: Medium
**Component**: `path/to/affected/file.ext`

**Summary**:
As a [user role], I want [feature] so that [benefit].

**Description**:
[Problem statement. Current behavior. Why this matters.]

**Acceptance Criteria**:
- [ ] First verifiable criterion
- [ ] Second verifiable criterion
- [ ] All existing tests continue to pass
```

### In Progress entry

Same as TODO but with `**Status**: Ongoing` and some criteria may be checked off.

### Completed entry

File: `prefix-001.md`

```markdown
# [HSH-001] ✅ COMPLETED - Brief descriptive title

**Status**: Completed (YYYY-MM-DD)
**Priority**: Medium
**Component**: `path/to/affected/file.ext`

[... all other fields with all acceptance criteria checked ...]
```

### TOC entry format (in `README.md`)

```markdown
### In Progress
- [HSH-014 — Backlog refinement](hsh-014.md)

### TODO
- [HSH-015 — Brief title](hsh-015.md)

### Done
- [HSH-001 — Brief title](hsh-001.md)
```

## Ongoing Refinement Item

Every backlog should include an ongoing refinement item that is never completed. All refinement commits reference this ID:

File: `prefix-0xx.md`

```markdown
# [PREFIX-0XX] Backlog refinement

**Status**: Ongoing
**Priority**: —

**Description**:
Ongoing backlog refinement — create, review, clarify, and update user stories. Add research findings, scope decisions, acceptance criteria, and implementation details as needed. This item is never completed; all refinement commits reference this ID.
```

## Status Transitions

```
Open (TODO) → Ongoing (IN PROGRESS) → Completed (DONE)
```

When changing an item's status:
1. Move the link in `README.md` to the correct section — this is the authoritative status
2. Update the `**Status**` field inside the item file
3. For completed items: add date and `✅ COMPLETED -` prefix to heading

No file moves needed — all items stay in the same folder.
