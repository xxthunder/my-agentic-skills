# [XAS-015d] ✅ DONE - Privacy opt-in for LLM content analysis in naps2-scan and split-batch

**Status**: Done (2026-04-23)
**Priority**: Medium
**Component**: plugins/xxthunder-paperless-skills/skills/naps2-scan/SKILL.md, plugins/xxthunder-paperless-skills/skills/split-batch/SKILL.md

**Summary**:
As a user digitizing personal paperwork, I want to be asked once per conversation whether OCR text may be sent to an LLM so that I can keep sensitive documents fully local when I choose, without noisy per-invocation prompts.

**Description**:
Today `naps2-scan` Step 4-5 unconditionally sends OCR text to Claude for filename proposal — the first time the user runs the skill, content leaves the local machine without explicit consent. `split-batch` (XAS-015b) is designed to send OCR text for boundary escalation under the same trust boundary.

This item introduces an **in-conversation consent gate** shared by both skills: the first time any LLM-bound content step is about to run in a conversation, the skill asks "OK to use LLM to analyse document content? [yes / no]" and caches the answer for the rest of the conversation. The answer is **not persisted** — next conversation asks again. This keeps consent fresh without turning every scan into a modal dialog.

`allow` path: existing behavior. Filename proposal runs; split-batch LLM escalation runs.

`deny` path: manual fallback.
- `naps2-scan` filename proposal: skill asks the user directly for date / sender / topic components and assembles the filename from the answers. No OCR text is transmitted.
- `split-batch` detection: rules-only. If rules return `low` or `ambiguous` confidence, the skill asks the user for boundaries directly rather than escalating.

**Scope Decisions**:
- **Persistence**: in-conversation cache only. No config file field, no on-disk state. The skill's SKILL.md documents the protocol ("ask on first LLM-eligible step of the conversation; reuse the answer for all subsequent LLM-eligible steps in the same conversation").
- **Granularity**: one consent decision covers both filename proposal and boundary escalation within a single conversation. No finer-grained per-step consent.
- **Ask phrasing**: SKILL.md specifies exact wording so the two skills ask consistently. Proposed: _"This step can analyse the document's OCR text via the Claude LLM to {propose a filename | detect document boundaries}. OK to proceed? (yes = LLM; no = I'll ask you for the info manually)."_
- **Not a config field** (XAS-015d explicitly rejects the config-persistence option). Users who want zero LLM interaction can add a CLAUDE.md or user-preferences note; the skill will still ask, and they can answer "no" every time.
- **Scope limited to these two skills**. `auto-file` (XAS-015a) will need its own consent gate when it lands; out of scope here.

**Dependencies**:
- Touches `naps2-scan/SKILL.md` (XAS-018, Done). This item does **not** reopen XAS-018 — it is a forward-looking SKILL.md edit in a new substory.
- Referenced by `split-batch` (XAS-015b) for its LLM escalation path.

**Open questions**:
- Should the `deny` path for `split-batch` offer an "LLM just this once" override when rules return `ambiguous`, or strictly honor the session consent? Leaning strict (no override — user said no, skill respects it).
- Wording of the consent prompt — confirm the proposed phrasing during implementation or refine based on test use.

**Scope** (narrowed at close time): this item delivers the consent protocol and its implementation in `naps2-scan` only. Adoption of the same consent cache by `split-batch` is owned by XAS-015b — that item's AC `LLM escalation ... gated by the XAS-015d consent` covers the split-batch side and closes there.

**Acceptance Criteria**:
- [x] `naps2-scan/SKILL.md` gains a "LLM consent" section with the exact prompt wording and cache semantics; Step 4 references it before sending OCR text
- [x] On `allow`: existing LLM filename proposal behavior is preserved (same heuristics, same format, same examples)
- [x] On `deny` in `naps2-scan`: skill asks user for date / sender / topic directly and assembles the filename without any OCR text transmission
- [x] Consent is asked **once per conversation**, cached for subsequent LLM-eligible steps; no re-ask mid-conversation
- [x] Plugin version bumped in `plugin.json` and `marketplace.json`

**User Acceptance Test**:

1. **Consent gate appears**
   - Fresh conversation, run `naps2-scan` to the filename-proposal step. Expect: skill asks the consent question with the documented wording before reading OCR text.
2. **Allow path**
   - Answer `yes`. Expect: filename proposal runs as today; no re-ask in the same conversation when a subsequent scan reaches Step 4.
3. **Deny path — filename**
   - Answer `no`. Expect: skill asks for date / sender / topic directly; assembles a filename from the answers; no OCR text leaves local.
4. **Deny path — split-batch (requires XAS-015b)**
   - In a conversation where consent was denied, run a batch scan. Expect: rules-only detection; if low/ambiguous, skill asks user for boundaries.
5. **Consent scope**
   - Run a second scan in the same conversation. Expect: no re-ask; cached answer applies.
6. **Fresh conversation**
   - Start a new Claude Code session / clear context. Run `naps2-scan`. Expect: consent asked again.
