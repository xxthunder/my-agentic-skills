"""Tests for naps2-scan/scripts/read_config.py.

Covers pure functions (load_config, exe_is_valid) plus subprocess-based
CLI contract checks (exit codes 0/1/2, stdout JSON schema) so the
documented contract stays pinned.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import read_config

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "naps2-scan"
    / "scripts"
    / "read_config.py"
)


# ---------- load_config ----------


def test_load_config_returns_dict(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"exe_path": "X", "default_profile": "P"}', encoding="utf-8")
    assert read_config.load_config(path) == {"exe_path": "X", "default_profile": "P"}


def test_load_config_returns_none_when_missing(tmp_path):
    assert read_config.load_config(tmp_path / "nope.json") is None


def test_load_config_returns_none_on_invalid_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("not-json", encoding="utf-8")
    assert read_config.load_config(path) is None


def test_load_config_returns_none_on_non_object_json(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('["array", "not", "object"]', encoding="utf-8")
    assert read_config.load_config(path) is None


# ---------- exe_is_valid ----------


def test_exe_is_valid_true_without_exe_path():
    assert read_config.exe_is_valid({}) is True


def test_exe_is_valid_true_with_empty_exe_path():
    assert read_config.exe_is_valid({"exe_path": ""}) is True


def test_exe_is_valid_true_when_file_exists(tmp_path):
    real = tmp_path / "NAPS2.Console.exe"
    real.write_text("x", encoding="utf-8")
    assert read_config.exe_is_valid({"exe_path": str(real)}) is True


def test_exe_is_valid_false_when_file_missing(tmp_path):
    assert read_config.exe_is_valid({"exe_path": str(tmp_path / "nope.exe")}) is False


# ---------- config_path ----------


def test_config_path_uses_appdata_on_windows(monkeypatch):
    appdata = r"C:\Users\test\AppData\Roaming"
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", appdata)
    assert read_config.config_path() == Path(appdata) / "naps2-scan" / "config.json"


def test_config_path_uses_xdg_on_linux(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert read_config.config_path() == tmp_path / "naps2-scan" / "config.json"


def test_config_path_falls_back_to_home_dot_config(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    expected = Path.home() / ".config" / "naps2-scan" / "config.json"
    assert read_config.config_path() == expected


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
    )


def _env_with_config_dir(tmp_path: Path) -> dict:
    """Build an env where config_path() resolves under tmp_path on any OS."""
    env = os.environ.copy()
    if sys.platform == "win32":
        env["APPDATA"] = str(tmp_path)
    else:
        env["XDG_CONFIG_HOME"] = str(tmp_path)
    return env


def _write_config(tmp_path: Path, data: dict) -> Path:
    cfg_dir = tmp_path / "naps2-scan"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg = cfg_dir / "config.json"
    cfg.write_text(json.dumps(data), encoding="utf-8")
    return cfg


def test_cli_exits_1_when_config_missing(tmp_path):
    result = _run([], _env_with_config_dir(tmp_path))
    assert result.returncode == 1
    assert result.stdout == ""


def test_cli_prints_json_and_exits_0(tmp_path):
    _write_config(tmp_path, {"default_profile": "MFC"})
    result = _run([], _env_with_config_dir(tmp_path))
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"default_profile": "MFC"}


def test_cli_validate_exe_ok(tmp_path):
    exe = tmp_path / "fake.exe"
    exe.write_text("x", encoding="utf-8")
    _write_config(tmp_path, {"exe_path": str(exe)})
    result = _run(["--validate-exe"], _env_with_config_dir(tmp_path))
    assert result.returncode == 0


def test_cli_validate_exe_stale_returns_2(tmp_path):
    _write_config(tmp_path, {"exe_path": str(tmp_path / "ghost.exe")})
    result = _run(["--validate-exe"], _env_with_config_dir(tmp_path))
    assert result.returncode == 2
    assert json.loads(result.stdout) == {"exe_path": str(tmp_path / "ghost.exe")}
