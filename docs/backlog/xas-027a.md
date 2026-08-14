# [XAS-027a] ✅ DONE - `design-record` skill — ADR authoring, numbering, index

**Status**: Done (2026-08-14)
**Priority**: High
**Component**: `plugins/xxthunder-dev-skills/skills/design-record/SKILL.md` (new),
`plugins/xxthunder-dev-skills/skills/design-record/references/adr-format.md` (new),
`plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, `README.md`

**Summary**:
As a maintainer, I want a skill that turns a decision reached in conversation
into a correctly formatted ADR, so that the rationale is captured while it is
still in context rather than reconstructed later, when the alternatives that
lost are no longer recoverable.

**Description**:
The first half of `design-record`, and the first thing worth shipping: it is
useful on its own, before `architecture.md` support exists and before the hook
points at it.

The skill drafts the ADR body itself. This is a deliberate divergence from
`backlog-ops`, which refuses to author content — the reason is that most
decisions produce both an ADR and an architecture edit, and splitting authorship
across a conversation skill and a mechanics skill would make recording a
decision a two-invocation ritual for the most common case. The skill must state
this divergence and its reason in its own text; otherwise a future session will
notice the inconsistency with `backlog-ops` and "fix" it.

The guardrail that matters most: **never invent rationale**. If the conversation
does not contain why an alternative lost, the skill asks rather than filling the
section in. A fabricated "Alternatives considered" reads as history and is not,
which is worse than an absent one.

**Scope Decisions**:
- ADRs live at `docs/adr/NNNN-kebab-title.md`, four-digit, sequential, numbers
  never reused.
- Statuses: `Proposed` → `Accepted` | `Rejected`, and later
  `Superseded by ADR-NNNN`. Rejected ADRs stay in the log — "we considered this
  and said no" is as useful as a yes.
- An Accepted ADR is immutable. The only permitted edit is its `**Status**` line
  at supersede time; a changed mind is a new ADR.
- `docs/adr/README.md` is an **index derived from the files**. Where index and
  files disagree, the files win and the index is regenerated. This inverts the
  backlog rule, where `README.md` wins — deliberately, because the backlog README
  carries status that lives nowhere else, while the ADR index carries nothing the
  files do not already hold.
- The ADR links to the backlog item that produced it; the item is not required to
  link back. One direction is free, two directions cost an edit every time and
  rot silently.

**Acceptance Criteria**:
- [x] `SKILL.md` exists with a description that triggers on "record an ADR",
      "document this decision", "we decided X" and similar, and that does not
      overlap `refinement`'s or `backlog-ops`' trigger phrases.
- [x] `references/adr-format.md` documents the template, the status values, the
      numbering rule, immutability, the supersede path, and the
      index-is-derived rule.
- [x] The skill allocates the next number by scanning `docs/adr/NNNN-*.md`,
      taking the maximum and incrementing, zero-padded to four digits.
- [x] The skill drafts Context / Decision / Alternatives considered /
      Consequences from the conversation, and **asks** for anything it cannot
      source rather than inventing it.
- [x] The skill applies the three-part test — consequences outlive the change, a
      competent engineer could have chosen otherwise, the reason is not
      recoverable from the code — and when a request fails it, declines and
      points at the backlog item's `Scope Decisions` instead.
- [x] Supersede path works: the new ADR records `Supersedes ADR-NNNN`, the old
      one's `**Status**` line becomes `Superseded by ADR-NNNN`, and the old
      body is untouched.
- [x] The skill creates `docs/adr/README.md` and adds the index row; it
      regenerates the index from the files when the two disagree.
- [x] The skill bootstraps `docs/adr/` when the directory is absent.
- [x] The skill stages edits only and never commits, matching `backlog-ops`.
- [x] `SKILL.md` states explicitly why this skill authors prose while
      `backlog-ops` does not.
- [x] `plugin.json` and `marketplace.json` bumped (minor), and `plugin.json`'s
      `description` updated to list the new skill.
- [x] `README.md`'s `xxthunder-dev-skills` table gains a `design-record` row
      linking its `SKILL.md`. Every other skill in both plugins appears there;
      a new skill that does not is invisible to anyone browsing the repo.
- [x] All existing tests continue to pass.
