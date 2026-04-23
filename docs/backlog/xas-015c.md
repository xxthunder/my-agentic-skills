# [XAS-015c] ✅ DONE - Unit test harness + backfill for plugin Python scripts

**Status**: Done (2026-04-23)
**Priority**: Medium
**Component**: plugins/xxthunder-paperless-skills/tests/, plugins/xxthunder-paperless-skills/skills/naps2-scan/scripts/, plugins/xxthunder-paperless-skills/skills/simplex-merge/scripts/

**Summary**:
As a skill maintainer, I want all plugin Python helper scripts covered by automated unit tests so that refactors and future script additions cannot silently break the scan pipeline, and so the "every new script ships with tests" rule has a working example to follow.

**Description**:
The paperless plugin currently ships four Python helper scripts — `naps2-scan/scripts/read_config.py`, `write_config.py`, `extract_text.py`, and `simplex-merge/scripts/simplex_merge.py` — all written as PEP 723 inline-metadata scripts and run via `uv run`. None have automated test coverage; bugs regress silently.

This item (a) sets up a pytest + uv test harness under the plugin, (b) backfills tests for the four existing scripts to pin their current documented behavior (exit codes, JSON contracts, CLI flag semantics), and (c) documents how to run the tests locally. It does **not** add CI enforcement — that would be a separate item.

**Scope Decisions**:
- **Test location**: `plugins/xxthunder-paperless-skills/tests/<skill>/test_*.py` — co-located with the plugin but separate from the `skills/` tree. Tests live in the repo; they do not ship to end users on plugin install (skills stay portable).
- **Test runner**: `uv run --with pytest pytest` (PEP 723 inline pattern) or a tiny per-plugin `pyproject.toml` — pick whichever keeps scripts invokable unchanged via `uv run <script>`. Decide during implementation.
- **Coverage target**: behavior coverage of documented contracts — exit codes, JSON schema on stdout, flag semantics, error paths. Not 100% line coverage.
- **CI**: out of scope. Local `pytest` invocation only. A later item can wire a GitHub Actions job.
- **Script refactoring**: minimal. If a script is not unit-testable as written (e.g., all logic inside `if __name__ == "__main__"`), extract pure functions to module scope and keep the `__main__` block as a thin CLI wrapper.

**Dependencies**:
- `uv` on PATH (already required by all plugin scripts)

**Open questions**:
- Single `pyproject.toml` at the plugin root driving both runtime deps and test deps, or per-script PEP 723 with a separate tiny test harness config? Pick the one that keeps `uv run <script>` unchanged for end users.
- Subprocess-based tests (invoke the script as-is and assert on stdout/exit) vs. function-import tests (extract pure functions, import into test). Leaning import-based for fast feedback, plus a few subprocess tests per script for end-to-end contract verification.

**Acceptance Criteria**:
- [x] `pytest` harness set up at repo root (`pyproject.toml` + `tests/`) with a documented local-run command
- [x] `naps2-scan/scripts/read_config.py` — tests cover: valid config, missing file (exit 1), unreadable, `--validate-exe` pass/fail (exit 0/2)
- [x] `naps2-scan/scripts/write_config.py` — tests cover: merge-and-preserve behavior, partial-flag inputs, invalid `--scanner-type` rejected, atomic write
- [x] `naps2-scan/scripts/extract_text.py` — tests cover: happy path with a small fixture PDF, `--pages` limit, empty/unreadable PDF error path
- [x] `simplex-merge/scripts/merge.py` — tests cover: interleave correctness with fixture PDFs, odd/even page-count handling, CLI error paths
- [x] Repo `README.md` notes how to run tests
- [x] All existing scripts continue to behave identically (tests pin current behavior; only refactor was extracting pure functions from `main()`)
- [x] Plugin version bumped in `plugin.json` and `marketplace.json` (patch — no behavior change, only tests added)

**User Acceptance Test**:

1. **Local test run**
   - `cd plugins/xxthunder-paperless-skills && uv run --with pytest pytest` (or documented equivalent) exits 0 with all tests passing.
2. **Coverage sanity**
   - Each of the four scripts has at least one test per exit code it documents.
3. **Regression guard**
   - Introduce a deliberate bug in one script (e.g., flip an exit code in `read_config.py`); at least one test fails with a clear message. Revert.
