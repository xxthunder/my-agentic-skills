"""Tests for split-batch/scripts/detect_separators.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import detect_separators as ds

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "split-batch"
    / "scripts"
    / "detect_separators.py"
)


def pg(index: int, char_count: int) -> dict:
    return {"index": index, "char_count": char_count}


# ---------- detect_separators ----------


def test_splits_on_blank_between_two_docs():
    pages = [pg(0, 400), pg(1, 300), pg(2, 0), pg(3, 500)]
    result = ds.detect_separators(pages)
    assert result["blank_pages"] == [2]
    assert [d["pages"] for d in result["documents"]] == [[0, 1], [3]]
    assert result["overall_confidence"] == "high"


def test_consecutive_blanks_collapse():
    pages = [pg(0, 400), pg(1, 0), pg(2, 5), pg(3, 500)]
    result = ds.detect_separators(pages)
    assert result["blank_pages"] == [1, 2]
    assert [d["pages"] for d in result["documents"]] == [[0], [3]]


def test_leading_and_trailing_blanks_dropped():
    pages = [pg(0, 0), pg(1, 400), pg(2, 0)]
    result = ds.detect_separators(pages)
    assert result["blank_pages"] == [0, 2]
    assert [d["pages"] for d in result["documents"]] == [[1]]


def test_threshold_boundary():
    # char_count == threshold is NOT blank (strict less-than).
    pages = [pg(0, 50), pg(1, 49)]
    result = ds.detect_separators(pages, threshold=50)
    assert result["blank_pages"] == [1]
    assert [d["pages"] for d in result["documents"]] == [[0]]


def test_no_blanks_single_document():
    pages = [pg(0, 100), pg(1, 200)]
    result = ds.detect_separators(pages)
    assert result["blank_pages"] == []
    assert [d["pages"] for d in result["documents"]] == [[0, 1]]


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_cli_reads_file(tmp_path):
    path = tmp_path / "pages.json"
    path.write_text(
        json.dumps({"pages": [pg(0, 400), pg(1, 0), pg(2, 400)]}), encoding="utf-8"
    )
    result = _run([str(path)])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert [d["pages"] for d in data["documents"]] == [[0], [2]]


def test_cli_threshold_flag(tmp_path):
    path = tmp_path / "pages.json"
    path.write_text(
        json.dumps({"pages": [pg(0, 400), pg(1, 30), pg(2, 400)]}), encoding="utf-8"
    )
    result = _run([str(path), "--threshold", "10"])
    assert result.returncode == 0
    # With threshold 10, the 30-char page is NOT blank -> one document.
    data = json.loads(result.stdout)
    assert [d["pages"] for d in data["documents"]] == [[0, 1, 2]]


def test_cli_exits_1_on_missing_file(tmp_path):
    result = _run([str(tmp_path / "nope.json")])
    assert result.returncode == 1
    assert "not a file" in result.stderr


def test_cli_exits_1_on_bad_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{nope", encoding="utf-8")
    result = _run([str(bad)])
    assert result.returncode == 1
    assert "invalid pages JSON" in result.stderr
