"""Tests for split-batch/scripts/split_pdf.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

import split_pdf

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "split-batch"
    / "scripts"
    / "split_pdf.py"
)


# ---------- parse_groups ----------


def test_parse_groups_ranges_and_singles():
    assert split_pdf.parse_groups("0-2;3-4;5,7") == [[0, 1, 2], [3, 4], [5, 7]]


def test_parse_groups_skips_empty_chunks():
    assert split_pdf.parse_groups("0-1;;2") == [[0, 1], [2]]


def test_parse_groups_rejects_reversed_range():
    with pytest.raises(ValueError):
        split_pdf.parse_groups("3-1")


# ---------- boundaries_to_groups ----------


def test_boundaries_to_groups_contiguous_full_coverage():
    assert split_pdf.boundaries_to_groups([0, 3, 5], 8) == [
        [0, 1, 2],
        [3, 4],
        [5, 6, 7],
    ]


def test_boundaries_must_start_at_zero():
    with pytest.raises(ValueError):
        split_pdf.boundaries_to_groups([1, 3], 5)


def test_boundaries_dedupe_and_sort():
    assert split_pdf.boundaries_to_groups([0, 0, 2], 4) == [[0, 1], [2, 3]]


# ---------- split_pdf ----------


def test_split_pdf_writes_zero_padded_outputs(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["p0", "p1", "p2", "p3"])
    written = split_pdf.split_pdf(pdf, [[0, 1], [2, 3]], tmp_path)
    assert [p.name for p in written] == ["part-01.pdf", "part-02.pdf"]
    assert all(p.is_file() for p in written)
    assert len(PdfReader(str(written[0])).pages) == 2


def test_split_pdf_keeps_source(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["a", "b"])
    split_pdf.split_pdf(pdf, [[0], [1]], tmp_path)
    assert pdf.is_file()
    assert len(PdfReader(str(pdf)).pages) == 2


def test_split_pdf_can_drop_pages(make_pdf, tmp_path):
    # Separator-style: page index 1 omitted entirely.
    pdf = make_pdf("batch.pdf", ["keep0", "DROP", "keep2"])
    written = split_pdf.split_pdf(pdf, [[0], [2]], tmp_path)
    assert len(written) == 2
    assert len(PdfReader(str(written[0])).pages) == 1
    assert len(PdfReader(str(written[1])).pages) == 1


def test_split_pdf_padding_widens_for_ten_plus(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", [str(i) for i in range(10)])
    groups = [[i] for i in range(10)]
    written = split_pdf.split_pdf(pdf, groups, tmp_path)
    assert written[0].name == "part-01.pdf"
    assert written[-1].name == "part-10.pdf"


def test_split_pdf_raises_on_out_of_range(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["a", "b"])
    with pytest.raises(ValueError):
        split_pdf.split_pdf(pdf, [[0], [5]], tmp_path)


def test_split_pdf_raises_on_empty_group(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["a", "b"])
    with pytest.raises(ValueError):
        split_pdf.split_pdf(pdf, [[0], []], tmp_path)


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_cli_groups(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["a", "b", "c"])
    result = _run([str(pdf), "--groups", "0-1;2", "--outdir", str(tmp_path)])
    assert result.returncode == 0
    assert (tmp_path / "part-01.pdf").is_file()
    assert (tmp_path / "part-02.pdf").is_file()


def test_cli_boundaries(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["a", "b", "c", "d"])
    result = _run([str(pdf), "--boundaries", "0,2", "--outdir", str(tmp_path)])
    assert result.returncode == 0
    assert len(PdfReader(str(tmp_path / "part-01.pdf")).pages) == 2


def test_cli_requires_a_selector(make_pdf):
    pdf = make_pdf("batch.pdf", ["a"])
    result = _run([str(pdf)])
    assert result.returncode != 0  # argparse error


def test_cli_rejects_both_selectors(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["a", "b"])
    result = _run([str(pdf), "--groups", "0;1", "--boundaries", "0,1"])
    assert result.returncode != 0


def test_cli_exits_1_on_missing_pdf(tmp_path):
    result = _run([str(tmp_path / "ghost.pdf"), "--boundaries", "0"])
    assert result.returncode == 1
    assert "not a file" in result.stderr


def test_cli_exits_1_on_out_of_range(make_pdf, tmp_path):
    pdf = make_pdf("batch.pdf", ["a", "b"])
    result = _run([str(pdf), "--groups", "0;9", "--outdir", str(tmp_path)])
    assert result.returncode == 1
    assert "split error" in result.stderr
