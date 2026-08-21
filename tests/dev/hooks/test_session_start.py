"""The `SessionStart` orientation hook, exercised as a subprocess.

The hook fires in every session of every consuming repo, so the properties that
matter most are negative ones: it must stay silent where these conventions are
not in use, and it must never fail. Every test here asserts `returncode == 0`,
including the malformed-input cases.

The script is invoked through bash rather than `sh`. It is written to POSIX `sh`
rules so either works, but bash is what `run-hook.cmd` actually calls on both
platforms.

Which bash matters — see `resolve_bash`. A bare `bash` is *not* safe on the
Windows runner: PATH resolves it to the WSL launcher, not Git for Windows.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "xxthunder-dev-skills"
HOOK = PLUGIN_ROOT / "hooks" / "session-start"

# Deliberately no skip guard. The ADR-log tests skip when `docs/adr/` is absent
# because a consuming fork may legitimately not keep one — but the hook is part
# of this plugin, so its absence is a defect, never a valid state. Skipping here
# would let the whole suite pass green if the hook were deleted.


def resolve_bash() -> str:
    """Find a real bash, the way `run-hook.cmd` does.

    On the Windows runner a bare `bash` resolves through PATH to
    `C:\\Windows\\System32\\bash.exe` — the WSL launcher. With no distribution
    installed it prints a UTF-16 "no installed distributions" notice and exits
    1, so every test asserting `returncode == 0` fails for a reason that has
    nothing to do with the hook. Git for Windows is checked first, matching the
    wrapper's own search order.
    """
    for candidate in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ):
        if Path(candidate).is_file():
            return candidate
    return shutil.which("bash") or "bash"


BASH = resolve_bash()


def run_hook(project_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [BASH, str(HOOK)],
        cwd=str(project_dir),
        env={
            "PATH": __import__("os").environ.get("PATH", ""),
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT),
            "CLAUDE_PROJECT_DIR": str(project_dir),
        },
        capture_output=True,
        text=True,
        timeout=30,
    )


def payload_of(result: subprocess.CompletedProcess) -> str:
    """Return the injected context, or '' when the hook stayed silent."""
    if not result.stdout.strip():
        return ""
    doc = json.loads(result.stdout)
    return doc["hookSpecificOutput"]["additionalContext"]


BACKLOG_README = """# Backlog

## Table of Contents

### Open

---

## Notes

- **ID prefix**: `{prefix}` (a project)
- Keep items actionable.
"""


def make_backlog(root: Path, prefix: str = "XAS") -> None:
    d = root / "docs" / "backlog"
    d.mkdir(parents=True, exist_ok=True)
    (d / "README.md").write_text(BACKLOG_README.format(prefix=prefix), encoding="utf-8")


def make_adr(root: Path) -> None:
    d = root / "docs" / "adr"
    d.mkdir(parents=True, exist_ok=True)
    (d / "README.md").write_text("# ADRs\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Silence where the conventions are not in use
# --------------------------------------------------------------------------


def test_silent_in_unrelated_repo(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "README.md").write_text("unrelated project", encoding="utf-8")
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert payload_of(result) == ""


def test_silent_in_empty_directory(tmp_path):
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert payload_of(result) == ""


# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------


def test_backlog_present_yields_prefix_and_path(tmp_path):
    make_backlog(tmp_path)
    result = run_hook(tmp_path)
    assert result.returncode == 0
    payload = payload_of(result)
    assert "XAS" in payload
    assert "docs/backlog" in payload


def test_prefix_is_discovered_not_hardcoded(tmp_path):
    make_backlog(tmp_path, prefix="HSH")
    payload = payload_of(run_hook(tmp_path))
    assert "HSH" in payload
    assert "XAS" not in payload


def test_adr_log_mentioned_when_present(tmp_path):
    make_backlog(tmp_path)
    make_adr(tmp_path)
    payload = payload_of(run_hook(tmp_path))
    assert "docs/adr" in payload


def test_adr_log_not_mentioned_when_absent(tmp_path):
    """A repo with a backlog and no ADR log is not told about an ADR log."""
    make_backlog(tmp_path)
    payload = payload_of(run_hook(tmp_path))
    assert "docs/adr" not in payload


def test_architecture_doc_in_docs_is_found(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
    payload = payload_of(run_hook(tmp_path))
    assert "docs/architecture.md" in payload


def test_architecture_doc_at_root_is_found(tmp_path):
    """Root ARCHITECTURE.md is a convention in its own right."""
    (tmp_path / "ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")
    payload = payload_of(run_hook(tmp_path))
    assert "ARCHITECTURE.md" in payload


def test_adr_alone_is_enough_to_fire(tmp_path):
    make_adr(tmp_path)
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert "docs/adr" in payload_of(result)


# --------------------------------------------------------------------------
# Payload content
# --------------------------------------------------------------------------


def test_names_the_brainstorming_spec_step(tmp_path):
    """A general rule loses to a peer skill's explicit instruction."""
    make_backlog(tmp_path)
    payload = payload_of(run_hook(tmp_path))
    assert "superpowers:brainstorming" in payload
    assert "docs/superpowers/specs" in payload


