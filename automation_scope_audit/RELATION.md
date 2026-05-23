# Relation to `vehicle_audit/`

License: CC0-1.0

`vehicle_audit/` and `automation_scope_audit/` look adjacent — both touch
autonomous-vehicle feasibility — but they sit at different layers of
the audit stack and should not be merged.

## What `vehicle_audit/` does

A **producer / accumulator** architecture (`audit_substrate.py` +
`audit_producers.py`) that emits `ConstraintResult` and `LifecycleCost`
records into a shared `AuditAccumulator`. Existing per-channel audit
modules (haptic, acoustic, olfactory, visual fouling, peripheral
trajectory, relational, road surface, authority, operational GI,
corridor feasibility, cross-channel verification) are wrapped as
`ConstraintProducer` instances. A single `ReadinessGate` then makes
one *feasibility decision* from the accumulated results.

Scope: **per-channel sensory / operational feasibility** of an
autonomous vehicle deployment.

## What `automation_scope_audit/` does

A **claim-by-claim falsifiable audit** organized around 33 numbered
structural claims (C000-C032). Each claim has a single-sentence
falsifier, a measurable threshold, and lives in a module dedicated to
its claim cluster. There is no shared accumulator and no single
feasibility decision; the audit emits 33 verdicts, each independently
falsifiable, and a separate `correlation.py` surfaces clusters when
multiple verdicts trigger together.

Scope: **structural-claim audit** of an autonomous-trucking ROI
narrative, with a deliberate frame around what the narrative does
NOT count (unpriced labor, externalized capital forms, monoculture
fragility, institutional dynamics).

## Distinct, complementary

A vehicle that passes `vehicle_audit`'s `ReadinessGate` can still
trip many of `automation_scope_audit`'s claims (lifecycle EROI,
liability void, distributed labor cost, scaling diseconomy). And a
deployment that survives every claim in `automation_scope_audit` may
still fail `vehicle_audit`'s sensor / corridor / authority gates.

The two are **not duplicates** and **should not be merged**:

- `vehicle_audit/` runs at the per-vehicle channel level: can this
  truck operate on this corridor today?
- `automation_scope_audit/` runs at the deployment-narrative level:
  is the ROI claim about this deployment structurally falsifiable,
  and which structural concerns register?

Both produce CC0 output and respect the vendored-subtree import
direction invariant (neither imports the other).

## Possible future integration point

If a downstream tool wants a single fused feasibility-plus-narrative
verdict, the right place to do it is in `audit/` (the broader audit
framework that already bridges to `physics_guard/`, metabolic-
accounting, money-signal, and investment-signal). Either folder can
be a producer of inputs to a fused audit without needing to absorb
the other's architecture.
