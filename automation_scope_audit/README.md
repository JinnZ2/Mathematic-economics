# automation_scope_audit

Falsifiable audit of autonomous-trucking ROI claims, with emphasis on
oilfield / dispersed-well contexts where the marketing narrative diverges
most sharply from operational physics.

License: **CC0 1.0 Universal** — public domain.

## Thesis

Autonomous trucking ROI is real on a narrow geometric envelope (fixed
depot-to-pad routes on existing paved corridors in consolidated plays) and
structurally untenable everywhere else. The marketing narrative typically
operates by:

1. **Scope collapse** — collapsing haul, navigation, site work, monitoring,
   compliance, and interface labor into a single "automation" category, then
   pricing only the easiest piece (interstate haul).
2. **Unpriced infrastructure** — omitting the road, the lane markings, the
   HD maps, the receiving pads, and the comms towers from capex.
3. **Unpriced monitoring labor** — omitting the ~60 min/day of pretrip,
   posttrip, fluid, tire, brake, and undercarriage inspection that the
   driver currently performs for free.
4. **Interface externalization** — the driver-mediated interfaces (fuel,
   customer, dispatch, maintenance, regulatory, roadside, payment) are
   not eliminated; they are externalized onto middleware, heterogeneous
   third parties, and distributed labor at higher fully-loaded cost.
5. **Lifecycle mismatch** — depreciating equipment over 7 years against
   shale wells that lose 70-80% of flow in year one.
6. **Missing constraint-validation authority** — drivers carry legally-
   recognized refusal authority, override authority, and a settled
   liability chain; autonomous stacks do not.
7. **Legal / regulatory framework cost** — litigation defense,
   regulatory engagement, and lobbying for liability shields are
   structural operating expenses, not one-time startup costs.
8. **Cognitive monoculture** — human domain expertise atrophies during
   transition to AI dominance; degraded-mode operation disappears
   alongside the skill that once made recovery possible.
9. **Transition energy cost** — monoculture appears cheaper at steady
   state but pays a recovery cost (human re-skilling + AI retraining +
   downtime + cascade) when edge cases occur.
10. **Incomplete thermodynamic accounting** — apparent eROI counts fuel
    savings against truck operations; honest eROI must include server
    farm electricity, sensor manufacturing, rare-earth extraction,
    network transmission, and software / CI-CD energy.
11. **Scaling masks per-system costs** — backend amortizes (descending
    1/n term) but coordination overhead, infrastructure sprawl,
    regulatory complexity, and cascade risk are per-system (ascending).
    The true cost curve has an interior optimum, and current accounting
    counts only the descending term.
12. **Institutional dynamics** — at scale, institutions develop lock-in
    that blocks optimization, exclude knowledge that threatens their
    scale, and enter an accelerated collapse cycle when external
    variation finally arrives.

C000 is a *meta-claim*: a scope-admissibility gate that every other claim
(C001-C024) must pass. An "automation is more efficient" claim that does
not specify beneficiary, conditions, time period, resource, externalized
costs, profit distribution, and falsifier is structurally unfalsifiable
and inadmissible to physics-grounded analysis.

## Claims at a glance

See `CLAIM_TABLE.json` for the full machine-readable list.

