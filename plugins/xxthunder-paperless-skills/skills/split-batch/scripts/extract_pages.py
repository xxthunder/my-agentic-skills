# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=4"]
# ///
"""Extract per-page text plus top/bottom slices from a PDF as JSON.

Output schema (stdout or --out file):

    {
      "pdf": "scan.pdf",
      "page_count": 11,
      "pages": [
        {"index": 0, "text": "...", "top": "...", "bottom": "...", "char_count": 412},
        ...
      ]
    }

`top` / `bottom` are whitespace-normalized leading/trailing slices used by the
boundary heuristics; `char_count` is the number of non-whitespace characters on
the page (used by separator-sheet detection). Pages that fail to extract
contribute empty strings rather than raising.
"""
import argparse
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

_WS = re.compile(r"\s+")


def _normalize(text: str) -> str:
    """Collapse all runs of whitespace to single spaces and strip."""
    return _WS.sub(" ", text).strip()


def _nonws_count(text: str) -> int:
    """Number of non-whitespace characters in *text*."""
    return sum(1 for ch in text if not ch.isspace())


def extract_pages(pdf: Path, top_chars: int = 150, bottom_chars: int = 200) -> dict:
    """Return the page-level extraction dict for *pdf*.

    *top_chars* / *bottom_chars* bound the normalized leading/trailing slices.
    """
    reader = PdfReader(str(pdf))
    pages: list[dict] = []
    for index, page in enumerate(reader.pages):
        try:
            raw = page.extract_text() or ""
        except Exception:
            raw = ""
        normalized = _normalize(raw)
        pages.append(
            {
                "index": index,
                "text": raw,
                "top": normalized[:top_chars],
                "bottom": normalized[-bottom_chars:] if bottom_chars else "",
                "char_count": _nonws_count(raw),
            }
        )
    return {"pdf": pdf.name, "page_count": len(pages), "pages": pages}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--top-chars", type=int, default=150)
    parser.add_argument("--bottom-chars", type=int, default=200)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="write JSON to this path instead of stdout",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"not a file: {args.pdf}", file=sys.stderr)
        return 1

    try:
        result = extract_pages(args.pdf, args.top_chars, args.bottom_chars)
    except Exception as e:
        print(f"cannot open PDF: {e}", file=sys.stderr)
        return 1

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out is not None:
        args.out.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
