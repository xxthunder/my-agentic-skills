# [XAS-015e] Harden split-batch page-number rule: detect self-contained pages

**Status**: Open
**Priority**: Low
**Component**: plugins/xxthunder-paperless-skills/skills/split-batch/scripts/detect_boundaries.py

**Summary**:
As a user splitting a stack of same-sender documents, I want the offline rules to recognise pages that declare themselves complete (e.g. `Seite 1 von 1`) so that common batches split correctly without falling back to LLM escalation.

**Description**:
Surfaced during XAS-015b UAT (2026-05-28). A real two-document batch — two single-page VGF letters (an *Abbuchungsinformation* and a *Kündigung*) for the same recipient — was scanned into one 2-page PDF. `detect_boundaries.py` returned a single document at `low` confidence, finding **zero** signals, because:

1. Both pages share an identical VGF letterhead, so the letterhead-change rule (correctly) stayed quiet.
2. Page 0 carried `Seite: 1 von 1` — explicitly a complete one-page document — but the page-number **reset** rule only inspects pages *after* the first (`i >= 1`), so a `1 von N` marker on page 0 is never used as positive single-doc / boundary evidence.
3. Page 1's own `Seite:` value fell outside the captured top/bottom slice (and was OCR-garbled), so no marker was detected there either.

XAS-015b shipped a SKILL.md fix that routes `low`-confidence-in-batch-mode to LLM escalation, which resolved the case from content cues. This item is the **rules-side hardening** so the same batch splits *offline* (no tokens) — the rules-first half of the rules-first/LLM-escalation design.

**Scope Decisions**:
- Rules-only change in `detect_boundaries.py`; no SKILL.md behaviour change required (escalation already covers the gap as a safety net).
- A page whose marker reads `Seite X von X` / `page X of X` (current == total, i.e. a complete document on one logical span) is a **self-contained-document** signal. The page *after* such a page is a high-confidence boundary; the self-contained page itself closes the current document.
- Also consider page-number markers on page 0: a `1 von N` on the first page is consistent (not a boundary), but it establishes a running sequence the detector can use to spot the next reset more reliably.
- Widen / re-scan the page-number search if the marker commonly lands outside the current top/bottom slice — evaluate enlarging the slice or scanning full page text for the page-number regex only (cheap, no extra I/O since `extract_pages.py` already has full text).

**Dependencies**:
- Builds on XAS-015b (split-batch skill + scripts + test harness). [[xas-015b]]

**Open questions**:
- Is `Seite X von X` (e.g. `3 von 3`) on a non-final page genuinely a boundary, or could it be a multi-part document where each part paginates independently? Default: treat `X von X` as a document end (boundary after) and let the user correct via the split map.
- Should the page-number regex scan full page text rather than the top/bottom slices? Slices keep false positives down (body text rarely matches), but this UAT shows markers can fall outside them. Decide with a fixture from the VGF sample.

**Acceptance Criteria**:
- [ ] `detect_boundaries.py` treats a `Seite X von X` / `page X of X` marker as a self-contained-document signal: a boundary is emitted after that page when a following page exists
- [ ] First-page (`index 0`) page-number markers are no longer ignored — at minimum they do not suppress detection of a self-contained page 0
- [ ] The XAS-015b UAT batch (two same-sender single-page VGF letters) splits into 2 documents from rules alone, at `high` or `medium` confidence, with no LLM escalation
- [ ] New unit tests cover: `X von X` on a middle page, `1 von 1` on page 0 followed by a second document, and a genuine multi-page doc (`1..N von N`) that must NOT over-split
- [ ] Existing detect_boundaries tests still pass (no regression to letterhead / address / reset rules)
- [ ] Plugin version bumped in `plugin.json` and `marketplace.json` (patch — rule refinement, no new skill)

**User Acceptance Test**:
1. Re-scan or reuse the XAS-015b UAT sample (two single-page VGF letters in one PDF). Run `split-batch` with consent **denied**. Expect: rules alone propose 2 documents (boundary after page 1), no LLM escalation.
2. Scan a genuine multi-page single document with `Seite 1 von 3 … 3 von 3`. Expect: one document, no over-split.
