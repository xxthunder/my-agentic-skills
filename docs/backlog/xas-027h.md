# [XAS-027h] ADR-log invariant tests

**Status**: Open
**Priority**: Medium
**Component**: `tests/dev/adr/test_adr_log.py` (new),
`tests/dev/adr/conftest.py` (new, if fixtures are needed)

**Depends on**: [XAS-027a](xas-027a.md) — the invariants being tested are the
ones `adr-format.md` defines.

**Summary**:
As a maintainer, I want the ADR log's structural invariants checked by CI, so
that a log whose index has silently drifted from its files fails a build rather
than misleading the next reader.

**Description**:
This epic ships almost no automated tests, because five of its seven substories
are markdown and markdown cannot be unit tested. That is mostly unavoidable —
but not entirely.

The ADR log is a directory of files with genuinely checkable structure, and one
of its rules makes checking it necessary rather than merely nice. The index at
`docs/adr/README.md` is **derived**: where index and files disagree, the files
win. A derived artifact with no verification is an artifact that drifts, and
nothing currently notices. [XAS-027d](xas-027d.md)'s `architecture-scan` checks
code against `architecture.md` and explicitly does not check this.

The tests run against this repository's own `docs/adr/`. That makes them a
dogfood check as much as a unit test — they fail if the log this repo keeps
stops obeying the format the plugin ships.

**Scope Decisions**:
- **Tests target this repo's `docs/adr/`, not a fixture directory.** A fixture
  would verify that the test's own fake log is well-formed, which proves
  nothing. The point is to check the real log. Where a rule needs a negative
  case (a malformed log must fail), build that case in `tmp_path`.
- **Structure only, never content.** The tests check numbering, links, sections
  and status values. Whether an ADR's reasoning is any good is a review
  question and stays one.
- **Skip cleanly when `docs/adr/` is absent.** These tests ship in a repo whose
  own layout they assert; a consuming fork without an ADR log should see skips,
  not failures.
- Lives under `tests/dev/`, the tree [XAS-027c](xas-027c.md) introduces.
  Everything under `tests/` today belongs to `xxthunder-paperless-skills` and
  imports helper scripts via `conftest.py`; this suite reads markdown and needs
  no such path injection.

**Acceptance Criteria**:
- [ ] Numbering: every file matches `NNNN-kebab-title.md`, four digits and
      zero-padded; no number appears twice.
- [ ] Index agreement: every ADR file has exactly one row in
      `docs/adr/README.md`, and every row points at a file that exists. Row
      title, status and date match the file's header block.
- [ ] Header block: every ADR carries `**Status**:` and `**Date**:` lines, and
      the date parses as `YYYY-MM-DD`.
- [ ] Status values are one of `Proposed`, `Accepted`, `Rejected`, or
      `Superseded by ADR-NNNN`.
- [ ] Required sections present in every ADR: `## Context`, `## Decision`,
      `## Alternatives considered`, `## Consequences`.
- [ ] Supersede pairs are symmetric: if A says `Supersedes ADR-B`, then B's
      status is `Superseded by ADR-A`, and vice versa. Neither half may dangle.
- [ ] Relative links inside ADRs and the index resolve to files that exist —
      this catches a renamed backlog item breaking a `**Related**` link.
- [ ] A malformed log built in `tmp_path` fails each check that is supposed to
      catch it; the negative cases are not assumed.
- [ ] The suite skips rather than fails when `docs/adr/` does not exist.
- [ ] Tests pass on both ubuntu and windows in CI. Watch for the path-separator
      and line-ending issues that already required a portability fix in the
      `naps2-scan` config test.
- [ ] No plugin version bump — this substory touches only `tests/`, not
      `plugins/`.

**Out of scope**:
- Validating `architecture.md`'s slots. Its structure is looser by design
  (free-form `Key flows`, honest-degradation notes), so the same approach would
  produce false failures. Revisit only if the slot rules prove strict enough to
  check.
- Judging whether an ADR is still honoured by the code. That is
  [XAS-027d](xas-027d.md)'s drift report, and it is deliberately limited there
  to ADRs whose referenced paths have disappeared.
