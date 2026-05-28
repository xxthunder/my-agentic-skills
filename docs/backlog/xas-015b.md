# [XAS-015b] Add `split-batch` skill (detect + split multi-document PDFs)

**Status**: In Progress
**Priority**: Medium
**Component**: plugins/xxthunder-paperless-skills/skills/split-batch/, plugins/xxthunder-paperless-skills/skills/naps2-scan/SKILL.md

**Summary**:
As a user digitizing a stack of paperwork at once, I want a scanned PDF automatically split into individual documents based on content boundaries so that I can feed an entire pile through the scanner in one session instead of scanning each document separately.

**Description**:
Today `naps2-scan` assumes each scan session produces one document. Scanning 10 letters therefore means 10 sessions (20 passes on a simplex scanner). A new `split-batch` skill accepts a multi-document PDF and produces N separate PDFs, one per detected document.

Expected flow:
1. Receive a PDF (typically from `naps2-scan` after OCR and any simplex merge).
2. Detect document boundaries using local rules first (page-number regex, letterhead/sender change, address-block on first page of a doc).
3. Escalate ambiguous cases to an LLM over the OCR text — only when rules are inconclusive.
4. Present a proposed split map (e.g., "detected 4 documents at pages 1-3, 4-5, 6-8, 9-11"); user confirms or edits.
5. Emit N PDFs; caller (or user) runs filename proposal per document via the existing `naps2-scan` step.

`naps2-scan` will chain into this skill when the user signals batch mode ("I'm scanning a stack", "these are multiple documents"). Single-document scans continue to skip it.

**Scope Decisions**:
- **Placement**: standalone `split-batch` skill — not coupled to NAPS2. Accepts any searchable PDF so future inputs (email attachments, phone scans) work too.
- **Detection strategy**: **rules-first with LLM escalation**. Local regex/heuristics handle the common cases (page-number markers, letterhead change) for free and fully offline. LLM runs only when rules give ambiguous output.
- **Privacy posture**: rules run locally. LLM escalation sends OCR text to the Anthropic API — same trust boundary as the existing filename-proposal step, just wider scope when triggered.
- **Separator-sheet mode**: opt-in toggle. When enabled, blank pages (or a printed marker sheet) are treated as deterministic boundaries; heuristics skipped. Requires disabling `ExcludeBlankPages` in the NAPS2 profile for the batch scan.
- **User confirmation**: always present the proposed split map before emitting files. Even a wrong auto-split is cheap to correct, so optimising detection accuracy beyond "reasonable" is not worth it.
- **MVP scope**: detect + confirm + split. Filename proposal loops via existing `naps2-scan` Step 4-5. Auto-file integration is out of scope (handled separately by XAS-015a).

**Dependencies**:
- A searchable PDF as input (typically produced by `naps2-scan`, XAS-018)
- `uv` on PATH for helper scripts (same as `naps2-scan`)
- **XAS-015c** — test harness for plugin Python scripts (split-batch scripts must ship with tests per that harness)
- **XAS-015d** — privacy opt-in consent gate (governs whether LLM escalation may run; on deny, split-batch is rules-only with manual boundary prompt on ambiguity)

**Open questions** (resolve before implementation starts):
- **LLM escalation mechanism** — in-conversation reasoning by the running Claude Code instance (same trust model as the existing filename-proposal step), or a script-initiated Anthropic API call with its own key/config surface? Draft plan assumes the former.
- **Language coverage for MVP** — ship en + de regex sets only? Additional languages are a later patch bump.
- **Separator-sheet detection** — pure blank-page detection (text-length threshold) vs. requiring a printed QR/header marker. Draft plan picks blank-page detection because separator mode is opt-in.
- **Heuristic threshold constants** — Jaccard 0.3 for letterhead change, 50-char text-length for blank detection, 150-char top-block window. Ship best-guess defaults and retune after first UAT?
- **Standalone invocation** — when `split-batch` is run outside `naps2-scan` (e.g., on an email attachment), does filename proposal run? Draft plan says no — user manually invokes naps2-scan entry-point B per output file.

**Implementation Plan** (draft — pending resolution of open questions):

File layout:
```
plugins/xxthunder-paperless-skills/skills/split-batch/
  SKILL.md
  scripts/
    extract_pages.py        # per-page OCR text + top/bottom slices → JSON
    detect_boundaries.py    # rule-based detection on the JSON
    detect_separators.py    # blank-page mode
    split_pdf.py            # slice pages into N outputs
```

