"""Structural invariants of the backlog at `docs/backlog/`.

`README.md` is **authoritative** for status: `backlog-ops` states that where an
item file and the README disagree, the README wins. That makes disagreement
worse here than in the ADR log, where the files win and the index is a
regenerable cache. A stale TOC is not a cache miss, it is the wrong answer.

Checks are pure functions over a directory, so each runs against this
repository's real backlog (expected clean) and against a deliberately broken one
in `tmp_path` (expected to produce a finding). Without the second half, a check
that never fires looks identical to one that passes.

Structure only, never content.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKLOG = REPO_ROOT / "docs" / "backlog"

ITEM_RE = re.compile(r"^([a-z]+)-(\d{3})([a-z]?)\.md$")
HEADING_RE = re.compile(r"^#\s+\[([A-Z]+-\d{3}[a-z]?)\]\s*(.*)$", re.M)
STATUS_RE = re.compile(r"^\*\*Status\*\*:\s*(.+?)\s*$", re.M)
TOC_ROW_RE = re.compile(r"^- \[([A-Z]+-\d{3}[a-z]?) — .*?\]\(([a-z]+-\d{3}[a-z]?\.md)\)\s*$")
SECTION_RE = re.compile(r"^### (Open|In Progress|Done)\s*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

pytestmark = pytest.mark.skipif(
    not BACKLOG.is_dir(), reason="no docs/backlog/ in this repository"
)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def item_files(backlog: Path) -> list[Path]:
    return sorted(p for p in backlog.glob("*.md") if ITEM_RE.match(p.name))


def parse_item(p: Path) -> dict:
    t = read(p)
    h = HEADING_RE.search(t)
    s = STATUS_RE.search(t)
    status = s.group(1) if s else None
    return {
        "path": p,
        "name": p.name,
        "id": h.group(1) if h else None,
        "title": h.group(2) if h else "",
        "status": status,
        "section": "Done" if status and status.startswith("Done") else status,
    }


def parse_toc(backlog: Path) -> list[dict]:
    rows, section = [], None
    for line in read(backlog / "README.md").splitlines():
        m = SECTION_RE.match(line)
        if m:
            section = m.group(1)
            continue
        r = TOC_ROW_RE.match(line)
        if r and section:
            rows.append({"id": r.group(1), "target": r.group(2), "section": section})
    return rows


def check_toc_covers_every_item(backlog: Path) -> list[str]:
    listed = [r["target"] for r in parse_toc(backlog)]
    problems = []
    for p in item_files(backlog):
        n = listed.count(p.name)
        if n == 0:
            problems.append(f"{p.name}: not listed in the TOC")
        elif n > 1:
            problems.append(f"{p.name}: listed {n} times in the TOC")
    for r in parse_toc(backlog):
        if not (backlog / r["target"]).is_file():
            problems.append(f"TOC row {r['id']} points at missing file {r['target']}")
    return problems


def check_status_matches_section(backlog: Path) -> list[str]:
    by_target = {r["target"]: r for r in parse_toc(backlog)}
    problems = []
    for p in item_files(backlog):
        item = parse_item(p)
        row = by_target.get(p.name)
        if row is None or item["section"] is None:
            continue
        if item["section"] != row["section"]:
            problems.append(
                f"{p.name}: file says {item['status']!r}, TOC lists it under "
                f"{row['section']!r} (the README is authoritative)"
            )
    return problems


def check_heading_matches_filename(backlog: Path) -> list[str]:
    problems = []
    for p in item_files(backlog):
        item = parse_item(p)
        if item["id"] is None:
            problems.append(f"{p.name}: no '# [PREFIX-###] Title' heading")
        elif item["id"].lower() != p.stem:
            problems.append(f"{p.name}: heading says {item['id']}")
    return problems


def check_sections_are_id_sorted(backlog: Path) -> list[str]:
    rows, problems = parse_toc(backlog), []
    for section in ("Open", "In Progress", "Done"):
        ids = [r["id"] for r in rows if r["section"] == section]
        if ids != sorted(ids):
            for a, b in zip(ids, ids[1:]):
                if a > b:
                    problems.append(f"{section}: {b} listed after {a}")
    return problems


def check_done_markers_are_consistent(backlog: Path) -> list[str]:
    """Consistency, not conformance.

    Eight items — XAS-016 through XAS-024 — are Done with a bare `Done` status
    and no heading prefix. The backlog Notes document them as legacy bare-ID
    substories predating the convention, and inventing completion dates for
    them now would be fabrication. So this does not mandate the marker; it
    checks that the two halves agree wherever they appear, which is what
    actually goes wrong.
    """
    problems = []
    for p in item_files(backlog):
        item = parse_item(p)
        status, title = item["status"] or "", item["title"]
        is_done = status.startswith("Done")
        m = re.match(r"Done \((.+)\)$", status)
        if m:
            try:
                date.fromisoformat(m.group(1))
            except ValueError:
                problems.append(f"{p.name}: date {m.group(1)!r} does not parse")
        if "✅ DONE" in title and not is_done:
            problems.append(f"{p.name}: heading marked DONE but status is {status!r}")
    return problems


def check_epic_cascade(backlog: Path) -> list[str]:
    items = {parse_item(p)["id"]: parse_item(p) for p in item_files(backlog)}
    problems = []
    for iid, item in items.items():
        if iid is None or len(iid.split("-")[1]) != 3:
            continue
        subs = [o for k, o in items.items() if k and k[:-1] == iid and k != iid]
        if not subs:
            continue
        if (item["status"] or "").startswith("Done"):
            open_subs = [s["id"] for s in subs if not (s["status"] or "").startswith("Done")]
            if open_subs:
                problems.append(f"{iid} is Done while {', '.join(sorted(open_subs))} is not")
    return problems


def check_links_resolve(backlog: Path) -> list[str]:
    problems = []
    for p in item_files(backlog) + [backlog / "README.md"]:
        if not p.is_file():
            continue
        for raw in LINK_RE.findall(read(p)):
            t = raw.split("#", 1)[0].strip()
            if not t or "://" in t or t.startswith("mailto:"):
                continue
            if not (p.parent / t).exists():
                problems.append(f"{p.name}: link {t!r} resolves to nothing")
    return problems


ALL_CHECKS = (
    check_toc_covers_every_item,
    check_status_matches_section,
    check_heading_matches_filename,
    check_sections_are_id_sorted,
    check_done_markers_are_consistent,
    check_epic_cascade,
    check_links_resolve,
)


@pytest.mark.parametrize("check", ALL_CHECKS, ids=lambda c: c.__name__)
def test_real_backlog_satisfies(check):
    assert check(BACKLOG) == []


def test_real_backlog_is_not_empty():
    """Guard against every check above passing vacuously."""
    assert item_files(BACKLOG), "no items found; the checks would pass vacuously"


# --------------------------------------------------------------------------
# Negative cases — each check must actually bite
# --------------------------------------------------------------------------

ITEM = "# [{id}] {mark}{title}\n\n**Status**: {status}\n\nBody.\n"
README = "# Backlog\n\n## Table of Contents\n\n### Open\n{o}\n### In Progress\n{p}\n### Done\n{d}\n"


def build(tmp_path, items=None, rows=None):
    """Minimal valid-by-default backlog; callers break exactly one thing."""
    b = tmp_path / "backlog"
    b.mkdir(exist_ok=True)
    items = items or [("SC-001", "First", "Open")]
    sec = {"Open": [], "In Progress": [], "Done": []}
    for iid, title, status in items:
        mark = "✅ DONE - " if status.startswith("Done") else ""
        (b / f"{iid.lower()}.md").write_text(
            ITEM.format(id=iid, title=title, status=status, mark=mark), encoding="utf-8"
        )
        s = "Done" if status.startswith("Done") else status
        sec[s].append(f"- [{iid} — {title}]({iid.lower()}.md)")
    if rows is not None:
        sec = rows
    (b / "README.md").write_text(
        README.format(
            o="\n".join(sec["Open"]) + "\n" if sec["Open"] else "",
            p="\n".join(sec["In Progress"]) + "\n" if sec["In Progress"] else "",
            d="\n".join(sec["Done"]) + "\n" if sec["Done"] else "",
        ),
        encoding="utf-8",
    )
    return b


def test_baseline_fixture_is_clean(tmp_path):
    b = build(tmp_path)
    for check in ALL_CHECKS:
        assert check(b) == [], check.__name__


def test_item_missing_from_toc_is_caught(tmp_path):
    b = build(tmp_path, rows={"Open": [], "In Progress": [], "Done": []})
    assert any("not listed" in x for x in check_toc_covers_every_item(b))


def test_toc_row_pointing_nowhere_is_caught(tmp_path):
    b = build(tmp_path, rows={"Open": ["- [SC-009 — Ghost](sc-009.md)"], "In Progress": [], "Done": []})
    assert any("missing file" in x for x in check_toc_covers_every_item(b))


def test_status_section_mismatch_is_caught(tmp_path):
    """The defect this module was written for."""
    b = build(tmp_path)
    p = b / "sc-001.md"
    p.write_text(read(p).replace("**Status**: Open", "**Status**: In Progress"), encoding="utf-8")
    assert any("authoritative" in x for x in check_status_matches_section(b))


def test_heading_filename_mismatch_is_caught(tmp_path):
    b = build(tmp_path)
    p = b / "sc-001.md"
    p.write_text(read(p).replace("[SC-001]", "[SC-002]"), encoding="utf-8")
    assert any("heading says" in x for x in check_heading_matches_filename(b))


def test_out_of_order_section_is_caught(tmp_path):
    b = build(tmp_path, items=[("SC-001", "First", "Open"), ("SC-002", "Second", "Open")],
              rows={"Open": ["- [SC-002 — Second](sc-002.md)", "- [SC-001 — First](sc-001.md)"],
                    "In Progress": [], "Done": []})
    assert any("listed after" in x for x in check_sections_are_id_sorted(b))


def test_unparseable_done_date_is_caught(tmp_path):
    b = build(tmp_path, items=[("SC-001", "First", "Done (01-01-2026)")])
    assert any("does not parse" in x for x in check_done_markers_are_consistent(b))


def test_heading_marked_done_with_open_status_is_caught(tmp_path):
    b = build(tmp_path)
    p = b / "sc-001.md"
    p.write_text(read(p).replace("# [SC-001] ", "# [SC-001] ✅ DONE - "), encoding="utf-8")
    assert any("heading marked DONE" in x for x in check_done_markers_are_consistent(b))


def test_legacy_bare_done_status_is_tolerated(tmp_path):
    """XAS-016..024 shape: Done, no date, no prefix. Not a defect."""
    b = build(tmp_path, items=[("SC-001", "Legacy", "Done")])
    p = b / "sc-001.md"
    p.write_text(read(p).replace("✅ DONE - ", ""), encoding="utf-8")
    assert check_done_markers_are_consistent(b) == []


def test_epic_done_with_open_substory_is_caught(tmp_path):
    b = build(tmp_path, items=[("SC-001", "Epic", "Done (2026-01-01)"),
                               ("SC-001a", "Sub", "Open")])
    assert any("is Done while" in x for x in check_epic_cascade(b))


def test_epic_done_with_all_substories_done_passes(tmp_path):
    b = build(tmp_path, items=[("SC-001", "Epic", "Done (2026-01-01)"),
                               ("SC-001a", "Sub", "Done (2026-01-01)")])
    assert check_epic_cascade(b) == []


def test_broken_link_is_caught(tmp_path):
    b = build(tmp_path)
    p = b / "sc-001.md"
    p.write_text(read(p) + "\nSee [SC-999](sc-999.md).\n", encoding="utf-8")
    assert any("resolves to nothing" in x for x in check_links_resolve(b))
