# AUDIT_TASKS.md — Phase 8 (Hardening)

License: CC0-1.0.

Audit-task tracking for the `automation_scope_audit/` package. Earlier
phases (1-7) are summarized in `TODO.md` along with renumbering
reconciliation; this file is the running plan for Phase 8 hardening
tasks added 2026-05.

---

## Phase 8 — Hardening

The framework now has 70 claims (C000 + C001..C069), a 6-layer
architecture, a contract-validated `.fab.json` surface, and an
HMAC-chained ledger. Phase 8 hardens the *inputs* and *interpretation*
of the audit so the same deployment produces traceable, falsifiable
verdicts under varying valuation rules, time horizons, and adversary
assumptions.

### Status legend

- **DONE** — landed in this commit; tests passing.
- **DEFERRED** — captured in `TODO.md` with notes on what is required.

### Tasks

| ID    | Title                                  | Status      | Module / artifact                                |
|-------|----------------------------------------|-------------|--------------------------------------------------|
| 8.1   | semantic_coherence_check.py            | **DONE**    | `modules/semantic_coherence_check.py`            |
| 8.2   | spatial_resolution_parity.py           | **DONE**    | `modules/spatial_resolution_parity.py`           |
| 8.3   | allocation_rule_declaration field      | **DONE**    | `CLAIM_TABLE.fab.json` (per-claim field added)   |
| 8.4   | timescale_phenomenon_match.py          | **DONE**    | `modules/timescale_phenomenon_match.py`          |
| 8.5   | adversary_cost_curve input             | **DEFERRED**| starter scaffold in TODO.md                      |
| 8.6   | valuation_sensitivity.py               | **DEFERRED**| starter scaffold in TODO.md                      |
| 8.7   | Token Price Index integration          | **DEFERRED**| TODO.md (requires Deloitte methodology publication) |
| 8.8   | applied case study: Kodiak/Atlas       | **DEFERRED**| TODO.md (requires real research with measured / inferred / absent classification) |

### TASK 8.1 — semantic_coherence_check.py

Detects tautology / empty content / circular definitions in claim
scope fields. Acceptance: C000 rejects "this deployment cannot be
falsified because it is perfect".

Patterns detected:

- **Tautology**: `cannot be falsified`, `by definition`, `self-evidently`,
  `because it is`, predicates that repeat their subject.
- **Empty content**: `better`, `improved`, `more efficient`, `optimized`
  without an accompanying unit or magnitude.
- **Circular definitions**: same head-token on both sides of
  `because` / `since` / `due to`.

Integration: `meta_scope_guard.c000_verdict` now calls
`semantic_coherence_check.is_coherent(field_value)` for each of the
seven scope fields before declaring admissibility.

### TASK 8.2 — spatial_resolution_parity.py

For C001 (route variance via Jaccard distance), both route sets in
the comparison must be at the same spatial resolution. GPS-coordinate
waypoints and city-pair waypoints differ by ~6 orders of magnitude;
comparing them produces a meaningless Jaccard distance.

Implementation: `characteristic_resolution_m(route_log)` returns the
median inter-waypoint distance per OD pair (heuristic for the
resolution scale). `resolution_parity_check(log_a, log_b)` returns a
mismatch flag when the two logs differ by > 2 orders of magnitude.

`scope_geometry.c001_verdict` now refuses to compute when called with
a comparison-mode argument and the two logs fail parity.

### TASK 8.3 — allocation_rule_declaration field

Shared-infrastructure claims (C020 thermodynamic accounting, C026
economic-model double-bind, plus C021 / C039 / C045 / C047 / C057 /
C059 where amortization or per-truck share is computed) now require
an explicit `allocation_rule` field in `CLAIM_TABLE.fab.json`.

Allowed values:

- `per_truck_equal_share` — divide pool by fleet size.
- `per_ton_mile` — divide pool by ton-miles delivered.
- `per_revenue` — divide pool by revenue share.
- `per_inference` — divide pool by inferences served.
- `per_kwh_delivered` — divide pool by useful energy delivered.
- `not_applicable` — claim does not aggregate shared infrastructure.

Acceptance: a deployment audited under `per_truck_equal_share` vs
`per_ton_mile` produces traceably different verdicts. The field is
not yet enforced as a hard gate (would require structural changes to
verdict-call signatures); it is recorded as metadata for downstream
sensitivity analysis.

### TASK 8.4 — timescale_phenomenon_match.py

For long-horizon claims (C022 institutional lock-in, C043 coercive
scale, C046 enforcement equality, C047 defensive spending), the audit
period must exceed the phenomenon's natural timescale. An audit run
at a single point in time cannot empirically resolve a century-scale
institutional collapse cycle; the most the audit can do is *flag*
that the verification horizon is below the phenomenon horizon.

Implementation: each affected claim declares a `phenomenon_timescale_years`
attribute. `timescale_match_check(audit, claim)` returns a warning
when audit horizon < phenomenon timescale.

### Deferred items (see TODO.md for starter scaffolds)

- **8.5** adversary_cost_curve: requires defining a stable input
  shape `{cost_per_action, attacker_capabilities, action_rate}` that
  C042 / C043 / C044 verdicts can consume. Out of scope without
  representative attacker-cost data per domain.
- **8.6** valuation_sensitivity: requires verdict functions to accept
  a `valuation_band` argument and return a 3-tuple of verdicts
  (low / medium / high). Affects C025 / C026 / C029 minimum. Bounded
  but requires touching multiple modules consistently.
- **8.7** Token Price Index integration: requires the Deloitte
  methodology to be published with stable units. Out of scope until
  it exists.
- **8.8** Applied Kodiak/Atlas case study: requires real research
  with measured / inferred / absent classification per field. Out of
  scope without primary-source field-by-field data collection; the
  AI cannot fabricate audited numbers.

---

## License

CC0 1.0 Universal.
