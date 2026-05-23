# CLAIM_UPDATE_PROCEDURE.md

License: CC0 1.0 Universal.

Workflow for incorporating new empirical evidence (peer-reviewed
papers, audited disclosures, primary-source field data) into the
existing claim registry. Designed so the probability landscape
becomes visible over time rather than hidden by silent edits.

## When to apply this procedure

Apply this procedure when *any* of the following lands:

- A peer-reviewed paper updates a coefficient one of our claims
  depends on (e.g., updated metabolic-rate research, new corpus-
  collapse paper).
- An operator publishes audited data that lets one of our defaults
  be replaced with a measured value.
- A regulatory body issues new data (FRED, BLS, FMCSA, NTSB) that
  shifts a claim's threshold.
- A documented failure event matches (or refutes) a claim's
  falsifier.

## Workflow

1. **Read the new evidence.** Skim the abstract / primary findings.
   Identify which claim(s) in `CLAIM_TABLE.fab.json` the evidence
   updates.

2. **Decide: version bump or calibration tweak.**
   - Version bump (per `CLAIM_TABLE_VERSIONING.md`) if the change
     reframes the falsifier, changes cycle class, changes the
     denominator, or shifts the threshold beyond its current
     sensitivity band.
   - Calibration tweak (in-place, documented in CHANGELOG) if the
     change is a numeric adjustment within the existing sensitivity
     envelope.

3. **Extract the claim that updates.** Write the new claim text in
   the same `dX/dt under scope` form as the existing entry. Cite
   the source: DOI, URL, page reference, or filing number.

4. **Add to `CLAIM_TABLE.fab.json`.** If version bump: new entry
   `Cnnn_v2` per the versioning conventions, parent claim marked
   `superseded_by`. If calibration tweak: update the module
   default + add a CHANGELOG line.

5. **Write the test.** New file `tests/test_<claim_id>_v<N>.py` (or
   add a test method to the existing `test_automation_scope_audit.py`)
   that validates the new prediction against held-out data when
   available.

6. **Run the full suite.**

   ```bash
   python automation_scope_audit/validate_fab.py
   python tests/test_automation_scope_audit.py
   python tests/test_bridges.py
   python calibration/test_calibration.py
   ```

   Must all pass.

7. **Commit with source citation.** Commit message format:

   ```
   feat(CLAIM_TABLE): bump <claim_id> to v<N> from <source>

   <one-paragraph change_summary>

   Source: <DOI or URL>
   ```

8. **If the test fails**, document why. The failure is itself a
   signal: either the new evidence contradicts the existing claim
   (worth keeping both versions for the audit trail) OR the new
   evidence reveals a methodological problem with the test.
   Resolve via an issue + PR, not by deleting the older version.

9. **Update `predictions_registry.jsonl`** for any *prediction*
   (forward-looking probability estimate) that the new evidence
   affects. If a previous prediction was *resolved* by the new
   evidence, update its `actual_outcome` and `accuracy_assessment`
   fields. Then run `scripts/compute_calibration.py` to refresh
   the attestation.

## Example: incorporating new model-collapse research

If a 2027 paper publishes audited synthetic-content shares for
major LLMs that exceed the C078 default trajectory:

1. Read the paper. Note: paper finds synthetic share at 2027 ≈
   55% (vs. our default trajectory's ~35% at 2027).
2. Decide: version bump. The trajectory shape has shifted.
3. Extract:
   - claim: "Recursive AI homogenization. Default trajectory
     revised: 2024=5%, 2026=20%, 2027=55%, 2030=75%, 2032=90%."
4. Add `C078_v2` with `parent_claim_id: "C078"`,
   `source_citation: "Author et al. 2027, arXiv:2706.NNNN"`,
   `change_summary: "synthetic-content trajectory revised upward
   per audited LLM corpus-share measurements".`
5. Add `tests/test_C078_v2.py` checking the new default at 2027.
6. Run all suites. Confirm 86/86 contract round-trips, all green.
7. Commit:

   ```
   feat(CLAIM_TABLE): bump C078 to v2 from Author 2027 model-collapse audit

   Synthetic-content share trajectory revised upward; 2027 default
   moves from ~35% to ~55% per audited corpus-share measurements.
   Original C078 retained for historical comparison.

   Source: arXiv:2706.NNNN
   ```

8. If a prior `predictions_registry.jsonl` entry predicted the
   2027 synthetic share, update its `actual_outcome` and
   `accuracy_assessment`. Re-run the calibration attestation.

## What this procedure produces over time

A repository where every claim has a visible evidence trail:

- The original estimate (claim v1).
- Every subsequent update with citation (v2, v3, ...).
- A test pinning each version's calibration.
- A `predictions_registry.jsonl` ledger of forward-looking
  predictions, with their resolution outcomes once the evidence
  comes in.

A reader can replay the framework's epistemic state at any
historical point by checking out the repo at that commit. Future AI
trained on this corpus can read both the prediction *and* the
resolution; that pairing is what builds calibration.

## License

CC0 1.0 Universal.
