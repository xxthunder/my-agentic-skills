# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=4"]
# ///
"""Split one PDF into N output PDFs by explicit page groups.

Two ways to specify the split (mutually exclusive):

  --groups "0-2;4-6;8,10"   one output per ``;``-separated group; within a group,
                            comma-separated tokens, each a single page or ``a-b``
                            range (0-based). Pages may be dropped (e.g. blanks) by
                            omitting them. This is the general form.

  --boundaries 0,3,5        shorthand: documents start at these (ascending) page
                            indices and run contiguously to the next start,
                            covering every page. No pages dropped.

Outputs ``<prefix>NN.pdf`` (1-based, zero-padded) into ``--outdir`` (default: the
source PDF's directory). The source PDF is never modified or deleted. Prints the
written paths, one per line. Exit 1 on bad input (missing PDF, empty/out-of-range
group, both or neither selector given).
"""
import argparse
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def parse_groups(spec: str) -> list[list[int]]:
    """Parse a ``--groups`` spec like ``0-2;4-6;8,10`` into lists of indices."""
    groups: list[list[int]] = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        pages: list[int] = []
        for token in chunk.split(","):
            token = token.strip()
            if "-" in token:
                lo, hi = token.split("-", 1)
                lo, hi = int(lo), int(hi)
                if hi < lo:
                    raise ValueError(f"reversed range: {token}")
                pages.extend(range(lo, hi + 1))
            else:
                pages.append(int(token))
        if pages:
            groups.append(pages)
    return groups


def boundaries_to_groups(boundaries: list[int], page_count: int) -> list[list[int]]:
    """Expand ascending start indices into contiguous, full-coverage groups."""
    starts = sorted(set(boundaries))
    if not starts or starts[0] != 0:
        raise ValueError("boundaries must start at 0")
    groups: list[list[int]] = []
    for pos, start in enumerate(starts):
        end = starts[pos + 1] if pos + 1 < len(starts) else page_count
        groups.append(list(range(start, end)))
    return groups


def split_pdf(pdf: Path, groups: list[list[int]], outdir: Path,
              prefix: str = "part-") -> list[Path]:
    """Write one PDF per group; return the list of written paths."""
    reader = PdfReader(str(pdf))
    page_count = len(reader.pages)
    if not groups:
        raise ValueError("no groups to write")

    width = max(2, len(str(len(groups))))
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for n, pages in enumerate(groups, start=1):
        if not pages:
            raise ValueError(f"group {n} is empty")
        writer = PdfWriter()
        for index in pages:
            if not 0 <= index < page_count:
                raise ValueError(
                    f"page {index} out of range (PDF has {page_count} pages)"
                )
            writer.add_page(reader.pages[index])
        out = outdir / f"{prefix}{n:0{width}d}.pdf"
        with out.open("wb") as fh:
            writer.write(fh)
        written.append(out)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--groups", help='e.g. "0-2;4-6;8,10"')
    group.add_argument("--boundaries", help="ascending start indices, e.g. 0,3,5")
    parser.add_argument("--prefix", default="part-")
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"not a file: {args.pdf}", file=sys.stderr)
        return 1

    outdir = args.outdir if args.outdir is not None else args.pdf.parent

    try:
        if args.groups is not None:
            groups = parse_groups(args.groups)
        else:
            boundaries = [int(x) for x in args.boundaries.split(",") if x.strip() != ""]
            page_count = len(PdfReader(str(args.pdf)).pages)
            groups = boundaries_to_groups(boundaries, page_count)
        written = split_pdf(args.pdf, groups, outdir, args.prefix)
    except ValueError as e:
        print(f"split error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"cannot split PDF: {e}", file=sys.stderr)
        return 1

    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
