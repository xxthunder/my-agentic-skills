# `design-record` Skill Implementation Plan (XAS-027a + XAS-027b)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `design-record` skill — the single writer of a repo's durable design record — able to author ADRs (027a) and to edit a slotted `architecture.md` (027b).

**Architecture:** One skill directory under `plugins/xxthunder-dev-skills/skills/design-record/`, containing a `SKILL.md` that carries workflow and judgement, plus two reference files that carry the formats. The ADR half and the architecture half share the `SKILL.md` because most decisions produce both an ADR and an architecture edit, and splitting them across two skills would make the common case a two-invocation ritual (ADR-0003). The skill stages file edits and never commits, matching `backlog-ops`.

**Tech Stack:** Markdown only. No scripts, no Python, no new dependencies. Mermaid for diagrams, rendered by the reader, not by a toolchain.

## Global Constraints

Copied from `CLAUDE.md` and the epic's Scope Decisions. Every task's requirements implicitly include this section.

- **Version bump is mandatory.** Any change under `plugins/<plugin-name>/` bumps the version in **both** `plugins/xxthunder-dev-skills/.claude-plugin/plugin.json` (`"version"`) and `.claude-plugin/marketplace.json` (the matching `plugins[...].version`). These two values must never disagree in a commit.
- **Semantic versioning.** A new skill is a **minor** bump. XAS-028 took `1.5.0` then `1.6.0` on this branch (manifest, then its skill-prose behaviour change), so 027a lands `1.7.0` and 027b lands `1.8.0`. Confirm the baseline with `grep '"version"' plugins/xxthunder-dev-skills/.claude-plugin/plugin.json` before bumping rather than trusting these numbers — anything else landing on the branch first shifts them again.
- **Conventional commits.** Scope is the skill name: `feat(design-record): ...`. Body ends with `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`.
- **Skills are portable.** No repo-specific logic, paths, or assumptions in any file under `skills/`. Paths like `docs/adr/` are discovered or documented as conventions with a fallback, never hardcoded as "this repo's layout".
- **Stage, never commit.** The skill edits files and leaves them for the user. Only the implementing engineer commits, at the task boundaries below.
- **Never invent rationale.** Where a required section cannot be sourced from the conversation, the skill asks. A fabricated "Alternatives considered" reads as history and is not.
- **Out of scope for this plan:** a pytest check that `plugin.json` and `marketplace.json` versions agree. That is XAS-004b's deliverable — do not add it here.

## File Structure

| File | Responsibility | Task |
|------|----------------|------|
| `plugins/xxthunder-dev-skills/skills/design-record/references/adr-format.md` | The ADR format: template, statuses, numbering, immutability, supersede path, index-is-derived rule | 1 |
| `plugins/xxthunder-dev-skills/skills/design-record/SKILL.md` | Trigger phrases, the three-part test, the ADR workflow, the never-invent guardrail, the `backlog-ops` divergence statement | 2 |
| `plugins/xxthunder-dev-skills/.claude-plugin/plugin.json` | Manifest: version `1.7.0` → `1.8.0`, `description` lists the new skill | 3, 6 |
| `.claude-plugin/marketplace.json` | Registry: matching version and description | 3, 6 |
| `README.md` | The `xxthunder-dev-skills` skill table gains a `design-record` row | 3 |
| `plugins/xxthunder-dev-skills/skills/design-record/references/architecture-format.md` | The `architecture.md` format: slot list, canonical order, mermaid convention, honest-degradation rule | 4 |
| `plugins/xxthunder-dev-skills/skills/design-record/SKILL.md` (modified) | Adds the architecture workflow: skeleton creation, slot editing, insert-in-canonical-order | 5 |

**Verification note.** These deliverables are markdown skills, which pytest cannot exercise. There is no unit test to write and the plan does not pretend otherwise. Verification is two things: a structural check against the acceptance criteria, and a **rehearsal** — invoking the skill against a decision whose correct output already exists on disk (ADRs `0001`–`0005`, written by hand) and comparing. Tasks 3 and 6 carry those rehearsals. The full reconciliation is XAS-027f's job; these are the smoke tests.

---

### Task 1: ADR format reference

**Files:**
- Create: `plugins/xxthunder-dev-skills/skills/design-record/references/adr-format.md`

