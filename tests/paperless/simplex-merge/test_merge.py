"""Tests for simplex-merge/scripts/merge.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

import merge

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "simplex-merge"
    / "scripts"
    / "merge.py"
)


# ---------- interleave ----------


def test_interleave_equal_counts():
    assert merge.interleave(["o1", "o2", "o3"], ["e1", "e2", "e3"]) == [
        "o1",
        "e1",
        "o2",
        "e2",
        "o3",
        "e3",
    ]


def test_interleave_more_odd_than_even():
    # Scanning stack had a blank last back; even is shorter.
    assert merge.interleave(["o1", "o2", "o3"], ["e1", "e2"]) == [
        "o1",
        "e1",
        "o2",
        "e2",
        "o3",
    ]


def test_interleave_more_even_than_odd():
    # Unusual but possible — trailing evens appended at end.
    assert merge.interleave(["o1", "o2"], ["e1", "e2", "e3"]) == [
        "o1",
        "e1",
        "o2",
        "e2",
        "e3",
    ]


def test_interleave_empty_inputs():
    assert merge.interleave([], []) == []
    assert merge.interleave(["o1"], []) == ["o1"]
    assert merge.interleave([], ["e1"]) == ["e1"]


# ---------- end-to-end merge (imported main) ----------


def _extract_page_text(pdf: Path) -> list[str]:
    return [(p.extract_text() or "").strip() for p in PdfReader(str(pdf)).pages]


def test_merge_produces_correct_page_order(make_pdf, tmp_path, monkeypatch):
    # Four-side document: fronts 1/3/5/7, backs 2/4/6/8.
    # Simplex scanner: fronts captured in order, backs captured with the
    # stack flipped so the last back is scanned first -> [8, 6, 4, 2].
    odd = make_pdf("odd.pdf", ["front-1", "front-3", "front-5", "front-7"])
    even = make_pdf("even.pdf", ["back-8", "back-6", "back-4", "back-2"])
    output = tmp_path / "out.pdf"

    monkeypatch.setattr(
        sys, "argv", ["merge.py", str(odd), str(even), str(output)]
    )
    assert merge.main() == 0
    assert _extract_page_text(output) == [
        "front-1",
        "back-2",
        "front-3",
        "back-4",
        "front-5",
        "back-6",
        "front-7",
        "back-8",
    ]


def test_merge_returns_1_when_odd_missing(tmp_path, make_pdf, monkeypatch):
    even = make_pdf("even.pdf", ["x"])
    output = tmp_path / "out.pdf"
    monkeypatch.setattr(
        sys, "argv", ["merge.py", str(tmp_path / "ghost.pdf"), str(even), str(output)]
    )
    assert merge.main() == 1


def test_merge_returns_1_when_even_missing(tmp_path, make_pdf, monkeypatch):
    odd = make_pdf("odd.pdf", ["x"])
    output = tmp_path / "out.pdf"
    monkeypatch.setattr(
        sys, "argv", ["merge.py", str(odd), str(tmp_path / "ghost.pdf"), str(output)]
    )
    assert merge.main() == 1


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_cli_merges_end_to_end(make_pdf, tmp_path):
    odd = make_pdf("odd.pdf", ["A", "C"])
    even = make_pdf("even.pdf", ["D", "B"])
    output = tmp_path / "out.pdf"
    result = _run([str(odd), str(even), str(output)])
    assert result.returncode == 0
    assert output.is_file()
    assert _extract_page_text(output) == ["A", "B", "C", "D"]


def test_cli_reports_missing_inputs(tmp_path):
    result = _run(
        [
            str(tmp_path / "ghost-odd.pdf"),
            str(tmp_path / "ghost-even.pdf"),
            str(tmp_path / "out.pdf"),
        ]
    )
    assert result.returncode == 1
    assert "not a file" in result.stderr
