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
4. **Off-vehicle energy displacement** — moving fuel, dispatch, customer
   service, diagnostics, and roadside response into remote operations
   centers that aren't counted in the truck's TCO.
5. **Lifecycle mismatch** — depreciating equipment over 7 years against
   shale wells that lose 70-80% of flow in year one.

Each of these is encoded as a numbered claim (C001-C013) with a measurable
threshold and a single-sentence falsifier sufficient to refute it.

## Claims at a glance

See `CLAIM_TABLE.json` for the full machine-readable list.

| ID    | Module                          | Statement (short)                                     |
|-------|--------------------------------|--------------------------------------------------------|
| C001  | scope_geometry                  | ROI requires fixed depot-to-destination geometry      |
| C002  | embedded_labor_audit            | Wellsite labor not automated by haul automation       |
| C003  | infrastructure_precondition     | Infra capex > vehicle capex for dispersed wells       |
| C004  | lifecycle_eroi                  | ROI window must exceed well decline curve             |
| C005  | stranded_asset_risk             | Resale to non-consolidated operators -> zero          |
| C006  | scope_collapse_detector         | "Automation" framing collapses labor categories       |
| C007  | scope_collapse_detector         | Threat narrative correlates with wage suppression     |
| C008  | condition_monitoring_audit      | Driver monitoring is unpriced infrastructure          |
| C009  | condition_monitoring_audit      | Sensor replacement introduces new failure modes       |
| C010  | condition_monitoring_audit      | Roadside breakdown cost scales nonlinearly            |
| C011  | interface_labor_audit           | Driver-mediated interfaces are unpriced flexibility   |
| C012  | interface_labor_audit           | Energy cost shifted off-vehicle, off-TCO              |
| C013  | interface_labor_audit           | Driver adaptation is unpriced general problem-solving |

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
│   ├── embedded_labor_audit.py           # C002, C006
│   ├── lifecycle_eroi.py                 # C004
│   ├── stranded_asset_risk.py            # C005
│   ├── condition_monitoring_audit.py     # C008, C009, C010
│   ├── scope_collapse_detector.py        # C006, C007
│   └── interface_labor_audit.py          # C011, C012, C013
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
python automation_scope_audit/modules/condition_monitoring_audit.py
python automation_scope_audit/modules/interface_labor_audit.py
```

## Default numbers

Default unit costs, retention curves, sensor cost envelopes, and off-vehicle
energy stacks are 2025 US dollar / SI joule conservative estimates. Each
constant is exposed at module scope so callers can override with audited
data when available — the framework is the load-bearing piece, the numbers
are placeholders.

## Falsification

Every claim publishes a single-sentence falsifier. A claim is *retired*
when a primary source produces evidence matching that falsifier; until
then the claim survives. The works case (`kodiak_atlas_permian.py`)
deliberately satisfies the threshold for C001, C003, and C004 to show
that the framework does not auto-reject every deployment; the fails case
(`dispersed_wellsite.py`) shows which claims register simultaneously when
the geometry is wrong.

## Stdlib-only

The package has no third-party dependencies. It does not import from
`physics_guard/`, `calibration/`, or any of the vendored subtrees; the
invariant in `tests/test_bridges.py::ImportDirectionInvariant` is
respected by construction (vendored code is not imported here at all).