**Interfaces:**
- Consumes: nothing.
- Produces: the canonical ADR template and rule set that `SKILL.md` (Task 2) links to and that Task 3's rehearsal is checked against. Section headings this file defines and later tasks depend on by name: `## Context`, `## Decision`, `## Alternatives considered`, `## Consequences`.

- [ ] **Step 1: Write the reference file**

Create the file with this content. The template must match the ADRs already on disk at `docs/adr/0001`–`0005` exactly — heading shape `# ADR-NNNN — Title`, then `**Status**:` / `**Date**:` / `**Related**:` lines, then the four sections. Any divergence here manufactures a false discrepancy for XAS-027f.

```markdown
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

**An Accepted ADR is immutable.** The only permitted edit to an existing ADR is
its `**Status**` line at supersede time. A changed mind is a new ADR, not an
edit to the old one — an edited ADR silently rewrites history and destroys the
only thing the log is for.

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
```

- [ ] **Step 2: Verify the template matches the ADRs on disk**

Run: `head -6 docs/adr/0003-one-writer-for-the-design-record.md` and `grep -n '^## ' docs/adr/0003-one-writer-for-the-design-record.md`

Expected: header lines `# ADR-0003 — The design record has exactly one writer`, `**Status**: Accepted`, `**Date**: 2026-08-12`, `**Related**: ...`; and section headings exactly `## Context`, `## Decision`, `## Alternatives considered`, `## Consequences`. If the reference file disagrees with this output on heading text or casing, fix the reference file — the existing ADRs are the baseline.

- [ ] **Step 3: Verify the index rules match the existing index**

Run: `grep -n 'derived\|never reused\|immutable' docs/adr/README.md`

Expected: three hits, matching the index-is-derived, numbering, and immutability rules just written. The reference file must not contradict the `## Notes` section already in `docs/adr/README.md`.

No commit yet — this file is unusable without Task 2's `SKILL.md`.

---

### Task 2: `design-record` SKILL.md — the ADR half

**Files:**
- Create: `plugins/xxthunder-dev-skills/skills/design-record/SKILL.md`

**Interfaces:**
- Consumes: `references/adr-format.md` from Task 1, linked as `[references/adr-format.md](references/adr-format.md)`.
- Produces: the skill's `name: design-record` and its frontmatter `description`, which Task 5 extends and which XAS-027c's hook payload names. The `## The three-part test` section is referenced by XAS-027e's `refinement` wire-up by that heading.

- [ ] **Step 1: Write `SKILL.md`**

Match the house style of `skills/backlog-ops/SKILL.md`: YAML frontmatter with `name`, a quoted `description` ending in explicit trigger phrases, `user_invocable: true`, then an HTML source comment, then the body.

