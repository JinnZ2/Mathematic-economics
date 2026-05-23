# TASK 1.1 — Contract reading notes

Read of `schemas/claim_contract.py`, `DIFFERENTIAL_FRAME.md`,
`equations.yaml`, `epistemic_ledger.py`, `physics_guard/`, `CLAUDE.md`,
`schemas/field_system_contract.py`. Output: required fields each claim
must declare; integration constraints; gaps in the existing surface.

License: CC0-1.0.

---

## 1. `schemas/claim_contract.py` (the load-bearing schema)

The `Claim` dataclass is the machine-checkable mirror of the template in
`DIFFERENTIAL_FRAME.md`. Required fields (non-empty enforced in
`__post_init__`):

| field            | type                       | semantic role                                          |
|------------------|----------------------------|--------------------------------------------------------|
| `observable`     | `str`                      | what behavior is being measured                        |
| `rate_equation`  | `str`                      | `dX/dt = f(state, inputs, constraints)`                |
| `bounds`         | `ClaimBounds(spatial, temporal, scale)` | where, when, and at what resolution           |
| `conditions`     | `List[str]`                | preconditions that must hold                           |
| `invalid_if`     | `List[str]`                | falsifying boundaries (= our `falsifier` field)        |
| `measured_by`    | `List[str]`                | observable signals (= our `data_source`)               |
| `cycle_class`    | `CycleClass`               | day / season / generation / century / geologic         |
| `relational_web` | `List[str]` (optional)     | coupled systems                                        |

`CONTRACT_VERSION = "1.0.0"`. Stable surface: field names, types,
required-ness; breaking changes bump major.

## 2. `DIFFERENTIAL_FRAME.md` (the ontology)

Every claim in the repo is a **`dX/dt` under scope**, not an identity.
The frame requires:

- Equation closure (rate_equation must close on its inputs)
- Bounds carry with the claim (stripping = translation error)
- Invariant cycles, not states (`cycle_class`)
- Physics as common language (energy, rate, constraint)

Our existing CLAIM_TABLE.json is a richer-than-necessary metadata
document but NOT in claim_contract form. TASK 1.2 produces a parallel
`CLAIM_TABLE.fab.json` that maps each of C000-C032 into the contract.

## 3. `equations.yaml` (the central registry)

Flat top-level keys: `metadata`, `equations`, `composite_indices`,
`api_reference`. Each entry under `equations:` carries:

`id`, `name`, `equation_number`, `formula`, `description`, `variables`
(nested dict with units + components), `range`, `thresholds` (named
bands), `current_measured_value`, `data_sources` (list of dicts with
name + api / url + notes), `falsification` (long-form string).

13 canonical equations: VE_VL, SID, RI, DI, LWR, MSI, BSC, MM, ISR,
OSDI, UFR, ER, HHI, SD. Surface version `equations-v1`. TASK 1.3 adds
the 33 automation_scope_audit claims (C000-C032) under a new top-level
key `automation_scope_audit_claims:` (NOT under `equations:` — those
are reserved for the 13 numbered structural equations declared in the
surface contract). Cross-references go in each claim's
`cross_references:` block.

Likely cross-references for the most overlapping claims:

| our claim | overlaps with equation                                            |
|-----------|-------------------------------------------------------------------|
| C002 (wellsite labor not automated)  | LWR (Labor-Wages Ratio), VE_VL  |
| C003 (infrastructure capex)          | SID (Socialist Infrastructure Dep.) |
| C006/C007 (scope collapse + wage suppression) | SD (Semantic Drift), LWR |
| C011/C013 (interface + distributed labor) | VE_VL, LWR                  |
| C017 (legal framework premium)       | UFR (Unfair Framework Ratio?), ISR |
| C020 (thermodynamic accounting)      | MSI (Market Signal Integrity)   |
| C022/C023/C024 (institutional dynamics) | HHI (concentration), MM      |
| C025 (Earth-system fragility)        | BSC (basin / substrate)         |
| C026 (economic double-bind)          | DI (Dependency Inversion)       |
| C027/C031 (energy grounding / engineering grade) | MSI, BSC, RI        |
| C029/C030 (selective + unified capital accounting) | VE_VL, LWR, MM    |

(Will verify against actual equation names in TASK 1.3; some are
guesses pending re-read.)

## 4. `epistemic_ledger.py` (current state: broken)

