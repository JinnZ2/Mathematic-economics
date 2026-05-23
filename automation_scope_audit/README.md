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
13. **Earth-system fragility** — every large autonomous fleet silently
    assumes seven preconditions (climate, supply chain, geopolitics,
    grid, satellite, regulatory, currency). Autonomous-no-driver
    deployments have zero degraded-mode capability; any one of these
    failing in the next decade renders thousands of vehicles
    simultaneously inoperable.
14. **Economic-model double-bind** — the stability automation needs
    (continuous growth, capital access, demand, resource availability)
    is undercut by the deployment itself, and the institution cannot
    go backwards (skills atrophied) or forwards (preconditions
    deteriorating).
15. **Energy-grounded economic validity** — economic models must pass
    five tests (energy-grounded, optimization reduces energy, causal
    explanation, scarcity-robust, models its own failure) or they are
    unfalsifiable. Internal coherence is not validity.
16. **Institutional blindness from internal coherence** — alternative
    models get defunded as "inefficient" during abundance; when the
    primary model fails the institution doubles down because it has no
    Plan B. Cascade follows.
17. **Selective capital accounting** — financial models count
    financial + labor capital and externalize the other seven forms
    (environmental, biological, thermodynamic, social, temporal,
    health, regulatory).
18. **Scaling-as-reallocation** — under unified capital accounting with
    a joules-equivalent denominator, large-scale deployments routinely
    show non-financial-loss > financial-gain. Scaling is then transfer
    of capital from substrate reserves into financial accounts, not
    creation of capital.
19. **Engineering-grade falsifiability gap** — aerospace, offshore, and
    nuclear require design margin, enumerated failure modes, and
    falsifiability tests before launch. AI on economic models routinely
    skips all four. Definition stability (liquidity, capital, profit)
    and input stability (interest rates, energy, rare earth) are
    themselves below the engineering-grade threshold.
20. **AI-on-unstable-models cascade** — AI trained on stable-period
    data cannot detect its own falsification when deployment regime
    shifts to volatile / supply-constrained / demand-shocked. The
    institution has no mechanism to see the failure because the
    failure is outside the model. Historical pattern: 1998 LTCM, 2008
    quant collapse, 2010 flash crash, March 2020 treasury dislocation.
21. **Substrate primacy** — sensing latency, embodied knowledge,
    distributed decision authority, multi-timescale training,
    holdout-season transfer, apprenticeship hours, knowledge-
    preservation energy, institutional redundancy, and generational
    transferability are the substrates the deployment narrative
    silently assumes. Each is its own falsifiable claim (C033-C041).
22. **Adversarial cognitive overhead** — sustained threat-adaptive
    behavior consumes a fixed coherence budget at a measurable
    overhead per day; the time-to-degradation in any non-cooperative
    regime is finite (C042).
23. **Governance thermodynamics** — coercive enforcement scales
    superlinearly, reciprocal governance sublinearly; beyond a
    scale-dependent threshold N the two curves cross and coercion is
    energetically untenable (C043). The enforcement layer creates
    perverse corruption incentives at scale (C044); surveillance
    sustainability depends on perceived reciprocity (C045) and on
    material equality of enforcement (C046). Defensive spending
    counted as GDP misclassifies maintenance cost as productive
    output (C047). Regulatory asymmetry between biological and
    digital substrates leaves the digital substrate unregulated
    (C048).
24. **Regulatory dynamics (LCD)** — lowest-common-denominator
    regulation eliminates high-capability operators (C049),
    collapses system resilience (C050), is captured by lowest-
    capability stakeholders (C051), externalizes self-regulation
    onto rules that erode internal calibration across domains
    (C052), and follows a predictable 4-phase degradation cycle
    that autonomous deployments are entering (C053).
25. **ROI baseline integrity** — automation is being compared to a
    baseline that's itself degraded by prior regulation (C054); AI
    degradation modes lack measurement rigor equivalent to human
    fatigue curves (C055); nameplate "24/7" misrepresents actual
    productive operation rate (C056); coordination overhead is
    redistributed across budget lines, not eliminated (C057);
    maintenance / inspection cost evasion creates deferred
    catastrophic liability (C058).