```markdown
---
name: design-record
description: "Record a design decision as an ADR, or update the living architecture document, in a repo that keeps a durable design record. Drafts the ADR body from the conversation, allocates the next number, maintains the ADR index, and edits named sections of architecture.md. Stages file edits only; never produces its own commit. Trigger with: 'record an ADR', 'document this decision', 'we decided X — write it up', 'why did we choose Y — capture it', 'update the architecture doc'."
user_invocable: true
---

<!-- Source: https://github.com/xxthunder/xxthunder-agentic-skills/tree/develop/plugins/xxthunder-dev-skills/skills/design-record -->

# Design Record

Writes the two artifacts that outlive a unit of work: the **ADR log** at
`docs/adr/`, and the living **`docs/architecture.md`**. Formats live in
[references/adr-format.md](references/adr-format.md) and
[references/architecture-format.md](references/architecture-format.md).

This skill **stages file edits only**. It never creates a commit. Commits are
the user's call — typically via `commit-helper` — so a record change can ride in
the same commit as the code change that justifies it.

## Why this skill authors prose, unlike `backlog-ops`

`backlog-ops` refuses to author content: it applies mechanical lifecycle
operations and leaves all writing to `refinement`. This skill deliberately
breaks that seam and drafts ADR bodies itself.

The reason is frequency. Most decisions worth recording produce both an ADR and
an architecture edit, so splitting authorship across a conversation skill and a
mechanics skill would make recording a decision a two-invocation ritual on the
highest-frequency path in the whole design — and a two-step ritual on the common
path is how a practice quietly stops being followed.

**Do not "fix" this inconsistency.** It is a considered divergence, recorded in
ADR-0003 of this skill's home repository. Removing it reintroduces the friction
it exists to avoid.

## When This Skill Triggers

| Trigger phrase | Operation | Section |
|----------------|-----------|---------|
| "record an ADR", "document this decision", "write up why we chose X" | record decision | [Recording a decision](#recording-a-decision) |
| "supersede ADR-0004", "we're changing our mind about X" | supersede | [Superseding](#superseding-an-adr) |
| "regenerate the ADR index", "the index is out of date" | reindex | [The index](#maintaining-the-index) |
| "update the architecture doc", "redraw the container diagram", "document this module" | edit architecture | [Editing architecture.md](#editing-architecturemd) |

Do **not** trigger on:
- "let's refine", "add a new story", "prioritise the backlog" — that is `refinement`.
- "start XAS-025", "close XAS-025", "tick AC 2" — that is `backlog-ops`.
- "check the docs against reality", "is the architecture doc still true" — that
  is `architecture-scan`, which is read-only and proposes changes this skill
  then applies.

## The three-part test

Not every decision earns an ADR. A log that records everything is a log nobody
reads. **All three must hold:**

1. **The consequences outlive the change.** After the story is Done and its
   backlog item is closed, does this still constrain what the repo can do?
2. **A competent engineer could have chosen otherwise.** If there was only one
   sensible option, there was no decision — just work.
3. **The reason is not recoverable from the code.** If reading the
   implementation makes the rationale obvious, the code is already the record.

**When a request fails the test, decline and redirect.** Say which part it fails
and point at the alternative:

- Fails (1) — rationale local to this change → the backlog item's
  `**Scope Decisions**:` field.
- Fails (2) or (3) → nowhere. Not every choice needs a paper trail, and saying
  so is part of this skill's job.

The escalation ladder, in full: trivial → nothing; local to this change →
`Scope Decisions`; outlives the change → ADR.

## Recording a decision

### Step 1: Apply the three-part test

Run the test above before doing anything else. If it fails, redirect and stop.

### Step 2: Locate the log and allocate a number

1. Find the ADR directory — `docs/adr/` by convention. If it is absent, say so
   and offer to bootstrap it (Step 6 handles the index).
2. List `docs/adr/NNNN-*.md`. Take the **maximum** leading number, increment by
   one, zero-pad to four digits.
3. Never reuse a number, including numbers belonging to Rejected or Superseded
   ADRs. If the directory is empty, the first ADR is `0001`.

### Step 3: Draft the body from the conversation

Draft `## Context`, `## Decision`, `## Alternatives considered` and
`## Consequences` from what was actually said.

**Never invent rationale.** This is the guardrail that matters most in this
skill. If the conversation does not contain why an alternative lost, **ask** —
do not fill the section in with something plausible. A fabricated
"Alternatives considered" reads as history and is not, which is strictly worse
than an absent one, because a reader cannot tell the difference.

Specifically, ask rather than infer when:
- An alternative is named but the reason it lost was never stated.
- The `## Consequences` would otherwise list only benefits — a decision with no
  accepted cost usually means the cost was not discussed.
- The `## Context` would have to assert a constraint nobody mentioned.

### Step 4: Set the header block

`**Status**: Proposed` unless the user has clearly already agreed, in which case
`Accepted`. `**Date**` is today's — read it from the environment or ask; never
fabricate it. `**Related**` links the backlog item that produced the decision,
if there is one.

### Step 5: Write the file

`docs/adr/NNNN-kebab-title.md`. The title is sentence case, kebab-cased for the
filename, and short enough to read in an index row.

### Step 6: Update the index