def test_payload_frames_a_closed_item_as_history_not_deletion(tmp_path):
    """XAS-027j — "dies at Done" read as if the repo throws closed work away.

    Nothing is deleted; the file stays. What ends at Done is the item's
    authority about the present, because nothing keeps it current.
    """
    make_backlog(tmp_path)
    payload = payload_of(run_hook(tmp_path)).lower()
    assert "dies" not in payload
    assert "history" in payload
    assert "not kept current" in payload


def test_no_dangling_pointer_at_a_record_that_is_not_listed(tmp_path):
    """XAS-027j — "belongs in the record below" must not appear with no record.

    A repo adopting the backlog convention before it keeps an ADR log is the
    common first case, and the one most likely to be misled.
    """
    make_backlog(tmp_path)
    payload = payload_of(run_hook(tmp_path))
    assert "record below" not in payload
    assert "Decisions:" not in payload and "Architecture:" not in payload

    make_adr(tmp_path)
    payload = payload_of(run_hook(tmp_path))
    assert "record below" in payload, "with a record present, the pointer belongs"


def test_payload_carries_no_gating_language(tmp_path):
    """Orientation, not enforcement — ADR-0004."""
    make_backlog(tmp_path)
    make_adr(tmp_path)
    payload = payload_of(run_hook(tmp_path)).lower()
    for word in ("refuse", "must not proceed", "you may not", "blocked", "forbidden"):
        assert word not in payload, f"gating language present: {word!r}"


