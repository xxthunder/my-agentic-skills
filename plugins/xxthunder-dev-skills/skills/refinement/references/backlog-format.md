# Backlog Format Reference

This defines the backlog structure, entry format, and conventions used by the refinement skill. Use this reference when creating a new backlog or adding entries to an existing one.

## File Structure

The backlog uses a flat folder with one file per item. All items live in the same directory regardless of status or hierarchy:

```
docs/backlog/
├── README.md             # Status legend, flat TOC, Notes
├── prefix-001.md         # Top-level item (story or epic)
├── prefix-002.md
├── prefix-003.md         # Epic (has substories)
├── prefix-003a.md        # First substory of PREFIX-003
├── prefix-003b.md        # Second substory of PREFIX-003
└── prefix-015.md
```

`README.md` is the **single source of truth for item status** — an item's status is determined by which section its link appears in.

### `README.md`

Contains only metadata and navigation — no item content, no hierarchy groupings. The TOC is flat: each item lives in the section that matches **its own** status — an epic and its substories may sit in different sections at the same time. The letter-suffix ID convention visually groups epic and substory *only within a single section* when sorted by ID.

```markdown
# Backlog

## Status Legend

- **Open** - Ready to be picked up
- **In Progress** - Currently being worked on
- **Done** - Completed

## Table of Contents

### Open
- [PREFIX-003b — Second substory](prefix-003b.md)
- [PREFIX-003c — Third substory](prefix-003c.md)
- [PREFIX-015 — Standalone story](prefix-015.md)

### In Progress
- [PREFIX-001 — Ongoing refinement](prefix-001.md)
- [PREFIX-003 — Epic title](prefix-003.md)
- [PREFIX-003a — First substory (being worked on)](prefix-003a.md)

### Done
- [PREFIX-002 — Completed item](prefix-002.md)

---

## Notes

- **ID prefix**: `PREFIX` (e.g., `HSH` for HomeSweetHome)
- Keep items actionable with clear acceptance criteria
- Do NOT list commit hashes in backlog entries — the backlog is part of the commit itself, so hashes are circular and go stale after squash/rebase
```

Note in the example above: `PREFIX-003` is an In-Progress epic. One of its substories (`PREFIX-003a`) has been pulled and appears next to the epic in `### In Progress`. The other two substories (`PREFIX-003b`, `PREFIX-003c`) are still `Open` and sit in `### Open`. This is the normal state while an epic is being worked through — substories scatter across sections as they transition individually.

**No "Stories under X" groupings.** Each item sorts into the section its own status dictates; ID-sorting within a section is enough to keep related IDs visually adjacent when they happen to share a status.

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

Two shapes of ID:

| Shape               | Meaning                                   | Example        |
|---------------------|-------------------------------------------|----------------|
| `PREFIX-###`        | Top-level item (story OR epic)            | `HSH-003`      |
| `PREFIX-###<letter>`| Substory under the matching top-level item | `HSH-003a`     |

- The prefix is a short, memorable abbreviation of the repository/project name (e.g., `HSH` for HomeSweetHome).
- The three-digit number is zero-padded and **global and sequential** across top-level items.
- Substory letters start at `a` and continue `b`, `c`, … in the order substories are added. No gaps are intentional.
- There is **no explicit "Epic" type field**. An item *is* an epic if (and only if) at least one `PREFIX-###<letter>` sibling file exists. Epic-ness is emergent — a top-level story is "promoted" to an epic simply by adding its first substory.
- The prefix is stored in the **Notes** section of `README.md` so it is always discoverable.

Examples:
- `HSH-003` — top-level story. Becomes an epic if/when `HSH-003a` is added.
- `HSH-003a`, `HSH-003b` — substories of `HSH-003`.
- `HSH-015` — top-level story with no substories.

### Allocating the next ID

**New top-level item**: scan all `prefix-*.md` files, extract the three-digit base number from each, take the maximum, increment by one.

**New substory under `PREFIX-NNN`**: scan for files matching `prefix-NNN<letter>.md`, take the latest letter used (or none), advance to the next letter (`a` if none yet). If the parent is currently a standalone story, no rename is needed — adding the first substory implicitly promotes it.