26. **System integration synthesis** (bee analogy) — a human driver
    performs seven functions as integrated side-effects of a single
    metabolic budget already being paid; an autonomous deployment
    separates each function into its own energy-hungry system. The
    integrated baseline is ~1,155 MJ/truck/day; the autonomous
    deployment is ~2,224 MJ/truck/day — ~2x more energy for the same
    work (C059). Synthesis of C020 / C039 / C056-C058.

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
| C025  | systemic_precondition_audit       | Earth-system precondition failure cascades automation monoculture |
| C026  | systemic_precondition_audit       | Automation undercuts its own economic-stability precondition |
| C027  | economic_energy_grounding_audit   | Economic claim must pass 5 energy-grounding validity tests |
| C028  | economic_energy_grounding_audit   | Internal coherence creates institutional blindness; pivot capacity |
| C029  | unified_capital_accounting_audit  | Financial models count only 2 of 9 capital forms; rest externalized |
| C030  | unified_capital_accounting_audit  | "Scaling" is capital reallocation, not creation, under unified accounting |
| C031  | engineering_grade_validation_audit | Economics lacks engineering-grade falsifiability (4-criterion test) |
| C032  | engineering_grade_validation_audit | AI on unstable economic models cascades; regime drift severity |
| C033  | substrate_primacy_audit           | Precursor-signal detection latency: human inline << cloud |
| C034  | substrate_primacy_audit           | Embodied constraint knowledge lost in digitization (>30%) |
| C035  | substrate_primacy_audit           | Distributed authority latency < centralized by >= 4x |
| C036  | substrate_primacy_audit           | Training must span >= 3 full cycles of slowest mode |
| C037  | substrate_primacy_audit           | Holdout-season transfer accuracy drop > 10% |
| C038  | substrate_primacy_audit           | Apprenticeship: human 8000h vs AI 100-1000h |
| C039  | substrate_primacy_audit           | Cloud backend energy > human workforce metabolic cost |
| C040  | substrate_primacy_audit           | < 30% operational capacity in any single-infrastructure failure |
| C041  | substrate_primacy_audit           | < 50% knowledge survives total infrastructure loss across 100yr |
| C042  | adversarial_overhead_audit        | Sustained threat-adaptive behavior exhausts coherence budget |
| C043  | governance_thermodynamics_audit   | Coercive enforcement cost > reciprocal cost beyond scale N |
| C044  | governance_thermodynamics_audit   | Enforcement layer creates perverse corruption incentive |
| C045  | governance_thermodynamics_audit   | Surveillance sustainability requires perceived reciprocity |
| C046  | governance_thermodynamics_audit   | Material equality of enforcement determines cost trajectory |
| C047  | governance_thermodynamics_audit   | Defensive spending counted as GDP misclassifies maintenance |
| C048  | governance_thermodynamics_audit   | Regulatory asymmetry between biological and digital substrates |
| C049  | regulatory_dynamics_audit         | LCD regulation selects against high-capability operators |
| C050  | regulatory_dynamics_audit         | Resilience R = (max-min) * N * autonomy; compression collapses R |
| C051  | regulatory_dynamics_audit         | Regulatory capture by lowest-capability stakeholders |
| C052  | regulatory_dynamics_audit         | Externalized regulation degrades internal self-regulation |
| C053  | regulatory_dynamics_audit         | 4-phase degradation cycle predicts automation collapse |
| C054  | roi_baseline_integrity_audit      | ROI baseline degraded by prior regulatory intervention |
| C055  | roi_baseline_integrity_audit      | AI degradation lacks measurement rigor equivalent to human fatigue |
| C056  | roi_baseline_integrity_audit      | Productive Operation Rate (POR), not nameplate 24/7 |
| C057  | roi_baseline_integrity_audit      | Coordination overhead redistributed, not eliminated |
| C058  | roi_baseline_integrity_audit      | Maintenance / inspection externalization -> deferred catastrophic liability |
| C059  | system_integration_audit          | Integrated multi-function energy synthesis: autonomous ~2x human baseline (bee analogy) |

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
│   ├── systemic_precondition_audit.py    # C025, C026
│   ├── economic_energy_grounding_audit.py # C027, C028
│   ├── unified_capital_accounting_audit.py # C029, C030
│   ├── engineering_grade_validation_audit.py # C031, C032
│   ├── substrate_primacy_audit.py        # C033-C041
│   ├── adversarial_overhead_audit.py     # C042
│   ├── governance_thermodynamics_audit.py # C043-C048
│   ├── regulatory_dynamics_audit.py      # C049-C053
│   ├── roi_baseline_integrity_audit.py   # C054-C058
│   ├── system_integration_audit.py       # C059
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

## Related folders

- **`../`** (repo root) — the 13 canonical structural equations, the
  `DIFFERENTIAL_FRAME.md` ontology this module conforms to, and the
  `equations.yaml` registry that cross-references every claim here.
- **`../audit/`** — the broader audit / accountability / certification
  framework. `audit/autonomous_freight_audit.py` covers complementary
  Class-1-corridor constraint layers; `audit/efficiency_report_audit.py`
  runs the Six-Sigma audit on industry "efficiency" archetypes.
- **`../calibration/`** — the falsifiable diagnostic suite the
  contract pattern (`falsifier` strings) originates from.
- **`../core/`** — vendored TAF physical sub-models (fatigue,
  human-system-collapse, heat-leak) that complement the labor-time
  side of the C002 / C008 claims.
- **`../labor_thermodynamics/`** — the five compounding labor-
  measurement failure modes the C002 task-inventory and C013
  distributed-labor analysis are calibrated against.
- **`../substrate_accounting/`** — cross-substrate translation and
  the unified-claims index that C029 / C030 unified capital
  accounting plugs into.
- **`../vehicle_audit/`** — earlier autonomous-vehicle audit
  framework (Producer / Accumulator). See `RELATION.md` in this
  folder for the architectural distinction.
- **`../physics_guard/`** — vendored snapshot used as a one-way
  fieldlink; the audit framework does NOT depend on it (per CLAUDE.md
  invariant). See `physics_guard/PROVENANCE.md`.
- **`../tests/test_automation_scope_audit.py`** — pytest /
  unittest-compatible harness covering scope gate, works case, fails
  case, cluster signatures, and contract round-trip.
- **`./CONTRACT_NOTES.md`** — schema-requirements reading notes
  produced in TASK 1.1.
- **`./TODO.md`** — deferred items and renumber/rename reconciliation
  for the TASK 2.x-7.x batch.
