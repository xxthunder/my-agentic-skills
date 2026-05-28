# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Separator-sheet boundary detection over an extract_pages.py JSON file.

Deterministic, opt-in alternative to the heuristics in ``detect_boundaries.py``.
A page whose non-whitespace character count is below ``--threshold`` is treated
as a blank separator sheet: it ends the current document and is dropped from the
output. Runs of consecutive blanks collapse to a single boundary; leading and
trailing blanks are discarded.

Requires the scan profile's ``Exclude blank pages`` option to be DISABLED, so
the separator sheets actually survive into the PDF.

Output schema (stdout) mirrors detect_boundaries.py, minus weak signals — this
mode is always confident:

    {
      "page_count": 11,
      "blank_pages": [3, 7],
      "documents": [{"start": 0, "end": 2, "pages": [0,1,2],
                     "confidence": "high", "signals": ["separator-sheet"]}, ...],
      "overall_confidence": "high"
    }
"""
import argparse
import json
import sys
from pathlib import Path


def detect_separators(pages: list[dict], threshold: int = 50) -> dict:
    """Split *pages* on blank separator sheets (char_count < *threshold*)."""
    n = len(pages)
    blank_pages: list[int] = []
    groups: list[list[int]] = []
    current: list[int] = []

    for page in pages:
        index = page["index"]
        if page.get("char_count", 0) < threshold:
            blank_pages.append(index)
            if current:
                groups.append(current)
                current = []
        else:
            current.append(index)
    if current:
        groups.append(current)

    documents = [
        {
            "start": g[0],
            "end": g[-1],
            "pages": g,
            "confidence": "high",
            "signals": ["separator-sheet"],
        }
        for g in groups
    ]

    return {
        "page_count": n,
        "blank_pages": blank_pages,
        "documents": documents,
        "overall_confidence": "high",
    }


def _load(path: str) -> dict:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages_json", help="extract_pages.py output (path, or - for stdin)")
    parser.add_argument("--threshold", type=int, default=50,
                        help="max non-whitespace chars for a page to count as blank")
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

    result = detect_separators(pages, args.threshold)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
