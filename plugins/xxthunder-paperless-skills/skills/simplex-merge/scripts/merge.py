# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=4"]
# ///
"""Merge odd + reversed-even pages from a simplex scanner into one PDF.

The even (back) pages are assumed to be in reverse order because the user
flips the stack to scan the backs — so the last even page is scanned first.
"""
import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def interleave(odd_pages: list, even_pages_reversed: list) -> list:
    """Interleave odd (front) pages with reversed-even (back) pages.

    `even_pages_reversed` is the list of even pages already reversed (i.e.
    back-of-page-1 first). Returns a flat list: [odd1, even1, odd2, even2, ...].
    Excess pages in either input are appended at the end in their own order.
    """
    merged: list = []
    for i in range(len(odd_pages)):
        merged.append(odd_pages[i])
        if i < len(even_pages_reversed):
            merged.append(even_pages_reversed[i])
    for i in range(len(odd_pages), len(even_pages_reversed)):
        merged.append(even_pages_reversed[i])
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("odd", type=Path, help="PDF with odd (front) pages, in order")
    parser.add_argument("even", type=Path, help="PDF with even (back) pages, in reverse order")
    parser.add_argument("output", type=Path, help="output merged PDF")
    args = parser.parse_args()

    for label, p in [("odd", args.odd), ("even", args.even)]:
        if not p.is_file():
            print(f"{label}: not a file: {p}", file=sys.stderr)
            return 1

    odd_pages = list(PdfReader(str(args.odd)).pages)
    even_pages_reversed = list(reversed(list(PdfReader(str(args.even)).pages)))

    writer = PdfWriter()
    for page in interleave(odd_pages, even_pages_reversed):
        writer.add_page(page)

    try:
        with args.output.open("wb") as f:
            writer.write(f)
    except OSError as e:
        print(f"cannot write output: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