### Back-reference fields (do not use)

Do **not** add a `**Epic**: PREFIX-###` field inside substory files. The letter suffix encodes the parent — adding an explicit back-reference duplicates information and drifts on rename.

## Entry Fields

### Required fields (all entries)

| Field                  | Description                                              |
|------------------------|----------------------------------------------------------|
| **Status**             | `Open`, `In Progress`, or `Done (YYYY-MM-DD)` |
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

### Epic-only content

A top-level item that has (or will have) substories may include a narrative **Substories** section listing the children by ID and title. This is purely informative — the substory status comes from the README TOC, not from this list. Keep it as a bulleted list of `PREFIX-###<letter> — title` entries.

### Open entry

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

Same as Open but with `**Status**: In Progress` and some criteria may be checked off.

### Completed entry

File: `prefix-001.md`

```markdown
# [HSH-001] ✅ DONE - Brief descriptive title

**Status**: Done (YYYY-MM-DD)
**Priority**: Medium
**Component**: `path/to/affected/file.ext`

[... all other fields with all acceptance criteria checked ...]
```

### TOC entry format (in `README.md`)

```markdown
### Open
- [HSH-003c — Third substory (still open)](hsh-003c.md)
- [HSH-015 — Brief title](hsh-015.md)

### In Progress
- [HSH-001 — Backlog refinement](hsh-001.md)
- [HSH-003 — Epic title](hsh-003.md)
- [HSH-003a — First substory (being worked on)](hsh-003a.md)

### Done
- [HSH-002 — Completed item](hsh-002.md)
- [HSH-003b — Second substory (finished)](hsh-003b.md)
```

An epic and its substories are not constrained to share a section. Each row sits in the section for **its own** status.

## Epics and Status Cascade

An epic has no status of its own in the usual sense — its status is derived from its substories:

| Substory states                                        | Epic status   |
|--------------------------------------------------------|---------------|
| All substories `Done`                                  | `Done`        |
| At least one substory `In Progress`                    | `In Progress` |
| All substories `Open` (and none `In Progress`/`Done`)  | `Open`        |
| Mix of `Open` and `Done` (no `In Progress`)            | `In Progress` |

**Practical rule:** an epic stays out of `Done` as long as any substory is not `Done`.

When a substory transitions, the epic's status in `README.md` should be re-evaluated and moved to the appropriate section if it changed. The `backlog-ops` skill handles this cascade automatically; manual edits should follow the same rule.

An epic may also carry its own acceptance criteria (e.g., "End-to-end smoke test passes across all substories"). Those are checked independently. Avoid redundant ACs like "Child stories X/Y/Z completed" — substory completion is tracked by the cascade, not by a checkbox.

## Ongoing Refinement Item

Every backlog should include an ongoing refinement item that is never completed. All refinement commits reference this ID:

File: `prefix-0xx.md`

```markdown
# [PREFIX-0XX] Backlog refinement

**Status**: In Progress
**Priority**: —

**Description**:
Ongoing backlog refinement — create, review, clarify, and update user stories. Add research findings, scope decisions, acceptance criteria, and implementation details as needed. This item is never completed; all refinement commits reference this ID.
```

## Status Transitions

```
Open → In Progress → Done
```

When changing an item's status:
1. Move the link in `README.md` to the correct section — this is the authoritative status
2. Update the `**Status**` field inside the item file
3. For done items: add date and `✅ DONE -` prefix to heading
4. If the item is a substory, re-evaluate and adjust the parent epic's section per the cascade rule above

No file moves needed — all items stay in the same folder.

## Legacy IDs

A backlog created before the letter-suffix convention may contain Done substories that use bare sequential IDs (e.g., `PREFIX-018` was a child of `PREFIX-015` even though its ID has no letter suffix). These are left alone — renaming closed items churns git history and commit references for no practical gain. The convention applies going forward; the **Substories** list in an epic may mix legacy bare IDs and new letter-suffix IDs during the transition period.
