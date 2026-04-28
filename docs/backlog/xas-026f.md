# [XAS-026f] Coverage thresholds via codecov.yml

**Status**: Open
**Priority**: Low
**Component**: `codecov.yml`

**Summary**:
As a maintainer, I want enforced coverage thresholds so that PRs that meaningfully drop coverage are flagged automatically.

**Description**:
XAS-026b ships Codecov reporting only — no thresholds. Once the numbers have stabilized over a handful of PRs and we have a baseline, add a `codecov.yml` to enforce a minimum target and a maximum allowed dip.

**Depends on**: XAS-026b (need a stable baseline before setting numbers)

**Acceptance Criteria**:
- [ ] `codecov.yml` at repo root defines a `coverage.status.project` rule with `target` (a sensible baseline observed from recent PRs) and `threshold` (small allowed dip, e.g., 1%)
- [ ] `coverage.status.patch` rule enforces a target on the PR diff itself (catches new code that ships untested)
- [ ] At least one PR exercises the rule (deliberate dip below threshold) and the Codecov check fails as expected
- [ ] README or CONTRIBUTING notes the threshold policy and how to update it

**Technical Notes**:
- Set numbers from observed baseline, not from a wishlist — too-aggressive targets cause merge friction without quality gain.
- Per-component thresholds (per plugin, per skill) can come later if the single global rule proves too coarse.
