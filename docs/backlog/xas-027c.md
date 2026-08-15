# [XAS-027c] ✅ DONE - `SessionStart` orientation hook

**Status**: Done (2026-08-15)
**Priority**: High
**Component**: `plugins/xxthunder-dev-skills/hooks/hooks.json` (new),
`plugins/xxthunder-dev-skills/hooks/session-start` (new, extensionless),
`plugins/xxthunder-dev-skills/hooks/run-hook.cmd` (new),
`tests/dev/hooks/` (new test module), `CLAUDE.md`, `CONTRIBUTING.md`,
`plugins/xxthunder-dev-skills/.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`

**Depends on**: [XAS-027a](xas-027a.md), [XAS-027b](xas-027b.md) — the payload
should name skills that exist rather than advertise vapour.

**Summary**:
As a maintainer, I want every session in a repo that uses these conventions to
start already knowing where the design record lives, so that the knowledge
arrives without anyone invoking anything and without a paragraph pasted into
each repo's `AGENTS.md`.

**Description**:
Skills are pull-based: a skill only shapes behaviour once something invokes it,
and nothing would invoke a "the record lives here" skill at the moment
`superpowers:brainstorming` decides where to write. `AGENTS.md` works because it
is push-based — always in context — but it is per-repo, drifts as the wording
evolves, and only protects repos someone remembered to edit.

The mechanism that generalises is the one `superpowers` uses for its own
always-on rule: a plugin `SessionStart` hook. `superpowers` ships
`hooks/hooks.json` with a `startup|clear|compact` matcher that injects
`using-superpowers` into every session. This plugin ships the same thing.

The payload is **orientation, not enforcement**: it states what record exists in
this repo and who writes it. It does not gate work.
See [ADR-0004](../adr/0004-always-on-rule-is-orientation-not-enforcement.md).

The one place it is directive is the conflict with `brainstorming`'s
spec-writing step, and there it must **name that step explicitly**. "If
`superpowers:brainstorming` reaches its spec-writing step, the design goes to the
backlog item" is operative; "designs live in the backlog" is a suggestion a peer
skill's explicit instruction will win against.

**Scope Decisions**:
- Guarded on repo shape: silent unless `docs/backlog/`, `docs/adr/`, or
  `docs/architecture.md` exists. Repos that do not use these conventions get
  nothing rather than a nag about a backlog that does not exist.
- Payload lists only artifacts that are actually present, with their discovered
  paths. A repo with a backlog and no ADR log is not told about an ADR log.
- POSIX `sh`, **no external dependencies**, always exits 0. This fires on every
  session in every consuming repo; a hook that errors because a tool is missing
  is worse than no hook. Notably not `uv`, despite it being this repo's standard
  for helper scripts.
- **The hook script is extensionless and reached through a polyglot
  `run-hook.cmd` wrapper**, following the `superpowers` precedent rather than the
  plain `session-start.sh` this story originally specified. Two reasons, both
  from `superpowers` 6.2.0's own `hooks/`: Claude Code's Windows handling
  prepends `bash` to any command containing `.sh`, which breaks the invocation;
  and on Windows the wrapper must locate a Git-for-Windows `bash` itself and
  exit 0 silently when there is none. A plain `.sh` cannot satisfy this story's
  own windows-latest acceptance criterion.
- **`hooks/hooks.json` is auto-discovered; `plugin.json` needs no `hooks`
  field.** Confirmed by inspection of `superpowers` 6.2.0, whose `plugin.json`
  declares no such key while its `SessionStart` hook fires. This turns the
  open confirmation below into a check rather than an experiment.
- Tests live under `tests/dev/`, a tree that does not exist yet — everything
  under `tests/` today belongs to `xxthunder-paperless-skills`. The hook is
  exercised as a subprocess, so it needs no `conftest.py` path injection and
  should not be modelled on the paperless script-import harness.
- The payload stays short — it is injected into every session — and points at
  the skills for mechanics rather than restating any format.
- The ID prefix is read from the backlog README's Notes section, not configured.

**Acceptance Criteria**:
- [x] `plugins/xxthunder-dev-skills/hooks/hooks.json` exists with a
      `SessionStart` hook using matcher `startup|clear|compact`.
- [x] The hook script is POSIX `sh`, has no external dependencies, and exits 0
      on every path including malformed input.
- [x] The script is extensionless and invoked via a polyglot `run-hook.cmd`
      wrapper that finds `bash` on Windows and exits 0 silently when it cannot.
- [x] The hook is a no-op in a repo with none of `docs/backlog/`, `docs/adr/`,
      `docs/architecture.md` (verified in a scratch repo).
- [x] The payload lists only the artifacts that exist, with discovered paths,
      and the ID prefix read from the backlog README Notes section.
- [x] The payload names `superpowers:brainstorming`'s spec-writing step
      explicitly and states where that output goes instead.
- [x] The payload contains no refusal or gating language.
- [x] pytest coverage via `subprocess`: no backlog → silent, exit 0; backlog
      present → payload carries prefix and paths; malformed backlog README →
      still exit 0.
- [x] `CLAUDE.md`'s version-bump rule widened from
      `plugins/<plugin-name>/skills/` to the whole plugin directory — a hook
      lives under `hooks/` and today's wording would not require a bump for it.
- [x] `CONTRIBUTING.md`'s acceptance bar (point 6) widened identically. It
      carries the same narrow `plugins/<plugin-name>/skills/` wording, so
      fixing only `CLAUDE.md` leaves the two documents contradicting each
      other on the one rule this repo states twice.
- [x] Confirmed whether `plugin.json` needs a `hooks` field or whether
      `hooks/hooks.json` is auto-discovered; manifest updated if required.
      **Answer: auto-discovered.** `superpowers` 6.3.0 declares no `hooks` key
      and its `SessionStart` hook fires, so no manifest change was needed.
- [x] `plugin.json` and `marketplace.json` bumped (minor).
- [x] Tests pass on both ubuntu and windows in CI.
