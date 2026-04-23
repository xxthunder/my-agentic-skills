# [XAS-015a] Add `auto-file` skill (sort into configurable folder structure)

**Status**: Open
**Priority**: Medium
**Component**: plugins/xxthunder-paperless-skills/skills/auto-file/

**Summary**:
As a user with a digitized document, I want the file automatically classified and moved into the correct sub-folder of a given archive root so that my paperless archive stays organized without manual sorting.

**Description**:
New skill that takes an already-digitized PDF (typically produced by `naps2-scan`) plus a target archive root with a configured sub-folder schema, classifies the document by content, and moves the file into the right sub-folder. User is asked to confirm the classification before the move.

Expected flow:
1. Receive a source PDF and an archive-root path (from user or skill config).
2. Read OCR text (or filename metadata).
3. Classify by content (family / house / car / finance / ... — schema user-defined).
4. Propose the destination sub-folder and confirm with user.
5. Move (and optionally rename) the file into place.

**Open questions**:
- How is the folder schema configured? Options: (a) a config file in `~/.claude/paperless.yml`, (b) arguments passed to the skill each time, (c) learned from the existing archive contents.
- Classification strategy: LLM-based using OCR text vs. keyword rules vs. hybrid.
- Idempotency: what happens if the file already exists at the destination (duplicate detection, versioning, skip)?
- Multi-match handling: what if the document arguably belongs in more than one folder?

**Dependencies**:
- A digitized PDF as input (typically produced by `naps2-scan`, XAS-018)
- User's target archive root and sub-folder schema

**Acceptance Criteria**:
- [ ] `SKILL.md` created with clear trigger phrases ("file this", "sort this document", etc.)
- [ ] Accepts archive root + schema (mechanism per Open question resolution)
- [ ] Classifies document by content
- [ ] Asks user to confirm destination before moving
- [ ] Handles duplicate-at-destination gracefully (per decision on idempotency)
- [ ] Manual end-to-end test: classify and file a real document from each planned category
