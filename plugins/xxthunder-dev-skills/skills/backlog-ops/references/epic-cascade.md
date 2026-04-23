# Epic Status Cascade

An **epic** in this backlog convention is any top-level item (`PREFIX-###`) that has at least one substory (`PREFIX-###<letter>`). Epic-ness is emergent — no explicit `Type` field. An item that had no substories becomes an epic the moment the first `<letter>` sibling is created.

The epic's status is **derived** from its substories, not asserted independently. The `backlog-ops` skill keeps the README table-of-contents consistent with this derivation.

## The Cascade Rule

Given an epic `PREFIX-NNN` and its substories `PREFIX-NNN<a..>`:

| Substory states                                        | Epic status   |
|--------------------------------------------------------|---------------|
| All substories `Done`                                  | `Done`        |
| At least one substory `In Progress`                    | `In Progress` |
| No `In Progress`; mix of `Open` and `Done`             | `In Progress` |
| All substories `Open`                                  | `Open`        |

**Plain English**: as long as any substory is not `Done`, the epic is not `Done`. The moment any substory leaves `Open`, the epic leaves `Open`.

## When the Cascade Fires

The `backlog-ops` skill evaluates the cascade in three situations:

1. **After pulling a substory** (`Open` → `In Progress`): if the parent is currently in `### Open`, move it to `### In Progress`.
2. **After completing a substory** (`In Progress` → `Done`): if all siblings including this one are now `Done`, *prompt* the user to close the epic. Do not close the epic silently — the user may have outstanding epic-level ACs (e.g., a smoke test spanning all substories).
3. **Drift detection, any operation**: if the parent's current section is inconsistent with the rule (e.g., parent in `### Open` while a substory is `In Progress`), quietly correct it and note the correction in the summary.

## Epic-Level ACs vs. Substory Completion

An epic may carry its own Acceptance Criteria — for example an end-to-end smoke test that only makes sense once all substories ship. These ACs are checked independently via the `check` operation and are evaluated in the **Complete** preconditions just like any other ACs.

**Anti-pattern to avoid**: an AC that says "Child stories X, Y, Z completed". That duplicates the cascade and goes stale on rename. The cascade tracks substory completion; ACs should track *additional* epic-level work (integration tests, docs, migrations) that isn't captured by any single substory.

## Legacy Bare-ID Substories

Backlogs created before the letter-suffix convention may have Done substories with bare sequential IDs (e.g., `PREFIX-018` was a child of `PREFIX-015`). These are not detectable by pattern — they look like independent top-level items.

**Policy**: the cascade considers only letter-suffix children (`PREFIX-NNN<letter>`) when computing epic status. Legacy bare-ID Done children are out of scope for automatic cascade. If the user wants the epic treated as Done-contingent on a legacy child, they must either rename the child (not recommended — breaks git history) or close the epic manually once they are satisfied.
