"""Tests for split-batch/scripts/detect_boundaries.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import detect_boundaries as db

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "xxthunder-paperless-skills"
    / "skills"
    / "split-batch"
    / "scripts"
    / "detect_boundaries.py"
)


def pg(index: int, top: str = "", bottom: str = "") -> dict:
    return {"index": index, "text": top, "top": top, "bottom": bottom, "char_count": len(top)}


# ---------- page_number ----------


def test_page_number_english():
    assert db.page_number("Invoice page 1 of 3", "") == (1, 3)


def test_page_number_german():
    assert db.page_number("Rechnung Seite 2 von 4", "") == (2, 4)


def test_page_number_slash_form_in_footer():
    assert db.page_number("", "footer 1 / 5") == (1, 5)


def test_page_number_rejects_current_gt_total():
    assert db.page_number("9 / 3", "") is None


def test_page_number_none_when_absent():
    assert db.page_number("just a letter", "") is None


# ---------- jaccard / tokenize / address ----------


def test_jaccard_identical_tokens_is_one():
    assert db.jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_jaccard_disjoint_is_zero():
    assert db.jaccard({"a"}, {"b"}) == 0.0


def test_jaccard_two_empty_sets_is_one():
    assert db.jaccard(set(), set()) == 1.0


def test_tokenize_drops_digits_and_punct():
    assert db.tokenize("Hello, World 2026!") == {"hello", "world"}


def test_address_block_de_plz():
    assert db.has_address_block("Musterstr. 1 12345 Berlin")


def test_address_block_us():
    assert db.has_address_block("Springfield CA 90210")


def test_address_block_absent():
    assert not db.has_address_block("Dear customer, thank you")


# ---------- detect_boundaries ----------


def test_single_page_is_high_single_doc():
    result = db.detect_boundaries([pg(0, "a letter")])
    assert result["boundaries"] == [0]
    assert result["overall_confidence"] == "high"


def test_page_number_reset_splits_high():
    pages = [
        pg(0, "Acme Seite 1 von 2"),
        pg(1, "Acme Seite 2 von 2"),
        pg(2, "Globex Seite 1 von 2"),
        pg(3, "Globex Seite 2 von 2"),
    ]
    result = db.detect_boundaries(pages)
    assert result["boundaries"] == [0, 2]
    assert result["overall_confidence"] == "high"
    assert "page-number-reset" in result["documents"][1]["signals"]


def test_consistent_page_numbers_no_reset_is_high_single_doc():
    pages = [
        pg(0, "Acme Report Seite 1 von 3 quarterly figures"),
        pg(1, "Acme Report Seite 2 von 3 quarterly figures"),
        pg(2, "Acme Report Seite 3 von 3 quarterly figures"),
    ]
    result = db.detect_boundaries(pages)
    assert result["boundaries"] == [0]
    assert result["overall_confidence"] == "high"


def test_letterhead_plus_address_is_medium_boundary():
    pages = [
        pg(0, "Acme Corporation invoice total due now please"),
        pg(1, "Globex Limited notice 12345 Berlin different words entirely"),
    ]
    result = db.detect_boundaries(pages)
    assert result["boundaries"] == [0, 1]
    assert result["documents"][1]["confidence"] == "medium"
    assert result["overall_confidence"] == "medium"


def test_letterhead_only_is_low_weak_signal():
    pages = [
        pg(0, "alpha beta gamma delta epsilon"),
        pg(1, "completely different words here now today"),
    ]
    result = db.detect_boundaries(pages)
    # Weak: not auto-split, recorded for user confirmation.
    assert result["boundaries"] == [0]
    assert result["weak_signals"][0]["confidence"] == "low"
    assert result["overall_confidence"] == "low"


def test_continuation_marker_with_letterhead_is_ambiguous():
    pages = [
        pg(0, "Acme contract clause one two three four five"),
        pg(1, "Totally unrelated header Seite 2 von 9 nothing matches"),
    ]
    result = db.detect_boundaries(pages)
    assert result["overall_confidence"] == "ambiguous"
    assert result["weak_signals"][0]["confidence"] == "ambiguous"


# ---------- CLI contract (subprocess) ----------


def _run(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        input=stdin,
    )


def _pages_json(tmp_path: Path, pages: list[dict]) -> Path:
    path = tmp_path / "pages.json"
    path.write_text(json.dumps({"pages": pages}), encoding="utf-8")
    return path


def test_cli_reads_file_and_prints_json(tmp_path):
    pages = [pg(0, "Acme Seite 1 von 1"), pg(1, "Globex Seite 1 von 2")]
    path = _pages_json(tmp_path, pages)
    result = _run([str(path)])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["boundaries"] == [0, 1]


def test_cli_reads_stdin():
    payload = json.dumps({"pages": [pg(0, "x letter content")]})
    result = _run(["-"], stdin=payload)
    assert result.returncode == 0
    assert json.loads(result.stdout)["boundaries"] == [0]


def test_cli_exits_1_on_missing_file(tmp_path):
    result = _run([str(tmp_path / "nope.json")])
    assert result.returncode == 1
    assert "not a file" in result.stderr


def test_cli_exits_1_on_bad_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = _run([str(bad)])
    assert result.returncode == 1
    assert "invalid pages JSON" in result.stderr
