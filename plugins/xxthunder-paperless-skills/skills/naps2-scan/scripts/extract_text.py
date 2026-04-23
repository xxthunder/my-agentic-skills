# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=4"]
# ///
"""Extract text from a PDF to stdout."""
import argparse
import sys
from pathlib import Path

from pypdf import PdfReader


def extract_text(pdf: Path, max_pages: int = 0) -> str:
    """Return concatenated text of the PDF's pages.

    *max_pages* = 0 means all pages. Pages that fail to extract contribute
    an empty string rather than raising.
    """
    reader = PdfReader(str(pdf))
    pages = list(reader.pages)
    if max_pages > 0:
        pages = pages[:max_pages]
    parts: list[str] = []
    for page in pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument(
        "--pages",
        type=int,
        default=0,
        help="limit to first N pages (0 = all)",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"not a file: {args.pdf}", file=sys.stderr)
        return 1

    try:
        text = extract_text(args.pdf, args.pages)
    except Exception as e:
        print(f"cannot open PDF: {e}", file=sys.stderr)
        return 1

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