| ID    | Module                            | Statement (short)                                |
|-------|-----------------------------------|--------------------------------------------------|
| C000  | meta_scope_guard                  | Meta-claim: all claims must specify 7 scope dimensions |
| C001  | scope_geometry                    | ROI requires fixed geometry (Jaccard distance)   |
| C002  | embedded_labor_audit              | Wellsite labor not automated; 20-task automation_status |
| C003  | infrastructure_precondition       | Infra capex > vehicle capex with existing-state discounts |
| C004  | lifecycle_eroi                    | ROI window must exceed well decline curve        |
| C005  | stranded_asset_risk               | Resale to non-consolidated operators -> zero     |
| C006  | scope_collapse_detector           | "Automation" framing collapses labor categories  |
| C007  | scope_collapse_detector           | Threat narrative correlates with wage suppression|
| C008  | condition_monitoring_audit        | Driver monitoring is unpriced infrastructure     |
| C009  | condition_monitoring_audit        | Sensor replacement introduces new failure modes  |
| C010  | condition_monitoring_audit        | Roadside breakdown cost scales nonlinearly       |
| C011  | interface_externalization_audit   | Middleware lifecycle cost > driver-mediated      |
| C012  | interface_externalization_audit   | Heterogeneity risk: variant_count * miss * cost  |
| C013  | interface_externalization_audit   | Distributed labor cost >= half a driver          |
| C014  | constraint_validation_audit       | Refusal authority is unpriced legal authority    |
| C015  | constraint_validation_audit       | Liability void across 7-participant chain        |
| C016  | constraint_validation_audit       | Override hierarchy misses novel conflicts        |
| C017  | legal_liability_audit             | Framework + litigation premium > 1.5x conventional |
| C018  | cognitive_monoculture_audit       | Human domain expertise atrophies during AI transition |
| C019  | cognitive_monoculture_audit       | Edge-case recovery cost > apparent monoculture savings |
| C020  | thermodynamic_accounting_audit    | Honest eROI < 1.5 with full energy stack accounted |
| C021  | scaling_audit                     | Scaling has interior optimum; per-system costs hidden |
| C022  | institutional_dynamics_audit      | Institutional scale creates lock-in / gatekeeping |
| C023  | institutional_dynamics_audit      | Institutional monoculture creates knowledge exclusion |
| C024  | institutional_dynamics_audit      | Institutional lock-in -> accelerated collapse cycle |

## Layout

```
automation_scope_audit/
├── README.md
├── CLAIM_TABLE.json
├── run.py                                # entrypoint
├── modules/
│   ├── __init__.py
│   ├── scope_geometry.py                 # C001
│   ├── infrastructure_precondition.py    # C003
│   ├── embedded_labor_audit.py           # C002
│   ├── lifecycle_eroi.py                 # C004
│   ├── stranded_asset_risk.py            # C005
│   ├── condition_monitoring_audit.py     # C008, C009, C010
│   ├── scope_collapse_detector.py        # C006, C007
│   ├── interface_externalization_audit.py # C011, C012, C013
│   ├── constraint_validation_audit.py    # C014, C015, C016
│   ├── legal_liability_audit.py          # C017
│   ├── cognitive_monoculture_audit.py    # C018, C019
│   ├── thermodynamic_accounting_audit.py # C020
│   ├── scaling_audit.py                  # C021
│   ├── institutional_dynamics_audit.py   # C022, C023, C024
│   └── meta_scope_guard.py               # C000
└── examples/
    ├── kodiak_atlas_permian.py           # works case
    └── dispersed_wellsite.py             # fails case
```

## Usage

```bash
# Both examples, summary table
python automation_scope_audit/run.py

# Works case only
python automation_scope_audit/run.py --scenario works

# Raw JSON
python automation_scope_audit/run.py --json
```

Each module is also runnable standalone for inspection, e.g.:

```bash
python automation_scope_audit/modules/scope_geometry.py
python automation_scope_audit/modules/interface_externalization_audit.py
python automation_scope_audit/modules/constraint_validation_audit.py
python automation_scope_audit/modules/legal_liability_audit.py
```

## Concern polarity

`run.py` normalizes a per-claim `concern_registers` boolean across all 17
claims. For C001 (Jaccard variance) and C004 (lifecycle EROI vs decline)
the per-claim `threshold_met` field describes the *prescriptive* condition
(deployment in the safe zone), so the runner inverts those two for the
unified concern column. Every other claim uses `threshold_met = True` to
indicate the structural concern registers against the deployment.

## Default numbers

Default unit costs, retention curves, sensor cost envelopes, distributed-
labor stacks, refusal-event rates, liability-void probabilities, and
framework costs are 2025 US dollar / SI joule conservative estimates.
Each constant is exposed at module scope so callers can override with
audited data when available — the framework is the load-bearing piece,
the numbers are placeholders.

## Falsification

Every claim publishes a single-sentence falsifier. A claim is *retired*
when a primary source produces evidence matching that falsifier; until
then the claim survives. The works case (`kodiak_atlas_permian.py`)
deliberately satisfies the thresholds for C001, C003, and C004 to show
that the framework does not auto-reject every deployment; the fails case
(`dispersed_wellsite.py`) shows which claims register simultaneously when
the geometry is wrong.

## Stdlib-only

The package has no third-party dependencies. It does not import from
`physics_guard/`, `calibration/`, or any of the vendored subtrees; the
invariant in `tests/test_bridges.py::ImportDirectionInvariant` is
respected by construction.