def test_output_is_valid_json_for_claude_code(tmp_path):
    make_backlog(tmp_path)
    result = run_hook(tmp_path)
    doc = json.loads(result.stdout)
    assert doc["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert isinstance(doc["hookSpecificOutput"]["additionalContext"], str)


# --------------------------------------------------------------------------
# Never fail
# --------------------------------------------------------------------------


def test_backlog_readme_without_notes_section_still_exits_zero(tmp_path):
    d = tmp_path / "docs" / "backlog"
    d.mkdir(parents=True)
    (d / "README.md").write_text("# Backlog\n\nNo notes here.\n", encoding="utf-8")
    result = run_hook(tmp_path)
    assert result.returncode == 0
    json.loads(result.stdout)  # still well-formed


def test_backlog_directory_without_readme_still_exits_zero(tmp_path):
    (tmp_path / "docs" / "backlog").mkdir(parents=True)
    result = run_hook(tmp_path)
    assert result.returncode == 0


def test_binary_garbage_in_readme_still_exits_zero(tmp_path):
    d = tmp_path / "docs" / "backlog"
    d.mkdir(parents=True)
    (d / "README.md").write_bytes(b"\x00\xff\xfe binary \x00 garbage\n")
    result = run_hook(tmp_path)
    assert result.returncode == 0


def test_quotes_and_backslashes_in_prefix_do_not_break_json(tmp_path):
    """Discovered values are interpolated into JSON; they must be escaped."""
    d = tmp_path / "docs" / "backlog"
    d.mkdir(parents=True)
    (d / "README.md").write_text(
        '# Backlog\n\n## Notes\n\n- **ID prefix**: `A"B\\C` (odd)\n', encoding="utf-8"
    )
    result = run_hook(tmp_path)
    assert result.returncode == 0
    json.loads(result.stdout)


def test_crlf_backlog_readme_is_tolerated(tmp_path):
    d = tmp_path / "docs" / "backlog"
    d.mkdir(parents=True)
    (d / "README.md").write_bytes(
        BACKLOG_README.format(prefix="XAS").replace("\n", "\r\n").encode("utf-8")
    )
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert "XAS" in payload_of(result)


# --------------------------------------------------------------------------
# Wiring
# --------------------------------------------------------------------------


def test_hooks_json_declares_sessionstart_with_matcher():
    hooks_json = PLUGIN_ROOT / "hooks" / "hooks.json"
    assert hooks_json.is_file(), "hooks/hooks.json missing"
    doc = json.loads(hooks_json.read_text(encoding="utf-8"))
    entries = doc["hooks"]["SessionStart"]
    assert entries, "no SessionStart entry"
    assert entries[0]["matcher"] == "startup|clear|compact"
    assert "run-hook.cmd" in entries[0]["hooks"][0]["command"]


def test_hook_script_is_extensionless_and_wrapper_exists():
    """Claude Code's Windows handling prepends bash to commands containing .sh."""
    assert HOOK.is_file() and HOOK.suffix == ""
    assert (PLUGIN_ROOT / "hooks" / "run-hook.cmd").is_file()


# --------------------------------------------------------------------------
# Nested layouts (XAS-027i)
#
# xxthunder/shortcuts keeps docs/architecture/{README.md,adr/}. The 1.11.0
# order looked only at docs/adr/ and docs/architecture.md, so it reported a
# real ADR log and a real architecture document as absent.
# --------------------------------------------------------------------------


def make_nested_adr(root: Path) -> None:
    d = root / "docs" / "architecture" / "adr"
    d.mkdir(parents=True, exist_ok=True)
    (d / "0001-something.md").write_text("# ADR-0001 — Something\n", encoding="utf-8")


def test_nested_adr_log_is_found(tmp_path):
    make_backlog(tmp_path)
    make_nested_adr(tmp_path)
    payload = payload_of(run_hook(tmp_path))
    assert "docs/architecture/adr" in payload


def test_nested_architecture_readme_is_found(tmp_path):
    make_backlog(tmp_path)
    d = tmp_path / "docs" / "architecture"
    d.mkdir(parents=True)
    (d / "README.md").write_text("# Architecture\n", encoding="utf-8")
    payload = payload_of(run_hook(tmp_path))
    assert "docs/architecture/README.md" in payload


def test_top_level_adr_dir_wins_over_nested(tmp_path):
    make_backlog(tmp_path)
    make_adr(tmp_path)
    make_nested_adr(tmp_path)
    payload = payload_of(run_hook(tmp_path))
    assert "docs/adr/" in payload
    assert "docs/architecture/adr" not in payload


def test_architecture_md_wins_over_nested_readme(tmp_path):
    make_backlog(tmp_path)
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "architecture.md").write_text("# A\n", encoding="utf-8")
    (tmp_path / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "architecture" / "README.md").write_text("# B\n", encoding="utf-8")
    payload = payload_of(run_hook(tmp_path))
    assert "docs/architecture.md" in payload
    assert "docs/architecture/README.md" not in payload


def test_guard_fires_when_only_artifact_is_nested(tmp_path):
    """No backlog, no top-level ADR log — the hook must still speak up."""
    make_nested_adr(tmp_path)
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert "docs/architecture/adr" in payload_of(result)
