# ADR Format

An Architecture Decision Record captures **why** a structural choice was made,
at the moment it was made, while the alternatives that lost are still known.
Code shows what was decided; only an ADR shows what else was on the table.

## Location and naming

ADRs live at `docs/adr/NNNN-kebab-title.md` relative to the repository root.
`NNNN` is four digits, zero-padded, sequential. **Numbers are never reused** —
not even for a rejected or superseded ADR, because references to a number
appear in commit messages and other ADRs that are not going to be rewritten.

If `docs/adr/` does not exist, create it along with a `README.md` index.

## Template

    # ADR-NNNN — Title in sentence case

    **Status**: Proposed
    **Date**: YYYY-MM-DD
    **Related**: [PREFIX-###](../backlog/prefix-###.md)

    ## Context

    The forces in play. What made a decision necessary, what constraints
    applied, and what tension had to be resolved. Written so a reader who
    was not there understands why this was hard.

    ## Decision

    What was chosen, stated in the present tense as a standing position
    rather than as a narrative of the meeting.

    ## Alternatives considered

    Each alternative that was genuinely on the table, with the reason it
    lost. An alternative nobody actually considered does not belong here.

    ## Consequences

    What follows from the decision — including the costs accepted and the
    cheap escape hatch if it turns out wrong. Not a list of benefits.

## Statuses

| Status | Meaning |
|--------|---------|
| `Proposed` | Drafted, not yet agreed |
| `Accepted` | Agreed and in force |
| `Rejected` | Considered and declined |
| `Superseded by ADR-NNNN` | Replaced by a later decision |

**Rejected ADRs stay in the log.** "We considered this and said no" is as useful
a record as a yes, and deleting it guarantees the same idea is re-litigated.

## Immutability

**An Accepted ADR is immutable in substance.** A changed mind is a new ADR, not
an edit to the old one — an edited ADR silently rewrites history and destroys
the only thing the log is for.

Exactly two edits are permitted:

1. Its `**Status**` line, at supersede time.
2. A correction that changes no meaning: a typo, a broken link, or wording that
   misleads about what the ADR already decided.

The test for the second is whether a reader would decide anything differently
after the change. If they would, it is a new ADR that supersedes — not an edit.
Note the correction in the backlog item that made it, so the change is
traceable to a reason rather than appearing as silent drift.

## The supersede path

When ADR-0009 replaces ADR-0004:

1. ADR-0009 gains a `**Supersedes**: [ADR-0004](0004-....md)` line in its header
   block, below `**Related**`.
2. ADR-0004's `**Status**` line becomes `Superseded by ADR-0009`, linked:
   `**Status**: Superseded by [ADR-0009](0009-....md)`.
3. **ADR-0004's body is not touched.** Not corrected, not annotated, not
   softened.

## The index is derived

`docs/adr/README.md` holds a table of ADRs and a `## Notes` section. **Where the
index and the files disagree, the files win** and the index is regenerated from
them.

This inverts the rule used by the backlog, whose `README.md` is authoritative.
The inversion is deliberate: the backlog README carries status that lives
nowhere else, while this table carries nothing the ADR files do not already
hold, so treating it as a cache is safe and treating it as a source is a second
place for the truth to live.

Index row format:

    | [NNNN](NNNN-kebab-title.md) | Title | Status | YYYY-MM-DD |

## Links point one way

An ADR names the backlog item that produced it, in `**Related**`. The backlog
item is **not** required to link back. One direction is free; two directions
cost an edit every time and rot silently when only one side is updated.
