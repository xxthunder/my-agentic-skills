"""Tests for split-batch/scripts/extract_pages.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import extract_pages

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "split-batch"
    / "scripts"
    / "extract_pages.py"
)


# ---------- helpers ----------


def _normalize_roundtrip(text: str) -> str:
    return extract_pages._normalize(text)


# ---------- pure functions ----------


def test_normalize_collapses_whitespace():
    assert _normalize_roundtrip("a\n  b\t c  ") == "a b c"


def test_nonws_count_ignores_whitespace():
    assert extract_pages._nonws_count("a b\nc\t") == 3
    assert extract_pages._nonws_count("   \n\t ") == 0


def test_extract_pages_schema(make_pdf):
    pdf = make_pdf("doc.pdf", ["Hello World", "second page text"])
    result = extract_pages.extract_pages(pdf)
    assert result["pdf"] == "doc.pdf"
    assert result["page_count"] == 2
    assert len(result["pages"]) == 2
    first = result["pages"][0]
    assert set(first) == {"index", "text", "top", "bottom", "char_count"}
    assert first["index"] == 0
    assert "Hello World" in first["text"]
    assert "Hello World" in first["top"]
    assert first["char_count"] > 0


def test_extract_pages_top_slice_bounded(make_pdf):
    pdf = make_pdf("long.pdf", ["x" * 500])
    result = extract_pages.extract_pages(pdf, top_chars=20, bottom_chars=30)
    assert len(result["pages"][0]["top"]) <= 20
    assert len(result["pages"][0]["bottom"]) <= 30


def test_extract_pages_blank_page_has_zero_char_count(make_pdf):
    pdf = make_pdf("blank.pdf", [""])
    result = extract_pages.extract_pages(pdf)
    assert result["pages"][0]["char_count"] == 0


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_cli_prints_json(make_pdf):
    pdf = make_pdf("one.pdf", ["Hello CLI"])
    result = _run([str(pdf)])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["page_count"] == 1
    assert "Hello CLI" in data["pages"][0]["text"]


def test_cli_out_writes_file(make_pdf, tmp_path):
    pdf = make_pdf("one.pdf", ["payload"])
    out = tmp_path / "pages.json"
    result = _run([str(pdf), "--out", str(out)])
    assert result.returncode == 0
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["page_count"] == 1


def test_cli_exits_1_when_pdf_missing(tmp_path):
    result = _run([str(tmp_path / "ghost.pdf")])
    assert result.returncode == 1
    assert "not a file" in result.stderr


def test_cli_exits_1_when_pdf_unreadable(tmp_path):
    bogus = tmp_path / "corrupt.pdf"
    bogus.write_text("not a real PDF", encoding="utf-8")
    result = _run([str(bogus)])
    assert result.returncode == 1
    assert "cannot open PDF" in result.stderr