Add the row to `docs/adr/README.md` per
[Maintaining the index](#maintaining-the-index). Create that file if absent.

### Step 7: Report

State the path written, the number allocated, the status, and that the change is
staged and uncommitted.

## Superseding an ADR

1. Write the **new** ADR through the normal flow, adding a `**Supersedes**:`
   line linking the old one.
2. Edit the old ADR's `**Status**` line to
   `Superseded by [ADR-NNNN](NNNN-....md)`.
3. **Touch nothing else in the old file.** Its body is history and stays wrong
   if it was wrong.
4. Update both rows in the index.

## Maintaining the index

`docs/adr/README.md` carries a table of all ADRs and a `## Notes` section
stating the conventions.

**The index is derived from the files.** Where they disagree, the files win —
regenerate the table by scanning `docs/adr/NNNN-*.md` and reading each one's
title, `**Status**` and `**Date**`. Do not resolve a disagreement the other way.

When bootstrapping `docs/adr/` from nothing, create `README.md` with the table
and a `## Notes` section covering: the derived-index rule, sequential
non-reused numbering, immutability of Accepted ADRs, the status values, the
three-part test, and the one-way linking rule.

## Editing architecture.md

See [references/architecture-format.md](references/architecture-format.md).

## What This Skill Does NOT Do

- **No commits.** Ever. The record edit rides in the user's next commit.
- **No invented rationale.** It asks instead. See Step 3.
- **No reconstructed ADRs for past decisions.** Rationale is not recoverable
  from code, so an ADR inferred from a repo's current state is confident
  fiction — the opposite of what this log is for.
- **No editing an Accepted ADR's body.** Only its `**Status**` line, only at
  supersede time.
- **No reading the codebase to find drift.** That is `architecture-scan`.
- **No backlog status changes.** That is `backlog-ops`.

## Guidelines

- **Ask rather than guess, every time.** The cost of one question is a
  sentence; the cost of a fabricated alternative is a record nobody can trust.
- **Decline decisions that fail the three-part test**, and say which part.
- **Preserve file formatting.** Do not reflow prose, renumber, or touch lines
  the operation does not require.
- **Never auto-commit.** Always leave changes staged.

## Integration Points

- **`refinement`** applies the three-part test during its Architecture topic and
  hands off here for decisions that pass; decisions that fail stay in the
  backlog item's `Scope Decisions`.
- **`architecture-scan`** is read-only and proposes; this skill applies what the
  user approves.
- **`commit-helper`** commits the staged record edit alongside the code change.
```

- [ ] **Step 2: Verify the frontmatter parses and triggers do not collide**

Run: `head -5 plugins/xxthunder-dev-skills/skills/design-record/SKILL.md` and
`grep -o "Trigger with: [^\"]*" plugins/xxthunder-dev-skills/skills/*/SKILL.md`

Expected: valid YAML frontmatter delimited by `---`, and no trigger phrase in `design-record`'s description appearing in `refinement`'s or `backlog-ops`' description. If "document" or "decision" collides, sharpen this skill's phrases — do not edit the other skills here; that is XAS-027e.

- [ ] **Step 3: Verify the reference link resolves**

Run: `ls plugins/xxthunder-dev-skills/skills/design-record/references/`

Expected: `adr-format.md` present. The link to `architecture-format.md` will dangle until Task 4 — that is expected and is fixed there, not worked around by removing the link.

No commit yet — Task 3 bumps the version and commits both files together, because a skill added without its version bump violates `CLAUDE.md`.

---

### Task 3: Rehearse the ADR half, bump to 1.7.0, commit (closes XAS-027a)

**Files:**
- Modify: `plugins/xxthunder-dev-skills/.claude-plugin/plugin.json` (`version`, `description`)
- Modify: `.claude-plugin/marketplace.json` (matching `version`, `description`)
- Modify: `README.md` (skill table row)
- Modify: `docs/backlog/xas-027a.md` (tick acceptance criteria)
- Modify: `docs/backlog/README.md` (status move)

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: plugin version `1.7.0`, the baseline every later task bumps from.

- [ ] **Step 1: Rehearse the skill against a known-good ADR**

This is the substitute for a unit test. Read `SKILL.md` as if invoked, and walk the "Recording a decision" flow for the decision already recorded as ADR-0003, using only what `docs/backlog/xas-027.md` and `docs/adr/0003-*.md`'s Context section contain as the "conversation".

Check four things:
1. Number allocation on the real directory yields `0006` (max is `0005`).
2. The four section headings produced match ADR-0003's exactly.
3. The three-part test passes for this decision — confirm you can state which part each of the rejected alternatives fails.
4. At least one section triggers the ask-don't-invent rule, since the source material is thinner than a live conversation. If nothing triggers it, the guardrail is too weak — strengthen Step 3's ask-list in `SKILL.md`.

Record the outcome in the commit body. If any check fails, fix `SKILL.md` or `adr-format.md` before proceeding.

- [ ] **Step 2: Bump both version fields**

`plugin.json` and `marketplace.json` both move `"version": "1.6.0"` → `"1.7.0"`, and both `description` strings gain the new skill:

```
Reusable Claude Code skills: refinement, retrospective, commit-helper, tdd-workflow, backlog-ops, design-record
```

- [ ] **Step 3: Verify the two versions agree**

Run: `grep -h '"version"' plugins/xxthunder-dev-skills/.claude-plugin/plugin.json .claude-plugin/marketplace.json`

Expected: `1.7.0` appears for the dev-skills plugin in both files. `xxthunder-paperless-skills` stays at `0.2.0` — a change in one plugin does not bump the other.

- [ ] **Step 4: Add the README row**

`README.md`'s `### xxthunder-dev-skills` table is sorted alphabetically by skill name, so `design-record` goes between `commit-helper` and `refinement`:

```markdown
| [**design-record**](plugins/xxthunder-dev-skills/skills/design-record/SKILL.md) | Durable design record — drafts ADRs with numbering and a derived index, and edits the slotted `architecture.md` |
```

Verify with: `grep -n 'design-record\|commit-helper\|refinement' README.md` — expected order is `commit-helper`, `design-record`, `refinement`.

- [ ] **Step 5: Run the existing test suite**

Run: `uv run --group dev pytest -q`

Expected: all existing tests pass. Nothing in this task touches Python, so a failure here means something unrelated broke and must be investigated before committing, not after.

- [ ] **Step 6: Tick the acceptance criteria and move status**

Use the `backlog-ops` skill on `XAS-027a` — pull it to In Progress if it is still Open, tick each satisfied AC, then complete it. Do not hand-edit `docs/backlog/README.md`; the cascade will move the `XAS-027` epic to In Progress.

- [ ] **Step 7: Commit**

```bash
git add plugins/xxthunder-dev-skills/skills/design-record/ \
        plugins/xxthunder-dev-skills/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json README.md \
        docs/backlog/xas-027a.md docs/backlog/README.md
git commit -m "feat(design-record): add ADR authoring, numbering and index (XAS-027a)

Adds the first half of the design-record skill: it drafts an ADR body from
the conversation, allocates the next four-digit number, maintains the derived
index at docs/adr/README.md, and handles the supersede path without touching
a superseded ADR's body.

The skill authors prose, unlike backlog-ops. SKILL.md states that divergence
and its reason so a later session does not 'fix' the inconsistency and
reintroduce a two-invocation ritual on the highest-frequency path.

Rehearsed against the hand-written ADR-0003; full reconciliation is XAS-027f.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: Architecture format reference

**Files:**
- Create: `plugins/xxthunder-dev-skills/skills/design-record/references/architecture-format.md`

**Interfaces:**
- Consumes: nothing from earlier tasks. Resolves the dangling link left by Task 2.
- Produces: the canonical slot names and order that Task 5's `SKILL.md` section and XAS-027d's `architecture-scan` both depend on by name: `## Purpose`, `## System context`, `## Containers`, `## Components`, `## Key flows`, `## Glossary`, `## Decisions`.

- [ ] **Step 1: Write the reference file**

```markdown
# `architecture.md` Format

One document, read top to bottom, describing how the product is put together.
It has the same lifetime as the product — unlike a backlog item, which dies at
Done.

## Where the document lives

Discovered, not hardcoded. In order:

1. `docs/architecture.md` — use it if it exists.
2. Root `ARCHITECTURE.md` — use it if it exists. This is a widely used
   convention in its own right, and a consuming repo may already have one.
3. Neither exists → create `docs/architecture.md`.
4. Both exist → **ask**. Do not guess, and do not merge them unprompted.

**Never create a second document alongside one that already exists.** That is
the "third place for design to hide" the whole record exists to prevent.

## Fixed slots for structure, free-form for behaviour

Structure gets **named, stable sections** so that an update is an edit to a
known diagram. Behaviour gets whatever diagram fits, added under `Key flows` as
needed.

Without stable slots, every session has to decide whether to edit or append —
and it will append, because appending is safe and editing requires
understanding what is already there. That is how a document becomes twelve
overlapping diagrams nobody trusts.

## Canonical slot order

1. `## Purpose` — what the system is for, in a few sentences.
2. `## System context` — the system, its users, and the external things it
   talks to. C4 level 1.
3. `## Containers` — separately deployable or independently installable units.
   C4 level 2.
4. `## Components` — the significant parts inside a container. C4 level 3.
5. `## Key flows` — how a request, a job, or a workflow moves through the
   parts. The only slot new diagrams may be added to.
6. `## Glossary` — optional. Domain terms and what they mean here.
7. `## Decisions` — a link to the ADR index. Nothing else.

Slots appear in this order. A slot inserted later goes into its **canonical
position**, not at the end of the file.

## Structural slots are edited, never appended to

`Purpose`, `System context`, `Containers` and `Components` each hold **one**
current description. When the structure changes, the existing text and diagram
are edited to match. A second container diagram is never added below the first.

`Key flows` is the exception: it holds many diagrams, one per flow, and grows.

## Honest degradation

Not every repository has something to say in every slot. C4's container concept
fits a multi-service system well and barely applies to, say, a marketplace of
markdown skills.

**A slot with nothing to say gets one explicit line saying so.** For example:

    ## Containers

    Single container — the repository is installed as one unit. See Components.

Never an empty heading, and **never a fabricated box** to make the diagram look
complete. An invented container is worse than an admitted absence, because a
reader cannot tell it was invented.

## Diagrams

Mermaid, inline, in fenced ` ```mermaid ` blocks. One document that reads top to
bottom, diffs cleanly in review, and is editable without a toolchain.

**No code-level diagrams** — no class diagrams, no function call graphs. They
duplicate what the code already shows, drift within days, and cost the most
maintenance for the least insight. C4 level 4 is deliberately not a slot.

## The Decisions slot

    ## Decisions

    Recorded as ADRs — see [docs/adr/README.md](adr/README.md).

**A table of ADRs is never copied into `architecture.md`.** A copy is a second
source of truth that drifts the first time an ADR is added without updating it,
and the drift is silent.

## Skeleton

When `docs/architecture.md` is absent, create it with every slot present, each
either populated or carrying an honest one-line note:

    # Architecture

    ## Purpose

    ## System context

    ## Containers

    ## Components

    ## Key flows

    ## Glossary

    ## Decisions

    Recorded as ADRs — see [docs/adr/README.md](adr/README.md).
```

- [ ] **Step 2: Verify the dangling link from Task 2 now resolves**

Run: `ls plugins/xxthunder-dev-skills/skills/design-record/references/`

Expected: both `adr-format.md` and `architecture-format.md`.

No commit yet — Task 5 adds the workflow that makes this reference usable.

---

### Task 5: `SKILL.md` — the architecture half

**Files:**
- Modify: `plugins/xxthunder-dev-skills/skills/design-record/SKILL.md` — the `## Editing architecture.md` section, which Task 2 left as a heading plus a single pointer line, and the frontmatter `description`

**Interfaces:**
- Consumes: `references/architecture-format.md` from Task 4; the `SKILL.md` structure from Task 2.
- Produces: the completed skill. XAS-027c's hook payload and XAS-027e's wire-up both point at it as a whole.

- [ ] **Step 1: Replace the stub section**

Replace the `## Editing architecture.md` heading and its single pointer line, written in Task 2, with:

```markdown
## Editing architecture.md

Format, slot list and canonical order live in
[references/architecture-format.md](references/architecture-format.md). This
section is the workflow.

### Step 1: Locate or create the document

Resolve the path by discovery, in the order given in the format reference:
`docs/architecture.md`, then root `ARCHITECTURE.md`, then create
`docs/architecture.md` if neither exists, and ask if both do. If it is absent,
create the skeleton with
**every** slot present, each either populated or carrying an honest one-line
note. Do not create a partial document intending to fill it in later — the
missing slots are what a later session appends to instead of editing.

### Step 2: Identify the slot

Map the change to exactly one slot. A change that seems to touch several
usually means the structural change is larger than described — say so and ask,
rather than editing four slots on an assumption.

### Step 3: Edit in place

- If the slot exists, **edit its content**. Do not append a second diagram to a
  structural slot.
- If the slot is missing, insert it at its **canonical position** in the order
  above — never at the end of the file.
- If the change is a new behavioural flow, add a diagram under `## Key flows`.
  This is the only slot that grows.

### Step 4: Degrade honestly

If the slot has nothing real to say for this repository, write the one-line
note. Never leave an empty heading, and never invent a box to fill a diagram.

### Step 5: Report

State which slot changed, whether it was edited or inserted, and that the
change is staged and uncommitted.
```

- [ ] **Step 2: Extend the frontmatter description**

The `description` written in Task 2 already names architecture triggers. Confirm it covers all three required phrases and add any that are missing: "update the architecture doc", "redraw the container diagram", "document this module".

- [ ] **Step 3: Verify no structural slot is described as appendable**

Run: `grep -n 'append' plugins/xxthunder-dev-skills/skills/design-record/SKILL.md plugins/xxthunder-dev-skills/skills/design-record/references/architecture-format.md`

Expected: every hit is a prohibition ("never appended to", "do not append") or the single `Key flows` exception. Any hit permitting appends to a structural slot is a defect — fix it.

---

### Task 6: Bump to 1.8.0, commit (closes XAS-027b)

**Files:**
- Modify: `plugins/xxthunder-dev-skills/.claude-plugin/plugin.json` (`version`)
- Modify: `.claude-plugin/marketplace.json` (matching `version`)
- Modify: `docs/backlog/xas-027b.md`, `docs/backlog/README.md`

**Interfaces:**
- Consumes: Tasks 4 and 5.
- Produces: plugin version `1.8.0`. XAS-027d and XAS-027e bump from here.

- [ ] **Step 1: Rehearse the architecture half against this repository**

Walk the "Editing architecture.md" flow for this repo without writing the file — XAS-027f owns actually creating it. Confirm the slots degrade honestly on a deliberately hard case:

- `Containers` → the two plugins, `xxthunder-dev-skills` and `xxthunder-paperless-skills`.
- `Components` → the skills inside each.
- `System context` → the Claude Code host, the marketplace, consuming repos.

If any slot can only be filled by inventing a box, the honest-degradation rule is not strong enough — fix `architecture-format.md` before committing.

- [ ] **Step 2: Bump both version fields**

`1.7.0` → `1.8.0` in `plugin.json` and `marketplace.json`. The `description` already lists `design-record` from Task 3 and does not change.

- [ ] **Step 3: Verify the two versions agree**

Run: `grep -h '"version"' plugins/xxthunder-dev-skills/.claude-plugin/plugin.json .claude-plugin/marketplace.json`

Expected: `1.8.0` in both for the dev-skills plugin.

- [ ] **Step 4: Run the existing test suite**

Run: `uv run --group dev pytest -q`

Expected: all existing tests pass.

- [ ] **Step 5: Tick criteria and close XAS-027b**

Via `backlog-ops`, as in Task 3 Step 6. No `README.md` change is needed here — 027b extends an existing skill rather than adding one, so its table row already exists.

- [ ] **Step 6: Commit**

```bash
git add plugins/xxthunder-dev-skills/skills/design-record/ \
        plugins/xxthunder-dev-skills/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json \
        docs/backlog/xas-027b.md docs/backlog/README.md
git commit -m "feat(design-record): add architecture.md slots and diagram editing (XAS-027b)

Completes the skill: architecture.md gains fixed slots for structure and
free-form Key flows for behaviour, so a structural update is an edit to a
known diagram rather than another diagram appended.

Slots degrade honestly — a slot with nothing to say carries an explicit
one-line note, never an empty heading and never a fabricated box. The
Decisions slot links the ADR index rather than duplicating it.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## What this plan does not cover

Each gets its own plan, written when it is next up:

- **XAS-027h** — ADR-log invariant tests. Real Python, runs against this repo's own `docs/adr/`, and the only automated coverage the epic gets. Sequenced right after this plan, because it verifies exactly what Tasks 1–3 produce.
- **XAS-027d** — `architecture-scan`, read-only bootstrap and drift report.
- **XAS-027c** — the `SessionStart` hook. The only substory with executable code and the only one with real CI risk. Note the amended scope: extensionless `hooks/session-start` plus a polyglot `run-hook.cmd`, tested via `subprocess` under a new `tests/dev/` tree.
- **XAS-027e** — wire-up into `refinement`, `tdd-workflow`, `commit-helper`.
- **XAS-027f** — dogfood: this repo's `architecture.md`, and reconciling hand-written ADRs `0001`–`0005` against what the skill now produces.
- **XAS-027g** — verify in `xxthunder/shortcuts`, retire the per-repo `AGENTS.md` paragraph, and settle the epic's open question about whether hook-injected text outranks a peer plugin's skill instruction.
