---
name: simplex-merge
description: >
  Merge two existing PDF files (odd pages + even pages) into one correctly ordered document.
  Post-processing only — this skill does NOT drive a scanner. Use ONLY when the user already
  has two PDF files in the working directory that represent the fronts and backs of a
  double-sided document. Typical cues: filenames containing "ungerade"/"gerade" (German),
  "odd"/"even", or "front"/"back", or the user explicitly asks to merge, interleave, or
  combine two existing PDFs. Do NOT use this skill to start a new scan or to digitize
  paperwork — for scanning, use the `naps2-scan` skill instead.
---

<!-- Source: https://github.com/xxthunder/xxthunder-agentic-skills/tree/develop/plugins/xxthunder-paperless-skills/skills/simplex-merge -->

# Simplex Scanner PDF Merge

Post-processing skill: interleave two already-scanned PDFs (fronts + reversed backs) into one correctly ordered document. This skill does **not** drive the scanner — if the user wants to *start* scanning, hand off to `naps2-scan`.

When scanning double-sided documents with a single-sided (simplex) scanner, you end up with two files:
- **Odd pages** (front sides, often named "ungerade") — in correct order
- **Even pages** (back sides, often named "gerade") — in **reverse** order, because the user flips the stack to scan the backs, so the last even page is scanned first

## When to Use

- The user already has **two existing PDF files** in the working directory that look like front/back halves of a double-sided document.
- Filenames contain `ungerade`/`gerade`, `odd`/`even`, or `front`/`back`.
- The user explicitly asks to "merge these", "interleave these PDFs", "combine odd and even", or similar.

## When NOT to Use

- The user wants to **start a new scan** (phrases like "scan this", "let's scan", "scan another", "digitize") — use the `naps2-scan` skill instead. This skill will not produce scans.
- The user has only one PDF file — no merge needed.
- The user has more than two scan PDFs — this skill pairs exactly one odd file with one even file.

## Prerequisites

- **`uv` on PATH** — the skill's merge script under `scripts/` is a [PEP 723](https://peps.python.org/pep-0723/) inline-metadata Python script run via `uv run`. Verify with `uv --version`. Install with `winget install astral-sh.uv` (Windows) or the installer at <https://docs.astral.sh/uv/>. `uv` handles Python + the `pypdf` dependency automatically — no manual `pip install` needed.

## Workflow

### 1. Identify the files

Look for two PDF files in the working directory. Common naming patterns:
- `*ungerade*` / `*gerade*` (German: odd/even)
- `*odd*` / `*even*`
- `*front*` / `*back*`

If the files aren't obvious, ask the user which is which.

### 2. Merge

Run the merge script via `uv`. `<skill_dir>` is this skill's base directory (Claude Code provides it at skill load time):

```bash
uv run <skill_dir>/scripts/merge.py "<odd_pages_file>" "<even_pages_file>" "<output_file>"
```

`uv` resolves `pypdf` automatically from the script's PEP 723 header. The script reverses the even pages, interleaves with the odd pages, and handles the unusual case where there are more even pages than odd.

The output filename should match the common prefix of the input files (dropping the ungerade/gerade/odd/even suffix).

### 3. Check for blank trailing pages

After merging, report the total page count. If the user mentions a blank page, remove it by rewriting the PDF without that page. Simplex scanning often produces one extra blank page when the document has an odd number of pages.

### 4. Clean up

Do NOT delete the source files unless the user asks.
