# CLAIM_TABLE_VERSIONING.md

License: CC0 1.0 Universal.

How to version entries in `CLAIM_TABLE.fab.json` (and equivalent
files in sister repos) when new evidence updates a claim. The goal
is a *visible* probability landscape over time, not a hidden
revision.

## Rule: old version stays visible

When new evidence updates an existing claim, **do not overwrite**.
Add a new versioned entry; keep the old one. The probability
landscape becomes legible in the history because both the older
estimate and the newer one are visible side-by-side.

## Naming convention

| Artifact | Convention |
|---|---|
| Claim entry in `CLAIM_TABLE.fab.json` | `Cnnn` for v1; `Cnnn_v2`, `Cnnn_v3` for subsequent versions |
| Test file | `tests/test_<claim_id>_v<N>.py` (e.g., `tests/test_C020_v2.py`) |
| Module updates | Same module gains a `c020_verdict_v2(...)` function; original `c020_verdict` stays callable |
| Cross-references | Newer version cites the older one in its `relational_web` field |

## What triggers a version bump

A version bump (rather than a calibration tweak in defaults) is
warranted when:

1. **New primary-source evidence** changes the predicted threshold by
   more than its current sensitivity band.
2. **Falsifier is reframed** — the new version has a different,
   tighter falsifier sentence.
3. **Cycle class changes** (e.g., the phenomenon turns out to be
   day-scale rather than season-scale).
4. **Cross-references change** — the new version couples to different
   canonical equations or sister claims.
5. **Unit / denominator change** — moving from per-truck to per-ton-
   mile is a unit change, not a numeric tweak.

Pure numeric calibration (adjusting a default coefficient) **does
not** require a version bump — those are documented in the module
docstring and CHANGELOG.

## Required entries per versioned claim

For `Cnnn_vN` to be valid:

- `parent_claim_id`: `Cnnn` (or `Cnnn_v(N-1)`)
- `version`: `N`
- `superseded_by`: filled in retroactively on the parent when a new
  version lands (`"superseded_by": "Cnnn_v2"`)
- `source_citation`: link or DOI for the evidence triggering the
  version bump
- `change_summary`: one-sentence description of what changed
- All other fields (`observable`, `rate_equation`, `bounds`,
  `conditions`, `invalid_if`, `measured_by`, `cycle_class`,
  `relational_web`, `scope_envelope`, `data_source`, `sensitivity`,
  `allocation_rule`) re-stated in full — the entry must be self-
  contained per `schemas/claim_contract.Claim.from_dict`.

## Verdict-function evolution

When `Cnnn_v2` lands:

1. Add `cnnn_verdict_v2(...)` to the module.
2. The original `cnnn_verdict(...)` keeps its signature and behavior;
   downstream callers do not break.
3. Update the example scenarios to call `cnnn_verdict_v2()` if the
   v2 is the now-canonical version. The v1 remains accessible for
   historical comparison.
4. `tests/test_<module>.py` keeps any v1-specific calibration tests
   and adds the v2 calibration tests.

## How the registry stays append-only

The contract round-trip (`schemas/claim_contract.Claim.from_dict /
to_dict`) is the integrity guarantee for individual entries.
**Versioning preserves the structural history** by never deleting
the older entry. The Git log is the integrity guarantee for the
file as a whole.

Validator (`automation_scope_audit/validate_fab.py`) checks that:

- Every `Cnnn_vN` entry has a `parent_claim_id` field referring to
  an existing claim.
- Every parent claim with a `superseded_by` field points to an
  entry that exists in the file.
- Round-trip succeeds for every version.

## Worked example

If new audited Permian-corridor data shows the per-truck-per-day
backend energy is closer to 25,000 kWh than the C020 default ~17,000
kWh, the right move is:

1. Keep `C020` (default 17,000 kWh) and mark `superseded_by =
   "C020_v2"`.
2. Add `C020_v2` with:
   - `parent_claim_id: "C020"`
   - `version: 2`
   - `source_citation: "Atlas 2027 corridor audit, Kodiak 10-Q 2027"`
   - `change_summary: "backend energy share revised upward from
     ~17k kWh to ~25k kWh per truck per year based on operator
     disclosure"`
   - rest of fields as for the original C020 entry, with updated
     `sensitivity` if the dominant term has shifted.
3. Add `c020_verdict_v2(...)` to
   `automation_scope_audit/modules/thermodynamic_accounting_audit.py`.
4. Add `tests/test_C020_v2.py` (or extend `test_automation_scope_audit.py`)
   to lock the new calibration.
5. Update the example scenarios to call `c020_verdict_v2()` if v2 is
   now canonical.

## License

CC0 1.0 Universal.
