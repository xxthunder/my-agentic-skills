"""Tests for naps2-scan/scripts/write_config.py."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import write_config

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "naps2-scan"
    / "scripts"
    / "write_config.py"
)


# ---------- merge_config ----------


def test_merge_config_preserves_existing_keys():
    existing = {"exe_path": "X", "default_profile": "P"}
    assert write_config.merge_config(existing, {}) == existing


def test_merge_config_applies_only_non_none_updates():
    existing = {"default_profile": "OLD"}
    updates = {"exe_path": "NEW", "profile": None, "ocr_lang": "eng"}
    assert write_config.merge_config(existing, updates) == {
        "default_profile": "OLD",
        "exe_path": "NEW",
        "default_ocr_lang": "eng",
    }


def test_merge_config_overwrites_when_flag_supplied():
    existing = {"default_profile": "OLD"}
    updates = {"profile": "NEW"}
    assert write_config.merge_config(existing, updates) == {"default_profile": "NEW"}


def test_merge_config_ignores_unknown_flags():
    existing = {"exe_path": "X"}
    updates = {"exe_path": "Y", "bogus": "ignored"}
    merged = write_config.merge_config(existing, updates)
    assert merged == {"exe_path": "Y"}
    assert "bogus" not in merged


def test_merge_config_maps_scanner_type_to_default_scanner_type():
    assert write_config.merge_config({}, {"scanner_type": "duplex"}) == {
        "default_scanner_type": "duplex"
    }


def test_merge_config_does_not_mutate_input():
    existing = {"exe_path": "X"}
    write_config.merge_config(existing, {"exe_path": "Y"})
    assert existing == {"exe_path": "X"}


# ---------- atomic_write ----------


def test_atomic_write_creates_file(tmp_path):
    path = tmp_path / "config.json"
    write_config.atomic_write(path, {"a": 1})
    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1}


def test_atomic_write_overwrites_existing(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"old": true}', encoding="utf-8")
    write_config.atomic_write(path, {"new": True})
    assert json.loads(path.read_text(encoding="utf-8")) == {"new": True}


def test_atomic_write_cleans_up_tmp_on_success(tmp_path):
    path = tmp_path / "config.json"
    write_config.atomic_write(path, {"a": 1})
    assert not (tmp_path / "config.json.tmp").exists()


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _env_with_config_dir(tmp_path: Path) -> dict:
    env = os.environ.copy()
    if sys.platform == "win32":
        env["APPDATA"] = str(tmp_path)
    else:
        env["XDG_CONFIG_HOME"] = str(tmp_path)
    return env


def _config_file(tmp_path: Path) -> Path:
    return tmp_path / "naps2-scan" / "config.json"


def test_cli_writes_new_config(tmp_path):
    env = _env_with_config_dir(tmp_path)
    result = _run(["--profile", "MFC", "--ocr-lang", "eng"], env)
    assert result.returncode == 0
    assert json.loads(_config_file(tmp_path).read_text(encoding="utf-8")) == {
        "default_profile": "MFC",
        "default_ocr_lang": "eng",
    }


def test_cli_merges_into_existing(tmp_path):
    cfg = _config_file(tmp_path)
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text('{"exe_path": "X", "default_profile": "OLD"}', encoding="utf-8")
    result = _run(["--profile", "NEW"], _env_with_config_dir(tmp_path))
    assert result.returncode == 0
    assert json.loads(cfg.read_text(encoding="utf-8")) == {
        "exe_path": "X",
        "default_profile": "NEW",
    }


def test_cli_rejects_invalid_scanner_type(tmp_path):
    result = _run(
        ["--scanner-type", "triplex"], _env_with_config_dir(tmp_path)
    )
    assert result.returncode != 0
    assert "triplex" in result.stderr or "invalid" in result.stderr.lower()


def test_cli_accepts_simplex_and_duplex(tmp_path):
    for value in ("simplex", "duplex"):
        result = _run(["--scanner-type", value], _env_with_config_dir(tmp_path))
        assert result.returncode == 0
    # The last one wins.
    assert json.loads(_config_file(tmp_path).read_text(encoding="utf-8")) == {
        "default_scanner_type": "duplex"
    }
