"""The `SessionStart` orientation hook, exercised as a subprocess.

The hook fires in every session of every consuming repo, so the properties that
matter most are negative ones: it must stay silent where these conventions are
not in use, and it must never fail. Every test here asserts `returncode == 0`,
including the malformed-input cases.

The script is invoked through `bash` rather than `sh`. It is written to POSIX
`sh` rules so either works, but `bash` is what `run-hook.cmd` actually calls on
both platforms, and it is the interpreter guaranteed to exist on the Windows
runner.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "xxthunder-dev-skills"
HOOK = PLUGIN_ROOT / "hooks" / "session-start"

pytestmark = pytest.mark.skipif(
    not HOOK.is_file(), reason="session-start hook not present"
)


def run_hook(project_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(HOOK)],
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