Detection rules (`detect_boundaries.py`):
- **Page-number reset** (strongest): regex on top/bottom 200 chars only. EN `page 1 of N`, `1/N`; DE `Seite 1 von N`.
- **Letterhead change**: token-set Jaccard on normalized top-150-char block of consecutive pages; <0.3 = signal.
- **Address block**: postal-code regex near top of page (DE 5-digit PLZ + city; US 2-letter state + ZIP).
- **Confidence classes**: `high` / `medium` / `low` / `ambiguous`. SKILL.md escalates on medium or ambiguous; accepts high without LLM; asks user on low (likely single doc).

Separator mode (`detect_separators.py`): text-length threshold (default 50 non-whitespace chars) flags a page as blank → boundary after each blank run. Opt-in only.

LLM escalation: Claude reads `pages.json` in-conversation (no script API call), proposes boundaries, flags disagreement with rules; user picks.

Split-map UI: numbered list with signals + confidence; free-form edits (`merge 2+3`, `boundaries: 1,4,9`) normalized by Claude before invoking `split_pdf.py`.

PDF splitting: `pypdf.PdfWriter`, output names `part-01.pdf`, `part-02.pdf`, … (zero-padded). Original multi-doc PDF kept; no auto-delete.

naps2-scan integration — minimal edits to its `SKILL.md`:
- Frontmatter description + trigger phrases: "scan this stack", "batch scan", "multiple documents".
- New **Step 3b (Split, batch mode only)** after merge that hands off to `split-batch` when user signalled batch mode.
- Note on Step 4: loop filename proposal per output file in batch mode.

Version bump: `plugins/xxthunder-paperless-skills/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` both minor-bump (new skill = new feature).

Commit: `feat(split-batch): add batch-PDF splitting skill` (conventional-commit scope matches skill name per CLAUDE.md).

**Acceptance Criteria**:
- [x] `SKILL.md` created with trigger phrases ("split this batch", "these are multiple documents", "split this stack", etc.)
- [x] Accepts a PDF in the current working directory as input
- [x] Rule-based boundary detection implemented (page-number regex, letterhead/sender change, address-block heuristic)
- [x] LLM escalation for ambiguous cases, with OCR text as input — gated by the XAS-015d consent (on deny, degrades to user-prompt for boundaries)
- [x] Separator-sheet mode toggle (deterministic splitting on blank/marker pages)
- [x] Presents proposed split map to user and accepts edits (add/remove/move boundaries) before committing
- [x] Emits one PDF per detected document after confirmation
- [x] `naps2-scan` SKILL.md updated to chain into `split-batch` when the user signals batch mode
- [x] Plugin version bumped in both `plugin.json` and `marketplace.json`
- [x] All new Python helper scripts covered by unit tests per the XAS-015c harness (behavior coverage of exit codes, JSON schemas, CLI flags)
- [x] Manual end-to-end test: scan a real stack of 3-5 documents and verify correct splits (see UAT below)

**User Acceptance Test**:

Prerequisites:
- All `naps2-scan` prerequisites (XAS-018 UAT) satisfied.
- `xxthunder-paperless-skills` plugin reinstalled from the feature branch or updated via `/plugin update`.

Test cases:

1. **Batch with mixed document types**
   - Prepare a stack of 3-5 documents (e.g., a 2-page letter with page numbers, a 1-page receipt, a 3-page invoice without page numbers, a 1-page statement).
   - Say "scan this stack, multiple documents".
   - Expect: `naps2-scan` runs, chains into `split-batch` after merge; skill proposes boundaries; user confirms; N PDFs produced; per-doc filename proposal runs on each.

2. **Page-number reset detection**
   - Stack of two multi-page documents, both with `Seite X von Y` markers.
   - Expect: split-batch detects the boundary at the second `Seite 1 von N` without LLM escalation.

3. **Separator-sheet mode**
   - Prepare a stack with blank pages inserted between documents. Disable `ExcludeBlankPages` in the NAPS2 profile.
   - Say "scan this stack, I used blank separators".
   - Expect: skill splits deterministically on the blank pages; zero LLM tokens used.

4. **Ambiguous boundary — LLM escalation**
   - Stack with two documents that share letterhead but are unrelated (e.g., two letters from the same sender on different topics).
   - Expect: rules return a weak/ambiguous split; LLM escalation invoked; proposal presented; user confirms or corrects.

5. **User correction**
   - Run any test case; intentionally adjust the proposed split map (merge two suggested docs into one, or split one suggested doc into two).
   - Expect: edits honoured in the emitted PDFs.
