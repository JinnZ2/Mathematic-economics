# automation_scope_audit / CLAUDE.md

Continuity protocol for future AI readers of this package.
License: CC0-1.0.

## What this package is

A falsifiable audit of autonomous-trucking ROI claims, with 33 numbered
structural claims (C000-C032) across 17 modules. Every claim conforms to
the repo-root `DIFFERENTIAL_FRAME.md`: each is a `dX/dt` under explicit
scope, with a single-sentence falsifier sufficient to refute it.
Contract-validated form: `CLAIM_TABLE.fab.json` (round-trips through
`schemas/claim_contract.Claim`).

## What this package is NOT

- **Not a prediction.** Every claim is a *structural* assertion about
  what would need to be true for the autonomous-trucking ROI narrative
  to hold. The threshold lines are calibrated against 2025-era public
  data; numbers will drift, but the structural shape persists.
- **Not a refusal.** The framework can register concerns OR not. The
  works case (Permian sand-haul on consolidated paved corridor) clears
  several claims; the fails case (dispersed Bakken-style wellsites)
  fails most. The framework is biased toward *honest accounting*, not
  toward "automation bad".
- **Not aligned with `vehicle_audit/`.** Different architecture, different
  scope. See `RELATION.md`.

## How to interpret output

`run.py` produces a per-claim verdict table with a `concern` column. Polarity:

- C001 and C004 are **prescriptive** claims (deployment in safe zone).
  `concern=YES` for these means the deployment violates the prescription.
  `concern=no` means the deployment satisfies it.
- All other claims are **structural**. `concern=YES` means the structural
  concern registers against this deployment. `concern=no` means it does
  not register (deployment is OK with respect to that specific claim).

A claim has not been *falsified* until its `falsifier` (single sentence
on each verdict dict) is satisfied by primary-source evidence.

## Tiered output

C001 (`scope_geometry`) also emits a `tier` field with four bins:
`fixed` (variance < 0.10), `hybrid_viable` (0.10-0.30), `variable`
(0.30-0.60), `chaotic` (>= 0.60). Use the tier for graduated routing
recommendations; use `threshold_met` for the binary 5% gate.

## 6-layer architecture

`architecture.py` encodes the 6-layer structural architecture:
technical → operational → behavioral → institutional → energy →
economic → technical (closed cycle). Every claim belongs to exactly
one layer or to the cross-cutting band; coverage check verifies this
on every run.

A deployment is `UNTENABLE_CYCLE_CLOSED` when every load-bearing
layer has at least one firing claim; `PARTIAL_FAILURE` when some
layers fire but not all; `ADMISSIBLE` only when zero layers register.

Run with `--layers` to see the per-layer status table and active
cycle edges. See `ARCHITECTURE.md` for the full architectural
description.

## Cluster signatures

`correlation.py` defines 8 curated cluster signatures (e.g.
`infrastructure_inadequacy_cluster: C001 + C003 + C014`,
`collapse_imminent_cluster: C022 + C024 + C025 + C032`). When multiple
related claims fire together, the cluster name surfaces the underlying
structural problem. Use `run.py --clusters` to see triggered clusters
per scenario.

## Scope gate

`modules/scope_gate.py` is the load-bearing pipeline-entry check. A
deployment spec must declare seven scope fields:

  beneficiary, conditions, time_period, resource, externalized_cost,
  profit_allocation, falsifier

with *measurable* values (numbers, lists, declarations longer than 8
characters, or a deliberate-open sentinel). Specs missing any field
trigger MISSING_SCOPE and the audit refuses to run unless
`--allow-missing-scope` is passed.

This is the engineering-grade falsifiability principle (C031 / C032)
applied to the framework itself: if a deployment spec doesn't publish
scope, the audit cannot be falsified — and an unfalsifiable audit is
not admissible.

## Per-claim cycle classes

Drawn from `DIFFERENTIAL_FRAME.md`'s `CycleClass` enum. Each claim in
`CLAIM_TABLE.fab.json` carries a `cycle_class`:

- **day**: per-evaluation claims (C000, C009, C010)
- **season**: operational labor and middleware (C002, C006, C008, C011-C013, C016)
- **generation**: deployment ROI and constraint authority (C001, C003-C005, C007, C014, C015, C017-C020)
- **century**: institutional and structural (C021-C024, C027-C032)
- **century to geologic**: Earth-system fragility (C025, C026)

Long-cycle claims look like permanence to the casual observer; they are
not permanence. See DIFFERENTIAL_FRAME.md section "Cycles are the
invariant, not the states."

## Adding a new claim

1. Pick a free claim ID (currently C033 is the next free number).
2. Add the verdict function in the appropriate existing module, OR
   create a new module under `modules/`. Each verdict function must
   return a dict with at minimum `claim_id`, `threshold_met`, and
   `falsifier`.
3. Add the claim entry to `CLAIM_TABLE.fab.json` with all required
   contract fields (round-trip via `validate_fab.py`).
4. Add a one-line entry to `equations.yaml::automation_scope_audit_claims:`
   with `cross_references` to any of the canonical 13 equations the
   new claim overlaps.
5. Wire the verdict into both `examples/kodiak_atlas_permian.py` and
   `examples/dispersed_wellsite.py`. Update the return-dict literal
   and the `CLAIM_ORDER` in `run.py`.
6. Add at least one assertion to `tests/test_automation_scope_audit.py`
   covering the new claim.

## Persistence

Every audit run appends verdicts to `epistemic_ledger.jsonl` (at repo
root) via the `AuditLedger` class in `epistemic_ledger.py`. Entries are
HMAC-chained; `AuditLedger.verify()` walks the chain end-to-end. Tampering
with any entry breaks the chain at that point and every entry after.

`--no-ledger` disables persistence. `--ledger-path` redirects to an
alternate path (useful for tests).

## Reading order for a fresh AI

1. `DIFFERENTIAL_FRAME.md` (repo root) — the ontology
2. `schemas/claim_contract.py` — the type-checkable claim shape
3. This package's `README.md` — thesis + 7 frames + 33 claim table
4. `CONTRACT_NOTES.md` — what schema requirements each claim must declare
5. `CLAIM_TABLE.fab.json` — contract-validated machine surface
6. `correlation.py` — cluster signatures
7. `examples/kodiak_atlas_permian.py` (works) and
   `examples/dispersed_wellsite.py` (fails) — paired contrast cases
8. `TODO.md` — what's deferred and why

## What NOT to do

- Don't merge with `vehicle_audit/`. See `RELATION.md`.
- Don't import from `physics_guard/` (the vendored-subtree import
  direction invariant in `tests/test_bridges.py::ImportDirectionInvariant`
  forbids it).
- Don't renumber existing claims silently. Downstream tools pin to
  C000-C032 IDs; renumber as an explicit refactor commit.
- Don't add a CI dependency on external networked services (the audit
  is stdlib-only and must remain so).
