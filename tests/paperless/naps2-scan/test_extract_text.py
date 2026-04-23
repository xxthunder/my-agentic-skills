"""Tests for naps2-scan/scripts/extract_text.py."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import extract_text

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "naps2-scan"
    / "scripts"
    / "extract_text.py"
)


# ---------- extract_text ----------


def test_extract_text_returns_page_content(make_pdf):
    pdf = make_pdf("one.pdf", ["Hello World"])
    assert "Hello World" in extract_text.extract_text(pdf)


def test_extract_text_joins_pages_with_newlines(make_pdf):
    pdf = make_pdf("two.pdf", ["first-page-text", "second-page-text"])
    out = extract_text.extract_text(pdf)
    assert "first-page-text" in out
    assert "second-page-text" in out
    # Page separator is a newline between page texts.
    assert out.index("first-page-text") < out.index("second-page-text")


def test_extract_text_respects_max_pages(make_pdf):
    pdf = make_pdf("three.pdf", ["alpha", "beta", "gamma"])
    out = extract_text.extract_text(pdf, max_pages=2)
    assert "alpha" in out
    assert "beta" in out
    assert "gamma" not in out


def test_extract_text_max_pages_zero_returns_all(make_pdf):
    pdf = make_pdf("three.pdf", ["alpha", "beta", "gamma"])
    out = extract_text.extract_text(pdf, max_pages=0)
    assert "gamma" in out


def test_extract_text_raises_on_missing_file(tmp_path):
    with pytest.raises(Exception):
        extract_text.extract_text(tmp_path / "nope.pdf")


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_cli_prints_text(make_pdf):
    pdf = make_pdf("one.pdf", ["Hello CLI"])
    result = _run([str(pdf)])
    assert result.returncode == 0
    assert "Hello CLI" in result.stdout


def test_cli_pages_flag_limits_output(make_pdf):
    pdf = make_pdf("three.pdf", ["one", "two", "three"])
    result = _run([str(pdf), "--pages", "1"])
    assert result.returncode == 0
    assert "one" in result.stdout
    assert "three" not in result.stdout


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