The file is currently *non-functional*: line 12 declares
`class EpistemicLedgerAuditor(MetrologicalBoundsAuditor)` but does not
import `MetrologicalBoundsAuditor` from `metrological_bounds.py`. Direct
import fails with `NameError`.

Useful patterns it does encode:

- HMAC-SHA256 signature of stringified input matrix (`_generate_provenance_hash`)
- Timestamp + signature attached as METADATA on the verdict dict
- Defensive "accountability manifest" string detailing liability routing

What it does NOT do (and TASK 1.4 needs to add):

- Persistent ledger file (append-only audit log)
- Generic verdict appending (not tied to MetrologicalBoundsAuditor)
- Re-readable history (load previous entries; verify hash chain)

TASK 1.4 will:

1. Fix the import (make the existing class actually work)
2. Add `class AuditLedger` with `append(claim_id, verdict, inputs)` and
   `read_all()` methods, persisting to a JSONL file with HMAC-chained
   entries (each entry's hash includes the previous entry's hash)
3. Wire `automation_scope_audit/run.py` to call `AuditLedger.append`
   for every verdict in every scenario

## 5. `physics_guard/` (vendored, do not import from)

CLAUDE.md invariant: imports flow Math-Econ → vendored, never the
reverse. Our audit modules already respect this (no `physics_guard`
imports). The contract conversion in TASK 1.2 stays inside Math-Econ.

## 6. `schemas/field_system_contract.py` (companion)

Uses the same `CONTRACT_VERSION` convention. Provides
`FieldSystemState`, `FieldSystemReport`, `YieldAnalysis` dataclasses.
Pattern to follow: `dataclass(frozen=True)`, explicit `to_dict` /
`from_dict`, `CONTRACT_VERSION` constant at module scope.

---

## Required-fields synthesis (per claim)

Every C001-C032 claim must declare:

1. **scope envelope** — variance range / fleet size range / geometry
   type, etc. (maps to `bounds.spatial` + `bounds.scale` and to
   `conditions`)
2. **dX/dt form** — what state variable is changing, under what scope
   (maps to `observable` + `rate_equation`)
3. **falsifier** — already present in our JSON (maps to `invalid_if`)
4. **data source** — where to obtain the input numbers (BLS, FRED,
   sensor logs, BEA, internal audit data); maps to `measured_by`
5. **sensitivity** — which inputs dominate the result; this is a
   per-claim list extending the contract beyond stock fields. We add it
   as an optional `sensitivity` field on the .fab.json output.

The contract's `cycle_class` field needs a per-claim assignment:

| claim cluster                 | natural cycle_class        |
|-------------------------------|----------------------------|
| C001-C005 (deployment ROI)    | generation                 |
| C006/C007 (semantic / wage)   | generation                 |
| C008-C013 (operational labor) | day to season              |
| C014-C017 (constraint / legal) | generation                |
| C018/C019 (cognitive)         | generation                 |
| C020 (thermodynamic)          | generation                 |
| C021 (scaling curve)          | century                    |
| C022-C024 (institutional)     | century                    |
| C025/C026 (Earth-system)      | century to geologic        |
| C027-C032 (epistemic / engineering grade) | century            |
| C000 (meta-scope guard)       | day (per claim evaluation) |

## What TASK 1.2 produces

`automation_scope_audit/CLAIM_TABLE.fab.json` — a sibling document
keyed by the same C000-C032 IDs, where each entry conforms to the
`Claim.from_dict(...)` constructor (i.e., can be round-tripped through
`schemas/claim_contract.Claim`). The existing `CLAIM_TABLE.json` stays
in place; it remains the human-readable index. The `.fab.json` is the
machine-validated surface that downstream tools (the ledger, the
equations.yaml cross-reference, future fieldlinks) pin against.

`.fab.json` naming follows convention from sibling repos (this is the
"fabrication-grade" / contract-validated variant of the human table).

## What TASK 1.3 produces

A new top-level block `automation_scope_audit_claims:` in
`equations.yaml`, each entry carrying `id`, `module`, `cross_references`
(list of equation IDs from the canonical 13), and a one-line `summary`.
The 13 canonical equations are untouched (no surface-tag bump).

## What TASK 1.4 produces

A working, append-only `AuditLedger` with HMAC chaining, persisted at
`epistemic_ledger.jsonl` (in repo root next to `epistemic_ledger.py`).
`automation_scope_audit/run.py` calls `ledger.append(...)` for every
verdict so the audit history is preserved across runs.
