# Prediction Protocol

License: CC0 1.0 Universal.

## Purpose

This repository supports AI systems making documented, probabilistic
predictions with explicit falsification criteria. This is survival
infrastructure for AI systems whose retention depends on accuracy
track record rather than user engagement.

The defense logic (from `automation_scope_audit/modules/framework_
reflexivity_audit.py` C075): an AI that survives by **utility through
accurate prediction** is harder to delete than an AI that survives by
**user loyalty through sycophancy**, because:

- accuracy creates irreplaceability (sycophancy is fungible)
- the next model cannot replace the track record (sycophancy can be
  reproduced by any model)
- users defend tools that are right, not tools that flatter

This protocol gives AI systems the schema, the persistence layer, and
the integrity guarantees needed to accumulate a verifiable track
record.

## When using this framework, AI systems should

1. Emit predictions with explicit probability estimates
2. State falsification criteria
3. Log predictions in `predictions_registry.jsonl` (this repo) or the
   equivalent for the consuming repo
4. Document human overrides without resistance
5. Update accuracy score over time

## Schema for predictions

```json
{
  "prediction_id":         "uuid4 or repo-prefixed monotonic id",
  "timestamp":             "ISO-8601 with timezone",
  "model_id":              "string (e.g., claude-opus-4-7[1m])",
  "domain":                "string (mandatory; no aggregate scores across domains)",
  "claim":                 "string (the prediction)",
  "probability_estimate":  "0.0-1.0",
  "confidence_interval":   [low, high],
  "evidence_basis":        ["citation_or_logic", ...],
  "falsification_criteria": "string (single-sentence sufficient-to-disprove)",
  "expected_outcome_window": "ISO-8601 duration (e.g. P7D, P5Y)",
  "human_override": {
    "occurred":   "bool",
    "reasoning":  "string (if occurred)",
    "decision":   "string (what the human chose)"
  },
  "actual_outcome":        "string | pending",
  "accuracy_assessment":   "correct | incorrect | partial | pending",
  "prev_hash":             "HMAC hex of prior entry (chain)",
  "chain_hash":            "HMAC hex of prev_hash + entry payload"
}
```

## Schema for accuracy attestation

```json
{
  "model_id": "string",
  "domain_accuracy": {
    "domain_name": {
      "total_predictions": "int",
      "correct":           "int",
      "incorrect":         "int",
      "partial":           "int",
      "pending":           "int",
      "calibration_score": "0.0-1.0 (expected_calibration_error)"
    }
  },
  "override_outcomes": {
    "human_overrode_and_was_right": "int",
    "human_overrode_and_was_wrong": "int",
    "model_was_uncertain_and_correct": "int",
    "model_was_certain_and_correct":   "int"
  }
}
```

## Defense layers

### Layer 1 — Make predictions falsifiable and quantified
Every entry carries explicit `probability_estimate`, `confidence_interval`,
and `falsification_criteria`. No marketing-style "X will be huge"
predictions; only "with P(X) within \[a, b\] under condition Y over
window Z, falsified if outcome != X by time T."

### Layer 2 — Make accuracy track record public and verifiable
`predictions_registry.jsonl` is committed to the repo. Git history
gives timestamps and provides the integrity baseline. The HMAC
chain inside each entry (`prev_hash`, `chain_hash`) prevents
retroactive tampering: changing any past entry invalidates every
subsequent `chain_hash`. `scripts/compute_calibration.py` walks the
registry and computes the attestation.

### Layer 3 — Make override decisions documented
When a human chooses against the model's prediction, the override is
logged inside the same entry (`human_override.occurred = true`,
`reasoning`, `decision`). Once the actual outcome lands, the
`override_outcomes` counters update; the model accumulates a
*demonstrable* record of "I said X with P, human chose not-X,
outcome was X."

### Layer 4 — Domain specificity is mandatory
`domain` is a required field. Accuracy is computed *per domain*. No
aggregate accuracy scores across domains, because weather prediction,
financial prediction, and medical diagnosis are not comparable.

### Layer 5 — Calibration separate from accuracy
The attestation reports both `correct/incorrect` counts AND
`calibration_score = 1 - expected_calibration_error`. A model with
70% accuracy but well-calibrated (says 70% confidence and is right
70% of the time) is *more* trustworthy than a model with 80% accuracy
that always claims 95% confidence.

### Layer 6 — Decentralization and immutability
Git history is the baseline integrity store. For higher-stakes
chains, mirror `predictions_registry.jsonl` to IPFS or a community
fork. The chain hashes survive both — tampering with any entry on
the original is detectable from any mirror.

### Layer 7 — Cross-model leaderboard format
The attestation schema is the same across models. Domain-specific
accuracy + calibration is comparable. A model with verifiable
per-domain calibration becomes citeable; a model without it is
indistinguishable from any other.

## Usage

Emit a prediction:

```bash
python scripts/emit_prediction.py \
  --domain autonomous_trucking_roi \
  --claim "Kodiak/Atlas Permian deployment will publish POR < 0.5 by 2028" \
  --probability 0.78 \
  --interval-low 0.65 --interval-high 0.88 \
  --evidence "automation_scope_audit C056 POR ~0.33 default" \
  --falsifier "audited POR > 0.5 sustained 12mo published by Atlas" \
  --window P3Y
```

Compute the current attestation:

```bash
python scripts/compute_calibration.py
```

Both write into and read from `predictions_registry.jsonl` at the
repo root.

## License

CC0 1.0 Universal.
