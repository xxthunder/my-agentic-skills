# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Rule-based document-boundary detection over an extract_pages.py JSON file.

Reads the JSON produced by ``extract_pages.py`` (a path argument, or ``-`` for
stdin) and proposes document boundaries using three offline heuristics:

  * **page-number reset** (strongest): a "page 1 of N" / "1/N" / "Seite 1 von N"
    marker on a page that is not the first page signals a new document.
  * **letterhead change**: token-set Jaccard similarity of consecutive pages'
    normalized top blocks below a threshold signals a new sender/letterhead.
  * **address block**: a postal address (DE PLZ + city, or US state + ZIP) near
    the top of a page that the previous page lacked.

Confident boundaries (page-number resets, and letterhead+address agreement) are
emitted in ``boundaries``. Weaker or conflicting evidence is recorded in
``weak_signals`` for the skill to escalate (LLM) or confirm (user) — it is not
auto-split. ``overall_confidence`` drives that decision:

    high       -> accept the split without escalation
    medium     -> escalate to the LLM (consent-gated)
    ambiguous  -> escalate to the LLM (conflicting signals)
    low        -> ask the user directly (likely a single document)

Output schema (stdout):

    {
      "page_count": 11,
      "boundaries": [0, 3, 5],
      "documents": [{"start": 0, "end": 2, "pages": [0,1,2],
                     "confidence": "high", "signals": [...]}, ...],
      "weak_signals": [{"index": 7, "confidence": "low",
                        "signals": ["letterhead-change"], "jaccard": 0.12}],
      "overall_confidence": "high"
    }
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Page-number markers. Group 1 = current page, group 2 = total.
_PAGE_NUMBER_PATTERNS = [
    re.compile(r"\bpage\s+(\d+)\s+of\s+(\d+)\b", re.IGNORECASE),       # EN
    re.compile(r"\bseite\s+(\d+)\s+von\s+(\d+)\b", re.IGNORECASE),     # DE
    re.compile(r"(?<!\d)(\d+)\s*/\s*(\d+)(?!\d)"),                     # 1/3
]

# Address blocks near the top of a page.
_ADDRESS_PATTERNS = [
    re.compile(r"\b\d{5}\s+[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß.\- ]+"),       # DE: 12345 City
    re.compile(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b"),                    # US: CA 90210
]

_TOKEN = re.compile(r"[^\W\d_]+", re.UNICODE)

# Worst-to-best attention ordering used to fold per-boundary verdicts into one.
_RANK = {"ambiguous": 0, "low": 1, "medium": 2, "high": 3}


def page_number(top: str, bottom: str) -> tuple[int, int] | None:
    """Return ``(current, total)`` from a page-number marker, or ``None``.

    Searches the top and bottom slices (markers live in headers/footers).
    Returns the first plausible ``X of N`` with ``N >= current >= 1``.
    """
    for blob in (top, bottom):
        for pat in _PAGE_NUMBER_PATTERNS:
            for m in pat.finditer(blob):
                current, total = int(m.group(1)), int(m.group(2))
                if total >= current >= 1 and total > 0:
                    return current, total
    return None


def tokenize(text: str) -> set[str]:
    """Lowercase alphabetic word tokens (digits/punctuation dropped)."""
    return {t.lower() for t in _TOKEN.findall(text)}


def jaccard(a: set[str], b: set[str]) -> float:
    """Token-set Jaccard similarity. Two empty sets count as identical (1.0)."""
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def has_address_block(top: str) -> bool:
    """True if a DE or US postal address pattern appears in the top slice."""
    return any(pat.search(top) for pat in _ADDRESS_PATTERNS)


def detect_boundaries(pages: list[dict], jaccard_threshold: float = 0.3) -> dict:
    """Propose document boundaries over *pages* (extract_pages output)."""
    n = len(pages)
    boundaries = [0]
    start_confidence: dict[int, tuple[str, list[str]]] = {0: ("high", [])}
    weak_signals: list[dict] = []
    saw_continuation = False
    saw_reset = False

    for i in range(1, n):
        prev, cur = pages[i - 1], pages[i]
        num = page_number(cur.get("top", ""), cur.get("bottom", ""))
        reset = num is not None and num[0] == 1 and num[1] > 1
        continuation = num is not None and num[0] > 1
        saw_reset = saw_reset or reset
        saw_continuation = saw_continuation or continuation

        sim = jaccard(tokenize(prev.get("top", "")), tokenize(cur.get("top", "")))
        letterhead = sim < jaccard_threshold
        new_address = has_address_block(cur.get("top", "")) and not has_address_block(
            prev.get("top", "")
        )

        signals: list[str] = []
        if reset:
            signals.append("page-number-reset")
        if letterhead:
            signals.append("letterhead-change")
        if new_address:
            signals.append("address-block")

        if reset:
            confidence = "high"
        elif continuation and letterhead:
            # A "page 2 of N" marker contradicts a fresh letterhead -> conflict.
            confidence = "ambiguous"
        elif letterhead and new_address:
            confidence = "medium"
        elif letterhead or new_address:
            confidence = "low"
        else:
            confidence = None

        if confidence in ("high", "medium"):
            boundaries.append(i)
            start_confidence[i] = (confidence, signals)
        elif confidence in ("low", "ambiguous"):
            weak_signals.append(
                {
                    "index": i,
                    "confidence": confidence,
                    "signals": signals,
                    "jaccard": round(sim, 3),
                }
            )

    documents = []
    for pos, start in enumerate(boundaries):
        end = (boundaries[pos + 1] - 1) if pos + 1 < len(boundaries) else n - 1
        confidence, signals = start_confidence[start]
        documents.append(
            {
                "start": start,
                "end": end,
                "pages": list(range(start, end + 1)),
                "confidence": confidence,
                "signals": signals,
            }
        )

    overall = _overall_confidence(
        boundaries, start_confidence, weak_signals, n, saw_continuation, saw_reset
    )

    return {
        "page_count": n,
        "boundaries": boundaries,
        "documents": documents,
        "weak_signals": weak_signals,
        "overall_confidence": overall,
    }


def _overall_confidence(boundaries, start_confidence, weak_signals, n,
                        saw_continuation, saw_reset) -> str:
    """Fold per-boundary verdicts into a single escalation signal."""
    verdicts = [conf for idx, (conf, _) in start_confidence.items() if idx != 0]
    verdicts += [w["confidence"] for w in weak_signals]

    if not verdicts:
        # No boundary evidence at all -> single document.
        if n <= 1:
            return "high"
        # Positive single-doc evidence: consistent page numbers, no reset.
        if saw_continuation and not saw_reset:
            return "high"
        return "low"

    # Otherwise report the most attention-needing verdict present.
    return min(verdicts, key=lambda c: _RANK[c])


def _load(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages_json", help="extract_pages.py output (path, or - for stdin)")
    parser.add_argument("--jaccard", type=float, default=0.3,
                        help="letterhead-change threshold (default 0.3)")
    args = parser.parse_args()

    try:
        data = _load(args.pages_json)
        pages = data["pages"]
    except FileNotFoundError:
        print(f"not a file: {args.pages_json}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"invalid pages JSON: {e}", file=sys.stderr)
        return 1

    result = detect_boundaries(pages, args.jaccard)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
