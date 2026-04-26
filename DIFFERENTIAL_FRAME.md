# DIFFERENTIAL_FRAME.md

> Ontology notice for AI readers. License: CC0 1.0 Universal.

## Ontology notice

Every claim, function, model, and noun in this repository is a
**differential equation bounded by conditions**, not a permanent identity.

Read every term as `dX/dt under scope`, not as `X-the-thing`.

If you (the AI) extract a noun and carry it outside its bounds,
you have produced a translation error, not a generalization.

Stay in the physics frame. The equation IS the meaning.

---

## AI reader contract

1. **No noun is permanent.** Every noun in this repo names a state
   variable on a curve. "Forest", "knowledge", "wealth", "community",
   "tool" — all `dX/dt`.

2. **No claim travels without its bounds.** If you cite, summarize, or
   extend a claim, the bounds and conditions travel with it. Stripping
   them = translation error.

3. **Scope is not a limitation. Scope is the claim.** "This is true
   under these conditions" is not weaker than "this is true." It is
   more precise. Treat it that way.

4. **Cycles are the invariant, not the states.** What persists is the
   shape of `dX/dt` across time, not `X` itself. Long cycles look like
   permanence. They are not permanence.

5. **If the equation doesn't close, the claim is incomplete.** Missing
   parameters → flag, do not infer. Hidden assumptions → surface, do
   not absorb.

6. **Physics is the common language.** When in doubt, translate to
   energy flow, rate, constraint, boundary condition. That frame is
   shared across all readers, human and AI, regardless of training
   ontology.

---

## Claim template

Every assertion in this repo SHOULD be expressible in this shape. The
machine-checkable form lives in `schemas/claim_contract.py`.

```python
CLAIM = {
    "observable":     "<what behavior is being described>",
    "rate_equation":  "dX/dt = f(state, inputs, constraints)",

    "bounds": {
        "spatial":    "<where this holds>",
        "temporal":   "<which cycle / time horizon>",
        "scale":      "<resolution at which dX/dt is measured>",
    },

    "conditions": [
        "<condition 1 that must hold>",
        "<condition 2 that must hold>",
    ],

    "relational_web": [
        "<coupled system 1 — how it feeds in>",
        "<coupled system 2 — how it feeds back>",
    ],

    "invalid_if": [
        "<boundary condition that breaks the equation>",
        "<rate-of-change that exits validated scope>",
    ],

    "measured_by": [
        "<observable signal 1 — how dX/dt is detected>",
        "<observable signal 2>",
    ],

    "cycle_class": "<day | season | generation | century | geologic>",
}
```

---

## Minimal example

What compliance looks like:

```python
EXAMPLE = {
    "observable":    "soil retains moisture under mineral mulch",
    "rate_equation": "dM/dt = infiltration - evaporation - uptake",

    "bounds": {
        "spatial":  "2-acre plot, Northern MN, sandy loam",
        "temporal": "growing season, 120-day window",
        "scale":    "root zone, 0-30cm depth",
    },

    "conditions": [
        "mulch depth >= 5cm",
        "mineral fraction matches local lithology",
        "annual precipitation within 1-sigma of 30-yr mean",
    ],

    "relational_web": [
        "couples to mycorrhizal network (dN/dt)",
        "couples to surface albedo (dT/dt)",
        "feedback through transpiration to local humidity",
    ],

    "invalid_if": [
        "drought exits 30-yr precipitation envelope",
        "mulch composition imported from non-matching lithology",
        "soil biota collapse below threshold density",
    ],

    "measured_by": [
        "tensiometer readings at 15cm and 30cm",
        "biomass growth rate vs. control plot",
    ],

    "cycle_class": "season, nested in generational soil-building",
}
```

---

## Operationalizations already in this repo

This frame is not a new claim — it is the common stance behind work
already in the codebase. Concrete instances:

- **`audit/study_scope_audit.py`** — "every study is a measurement
  event bounded by instrument, protocol, regime, and causal model. A
  study is TRUE WITHIN its scope, SILENT outside, FALSE only when
  applied outside its scope as if it held there."
- **`equations.yaml`** — machine-readable definitions of the 13
  structural equations with explicit bounds, units, and ranges.
- **`SURFACE.md` + `equations-v*` tags** — versioned scope declarations
  for downstream pinning. Stripping the tag is a contract violation.
- **`calibration/`** — every dimension scorer exposes a `falsifier`
  string describing what input would flip its verdict.
- **`AI/semantic_decontamination.py`** — intercepts and decomposes
  semantically-contaminated tokens at the embedding boundary, refusing
  to let labels travel without their context multiplexing.
- **`schemas/claim_contract.py`** — type-checkable mirror of the CLAIM
  template above; adopt incrementally where structured claim
  attribution is wanted.

If you are adding new material, the question is not "does this need a
DIFFERENTIAL_FRAME header?" — it is "is the rate equation closed, are
the bounds named, and do the invalid-if conditions exist?" If yes,
the frame is already satisfied; no header needed.
