---
name: split-batch
description: >
  Split a single multi-document PDF into one PDF per detected document. Post-processing
  for stacks of paperwork scanned in one pass: detect document boundaries from page content
  (page-number resets, letterhead/sender changes, address blocks) or from blank separator
  sheets, present a proposed split map, and emit one PDF per document after the user confirms.
  Use when the user has a searchable PDF that bundles several documents and says things like
  "split this batch", "split this stack", "these are multiple documents", "I scanned a pile",
  "separate these documents", or when `naps2-scan` hands off a batch-mode scan. Requires a
  searchable (OCR'd) PDF as input — it does NOT scan. For scanning, use `naps2-scan`.
---

<!-- Source: https://github.com/xxthunder/xxthunder-agentic-skills/tree/develop/plugins/xxthunder-paperless-skills/skills/split-batch -->

# Split Batch

Split one multi-document PDF into N single-document PDFs: **extract page text → detect boundaries → confirm split map → emit PDFs**.

## When This Skill Triggers

- "Split this batch" / "Split this stack" / "Separate these documents"
- "These are multiple documents" / "I scanned a pile / stack"
- `naps2-scan` hands off after a batch-mode scan (its Step 3b)
- The user has one searchable PDF in the working directory that bundles several distinct documents

This skill is **post-processing only**. It does not drive a scanner and does not OCR — it needs a PDF whose text is already extractable. To scan paper, use `naps2-scan` (which can chain into this skill). To merge two simplex halves, use `simplex-merge`.

## Prerequisites

- **A searchable PDF** in the working directory (typically `naps2-scan` output after OCR and any simplex merge). If the PDF has no extractable text, detection cannot run — tell the user to OCR it first (re-scan via `naps2-scan` with `--enableocr`).
- **`uv` on PATH** — the helper scripts under `scripts/` are [PEP 723](https://peps.python.org/pep-0723/) inline-metadata Python scripts run via `uv run`. Verify with `uv --version`. `uv` resolves `pypdf` automatically; no manual `pip install`. Install with `winget install astral-sh.uv` (Windows) or the installer at <https://docs.astral.sh/uv/>.

If a prerequisite is missing, stop and tell the user what to install or do.

## LLM Consent

Boundary detection runs **locally** (rules and separator mode read the PDF on-machine; no content leaves). But when the rules are inconclusive (`medium` or `ambiguous` confidence), this skill may escalate by reasoning over the extracted OCR text in-conversation — which transits Anthropic's API. This is the same trust boundary as `naps2-scan`'s filename proposal, and it shares one consent decision per conversation.

Before the first LLM-eligible step in a conversation (here, an escalation), ask:

> Analyse the document's OCR text via Claude to detect document boundaries? This sends the text to Anthropic's API. (yes = LLM escalation; no = I'll ask you where the boundaries are)

Cache the answer in-conversation and reuse it for any later LLM-eligible step (in this skill or `naps2-scan`) — do not re-ask. **Do not persist** it; the next conversation asks again. If consent was already given or denied earlier in this conversation (e.g. during `naps2-scan` filename proposal), reuse that answer here — do not ask twice.

On `deny`: detection stays rules-only. If confidence is `medium` or `ambiguous`, **do not escalate** — instead present what the rules found and ask the user directly where the boundaries are. No OCR text is transmitted.

## Workflow

### 1. Identify the input PDF

Find the multi-document PDF in the working directory (the `naps2-scan` output, or one the user names). If several PDFs are present, ask which one. Note its page count.

Ask whether the stack used **blank separator sheets** between documents. If yes → use separator mode (Step 2b); otherwise → content heuristics (Step 2a). Default to content heuristics if the user doesn't mention separators.

### 2. Extract page text

```bash
uv run <skill_dir>/scripts/extract_pages.py "<input.pdf>" --out pages.json
```

`<skill_dir>` is this skill's base directory (Claude Code provides it at load time). This writes `pages.json` — per-page text plus normalized top/bottom slices and a non-whitespace `char_count`. Exit `1` means the PDF is missing or unreadable: report it and stop.

### 2a. Detect boundaries — content heuristics (default)

```bash
uv run <skill_dir>/scripts/detect_boundaries.py pages.json
```

Reads the JSON and proposes boundaries from three offline rules: **page-number reset** (`page 1 of N` / `1/N` / `Seite 1 von N`), **letterhead change** (low token overlap between consecutive page tops), and **address block** (a postal address appearing on a page the previous one lacked). Output fields:

- `boundaries` — confident document start indices (0-based).
- `documents` — `{start, end, pages, confidence, signals}` per proposed document.
- `weak_signals` — pages with weak/conflicting evidence, not auto-split.
- `overall_confidence` — drives the next move:
  - **`high`** → accept the split as-is; go straight to the split map (Step 3).
  - **`medium`** / **`ambiguous`** → escalate to the LLM (consent-gated, see above). With consent, read `pages.json` yourself, reconcile the rule output with the text, and propose a refined split map; flag any disagreement with the rules. On deny, ask the user for boundaries.
  - **`low`** → the rules found little or no boundary evidence — typically a single proposed document. **This is suspicious in this skill**: `split-batch` only runs because the user (or `naps2-scan`'s batch handoff) asserted the input bundles *multiple* documents. The most common cause is several documents that share a letterhead and carry no page numbers — which the offline rules cannot split on. So treat `low` like `medium`: **escalate to the LLM (consent-gated)**. With consent, read `pages.json` and propose boundaries from content cues the rules miss — distinct document dates, a fresh salutation (`Sehr geehrte …` / `Dear …`), changed subject/reference numbers, or a new recipient address block mid-stream. On deny, ask the user directly where the boundaries are. Only conclude "it really is one document" after the LLM or the user confirms it — never silently because the rules were quiet.

### 2b. Detect boundaries — separator-sheet mode (opt-in)

Only when the user inserted blank separator sheets. Requires the scan profile's **Exclude blank pages** to have been **disabled** so the separators survive into the PDF.

```bash
uv run <skill_dir>/scripts/detect_separators.py pages.json
```

Splits deterministically on blank pages (non-whitespace `char_count` below the threshold), drops the separators, and returns `documents` with `overall_confidence: high`. No LLM, no tokens. Go to the split map.

### 3. Present the split map and accept edits

**Always** show the proposed split before emitting anything — even a wrong auto-split is cheap to fix. Present a numbered list, e.g.:

```
Proposed split (4 documents):
  1. pages 1–3   [page-number-reset]      confidence: high
  2. pages 4–5   [letterhead-change]      confidence: medium
  3. pages 6–8   [address-block]          confidence: low
  4. pages 9–11  [separator-sheet]        confidence: high
```

(Display page numbers 1-based for the user; the scripts use 0-based indices.)

Accept free-form edits and normalize them yourself before splitting:
- `merge 2+3` → combine documents 2 and 3.
- `split 1 at 2` → break document 1 after its 2nd page.
- `boundaries: 1,4,9` → replace the whole split with documents starting at those (1-based) pages.

Confirm the final map with the user before Step 4.

### 4. Emit the PDFs

Translate the confirmed map into 0-based page groups and split:

```bash
# General form — explicit groups (handles dropped separator pages):
uv run <skill_dir>/scripts/split_pdf.py "<input.pdf>" --groups "0-2;3-4;5-7;8-10"

# Shorthand when documents are contiguous and cover every page:
uv run <skill_dir>/scripts/split_pdf.py "<input.pdf>" --boundaries 0,3,5,8
```

Writes `part-01.pdf`, `part-02.pdf`, … into the input PDF's directory (override with `--outdir`). The original multi-document PDF is **kept** — never delete it automatically. Report the written filenames to the user.

### 5. Per-document filename proposal (when chained from naps2-scan)

When this skill runs as part of a `naps2-scan` batch (Step 3b), hand each emitted `part-NN.pdf` back to `naps2-scan` Step 4–5 to propose a content-derived filename per document, looping over the outputs. The same cached LLM-consent answer applies — on deny, `naps2-scan` asks for date / sender / topic directly per file.

When this skill is run **standalone** (e.g. on an email attachment), filename proposal does not run automatically. The user can invoke `naps2-scan` (post-processing entry point) on any output file to name it.

## Troubleshooting

- **"invalid pages JSON"**: `detect_boundaries.py` / `detect_separators.py` got something other than `extract_pages.py` output. Re-run Step 2 and pass the produced `pages.json`.
- **Empty or near-empty page text**: the PDF isn't OCR'd (or is image-only). Detection can't read content — re-scan with OCR via `naps2-scan`, or use separator mode if blanks are present and the user knows the layout.
- **Separator mode found no boundaries**: the profile likely dropped the blank pages (`Exclude blank pages` was enabled), so the separators never made it into the PDF. Disable that profile option and re-scan, or fall back to content heuristics.
- **Detection over-splits or under-splits**: that's expected sometimes — the split map is editable. Adjust with `merge`/`split`/`boundaries:` (Step 3). The heuristic thresholds are best-guess defaults and may be tuned over time.
- **`uv` not found**: install `uv` (`winget install astral-sh.uv` on Windows, or see <https://docs.astral.sh/uv/>). The scripts depend on PEP 723 metadata resolution that bare `python` does not provide.

## Notes

- The skill does **not** scan or OCR — it consumes an already-searchable PDF. Scanning is `naps2-scan`'s job.
- The skill does **not** auto-file the outputs into an archive folder — that's the `auto-file` skill.
- Page indices are 0-based in the scripts and JSON; show the user 1-based page numbers in the split map.
- The original multi-document PDF and any intermediate files are left in place for the user to delete.
