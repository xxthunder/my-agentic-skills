# `architecture.md` Format

One document, read top to bottom, describing how the product is put together.
It has the same lifetime as the product — unlike a backlog item, which dies at
Done.

## Where the document lives

Discovered, not hardcoded. In order:

1. `docs/architecture.md` — use it if it exists.
2. Root `ARCHITECTURE.md` — use it if it exists. This is a widely used
   convention in its own right, and a consuming repo may already have one.
3. `docs/architecture/README.md` — use it if it exists. A repo keeping
   `docs/architecture/` as a *directory* uses its README as the entry point,
   the same way `docs/adr/README.md` indexes an ADR log.
4. None exists → create `docs/architecture.md`.
5. More than one exists → **ask**. Do not guess, and do not merge them
   unprompted.

The ADR log is discovered the same way: `docs/adr/`, then
`docs/architecture/adr/`.

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

When the document is absent, create it with every slot present, each either
populated or carrying an honest one-line note:

    # Architecture

    ## Purpose

    ## System context

    ## Containers

    ## Components

    ## Key flows

    ## Glossary

    ## Decisions

    Recorded as ADRs — see [docs/adr/README.md](adr/README.md).
