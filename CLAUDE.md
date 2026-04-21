# CLAUDE.md

## Project Overview

This is an academic research repository applying mathematical and thermodynamic frameworks to economic analysis. The core thesis is that economic systems should be analyzed mathematically (measuring energy flows, time allocation, and physical constraints) rather than through semantic labels that obscure structural realities.

**License:** CC0 1.0 Universal (public domain)

## Repository Structure

```
Mathematic-economics/
├── AI/                                 # Computational models (Python / PyTorch)
│   ├── money_free_model.py             # Economic accounting without monetary proxies
│   ├── semantic_decontamination.py     # Intercept semantically-contaminated tokens for NLP
│   ├── temporal_energy.py              # Labor as time-energy flow with physics constraints
│   ├── equation_bridge.py              # Maps AI/ models to the 13 structural equations
│   ├── atomic-thermodynamic-accounting.md
│   ├── hidden-critical-factors.md
│   ├── money.md
│   └── work.md
├── Space-Kessler/                      # Orbital mechanics / risk analysis
│   ├── coupled_risk.py                 # Subsystem coupling risk model
│   └── time_evolve_3d.py               # 3D temporal evolution simulation
├── audit/                              # Accountability, certification, and audit protocols
│   ├── accountability_protocol.py
│   ├── ai_delusion_econ_checker.py     # Detect systemic assumptions in AI datasets
│   ├── certification_protocol.py
│   ├── deflection_pattern_analyzer.py
│   ├── efficiency_report_audit.py      # Audits industry "efficiency" report archetypes
│   ├── epistemic_cascade.py
│   ├── field_system.py                 # Rule-field engine used by system_audit
│   ├── implementation_layer.py
│   ├── incentive_structure.py
│   ├── incentives_audit.py
│   ├── metabolic_bridge.py             # Defensive bridge to JinnZ2/metabolic-accounting
│   ├── money_signal_bridge.py          # Defensive bridge to money_signal/ subsystem
│   ├── investment_signal_bridge.py     # Defensive bridge to investment_signal/ subsystem
│   └── system_audit.py                 # Six Sigma-style audit on field_system outputs
├── calibration/                        # Falsifiable diagnostics + falsification test suite (stdlib only)
│   ├── schema.py                       # Band / DimensionScore / CalibrationReport
│   ├── calibration_audit.py            # Q1-Q5 bite/skin/witness/memorialization/friction
│   ├── observation_dependence.py       # Witness-dependence coefficient
│   ├── adaptation_debt.py              # Friction removal -> stored fragility
│   ├── architecture_mismatch.py        # Language-primary vs substrate-primary cognition
│   ├── pipeline.py                     # Unified audit across calibration modules
│   ├── self_audit.py                   # Self-referential repo audit
│   └── test_calibration.py             # 11 falsification tests
├── core/                               # Vendored TAF physical / diagnostic sub-models (stdlib only)
│   ├── fatigue_model.py                # 0-10 fatigue from load vs. energy input
│   ├── human_system_collapse_model.py  # Distance-to-collapse at 120/140/160% thresholds
│   ├── data_logger.py                  # Parasitic energy-debt ledger
│   ├── automation_assessment.py        # Interactive hidden-variable entropy probe
│   ├── heat_leak_case.py               # Institutional friction / energy-loss detector
│   └── integrations/
│       └── biological_extraction_model.py  # Substrate-agnostic extraction physics
├── physics_guard/                      # Vendored PhysicsGuard snapshot (see PROVENANCE.md)
│   ├── core/                           # premise_parser -> constraint_mapper -> conservation_checker -> flag_engine
│   ├── domains/                        # organizational, information (Landauer, Shannon bound, etc.)
│   ├── tests/                          # 76 pytest tests
│   ├── main.py, ai_interface.py, monoculture_detector.py
│   └── PROVENANCE.md                   # Snapshot metadata and integration points
├── tests/                              # Integration tests across the three PhysicsGuard bridges
│   └── test_bridges.py                 # 10 unittest tests (6 always, 4 require numpy)
├── schemas/                            # Versioned data contracts for inter-module shapes
│   ├── __init__.py
│   └── field_system_contract.py        # Stable shape for field_system state / report
├── data/                               # External data fetch + sensitivity analysis
│   ├── fetch_and_compute.py
│   ├── sensitivity_analysis.py
│   └── plots/                          # Generated figures (PNG)
├── labor_thermodynamics/               # Markdown specs for the five labor-measurement failure modes
│   ├── README.md
│   ├── failure_modes.md
│   └── measurement_problem.md
├── docs/
│   └── economics/
│       └── dynamic_cpi_r/              # Dynamic CPI-R estimator (the "-R" suffix is the metric name)
│           ├── code/                   # Working module + validation script
│           ├── drafts/                 # Earlier prototype fragments
│           └── examples/               # Generated API payload
├── README.md                           # Core thesis with 13 equations and composite indices
├── SURFACE.md                          # Stable surface declaration for downstream pinning (tag: equations-v1)
├── navigation.md                       # Reading guide for different audiences
├── paradox.md                          # Contradictions in economic definitions
├── analysis.md                         # Economic analysis
├── structural-analysis.md              # Structural analysis of the framework
├── addendum-1.md … addendum-3.md       # Extended analysis documents
├── ideology-thermodynamics.md          # Thermodynamic lens on social systems
├── thermodynamic-governance.md         # Governance and labor analysis
├── signal-distortion.md                # Signal / distortion concepts
├── equations.yaml                      # Machine-readable definitions of the 13 equations
└── LICENSE                             # CC0 1.0
```

## Languages and Dependencies

**Primary languages:** Python 3.7+, Markdown

**Python dependencies (no requirements.txt — install manually):**
- `torch` / `torch.nn` — PyTorch for computational graphs and custom layers (used in `AI/`)
- `numpy` — numerical computing
- `pandas` — data manipulation
- `matplotlib` — visualization
- `scipy` — used by `docs/economics/dynamic_cpi_r/drafts/dynamic_inflation_weight.py`
- Standard library: `typing`, `dataclasses`, `enum`, `itertools`, `hashlib`, `json`, `re`, `collections`

## Key Python Modules

### AI/money_free_model.py
Economic accounting without monetary proxies. Key classes: `PhysicalConstraints`, `ResourceDepletion`, `EnergyLedger`. Tracks energy flows and sustainability (regeneration minus extraction).

### AI/semantic_decontamination.py
Intercepts and decomposes semantically-contaminated tokens. Uses `PowerPosition` and `CulturalFramework` enums for context-dependent token multiplexing. Designed to sit between NLP input and embedding layers.

### AI/temporal_energy.py
Models labor as time-energy flow under physics constraints. Key classes: `TemporalConstraints`, `ActivityCost`, `EnergyBalanceLayer` (custom PyTorch loss). Enforces conservation laws in economic modeling.

### AI/equation_bridge.py
Connects the `AI/` computational models to the 13 structural equations from `README.md`, mapping physical measurements to economic structure equations.

### Space-Kessler/coupled_risk.py
Risk analysis for orbital debris scenarios. Models subsystem coupling across debris states, maneuver loads, and solar activity.

### Space-Kessler/time_evolve_3d.py
3D temporal evolution simulation for orbital mechanics.

### audit/field_system.py
Minimal rule-field engine for regenerative system tracking: constraints, drift detection, adaptive suggestions, effective yield with ecological coupling. Imported by `system_audit.py` and `efficiency_report_audit.py`.

### audit/system_audit.py
Six Sigma-style audit on field_system outputs: `SixSigmaAudit` class, defect rate, process capability, thermodynamic efficiency.

### audit/efficiency_report_audit.py
Runs `SixSigmaAudit` against representative 2025-2026 "efficiency breakthrough" report archetypes and compares against a first-principles baseline.

### audit/ai_delusion_econ_checker.py
Regex-based detector for systemic assumptions (hierarchy, corporation, efficiency, optimization, productivity, economics) in text datasets, with plausibility flags.

### core/heat_leak_case.py
Institutional-friction / energy-loss diagnostic (vendored from thermodynamic-accountability-framework). Detects heat leaks and prediction-error patterns across shift-style data. Lives in `core/` alongside the other TAF-originated sub-models so the import-direction invariant test can scan it.

### calibration/
Falsifiable diagnostic suite (ported from thermodynamic-accountability-framework, CC0, stdlib only). Scores systems across five dimensions (bite source, skin-in-game, witness dependence, memorialization, friction removal) and aggregates into GREEN / YELLOW / RED / EXTINCT bands. `test_calibration.py` contains 11 falsification tests that must pass (`python calibration/test_calibration.py`). `self_audit.py` runs the framework against itself to detect propaganda-of-skill drift.

### core/fatigue_model.py, core/human_system_collapse_model.py
Physical sub-models for labor load vs. energy input. `fatigue_model.py` returns a 0-10 fatigue score with hidden-variable / automation / environment multipliers. `human_system_collapse_model.py` converts total load into a distance-to-collapse metric with thresholds at 120 / 140 / 160% of energy input. Both complement `AI/temporal_energy.py` but use stdlib only, so they run without PyTorch.

### core/integrations/biological_extraction_model.py
Substrate-agnostic extraction physics: the same energy-balance accounting applied whether the organism is human, machine, or AI. Supports `AI/semantic_decontamination.py`'s thesis that labels obscure structural realities.

### schemas/field_system_contract.py
`FieldSystemState` + `FieldSystemReport` + `YieldAnalysis` dataclasses mirroring the dict shape consumed and produced by `audit/field_system.py`. Consumers (`system_audit`, `efficiency_report_audit`) can adopt it incrementally for type-checked inputs. Versioned via `CONTRACT_VERSION`.

### labor_thermodynamics/
Markdown specifications for the five compounding labor-measurement failure modes (L1-L5). Sits next to the essay-style analysis files at the repo root; ported from thermodynamic-accountability-framework.

### physics_guard/
Vendored snapshot of [JinnZ2/PhysicsGuard](https://github.com/JinnZ2/PhysicsGuard) (CC0). Physics-grounded claim verification: `core/` pipeline parses a natural-language premise, maps it to a conservation equation, checks imbalance, and emits a scored `Verdict` with an audit trail. `domains/organizational.py` and `domains/information.py` apply the pipeline to structural-resilience and information-theoretic (Landauer, Shannon) constraints. `monoculture_detector.py` analyzes lexical/causal diversity — directly relevant to the HHI concentration metric in `README.md`. 76 pytest tests at snapshot. See `physics_guard/PROVENANCE.md` for snapshot version and integration points.

### PhysicsGuard bridges
Three wiring points connect PhysicsGuard into the existing Math-Econ modules. All three are defensive: they set `_HAS_PHYSICS_GUARD = False` and fall back to the pre-bridge behavior if `physics_guard/` is not importable.

- **`audit/efficiency_report_audit.py`** — `audit_efficiency_report()` now routes each report's headline claim through `physics_guard.main.check()` and attaches the verdict to the return dict under `physics_verdict`. A `CORRUPTED` verdict means the headline is physically impossible regardless of the Six Sigma audit outcome.
- **`audit/ai_delusion_econ_checker.py`** — `analyze_dataset_with_physics()` keeps the existing regex analysis and adds a per-entry PhysicsGuard verdict list. The original `analyze_dataset()` is untouched so downstream callers are unaffected.
- **`AI/equation_bridge.py`** — `SystemMeasurement.check_organizational_physics(node_count, ...)` constructs a `domains.organizational.OrgClaim` from the measured equations (HHI → structure type, ER → enforcement ratio, `1 - ER` → adaptive slack) and returns the `check_organization()` verdict plus audit trail.

### Metabolic-accounting bridge
A fourth bridge wires Math-Econ into [JinnZ2/metabolic-accounting](https://github.com/JinnZ2/metabolic-accounting) (CC0, stdlib-only). Unlike PhysicsGuard, metabolic-accounting is **not vendored** — `audit/metabolic_bridge.py` probes a few conventional locations (`<repo_root>/metabolic_accounting/`, `<parent>/metabolic-accounting/`) and sets `_HAS_METABOLIC_ACCOUNTING = False` if none are found. To activate the bridge, place a checkout in either location.

- **`audit/metabolic_bridge.py`** — exposes `metabolic_check(revenue, direct_operating_cost, regeneration_paid, stress, basin_overrides)` which builds a four-basin `Site`, optionally overrides basin `state[metric]` values to reflect steady-state degradation, applies a single-step stress shock, computes `GlucoseFlow`, and returns a normalized `Verdict` dict (GREEN/AMBER/RED/BLACK in `sustainable_yield_signal`; BLACK = irreversibility, not "very RED"). Two helpers derive the inputs from a Math-Econ `field_system` scenario: `stress_from_field_scenario(scenario)` for shock events, `basins_from_field_scenario(scenario)` for steady-state degradation. Use both together for scenarios like `REPORT_ARCHETYPES` in `efficiency_report_audit.py`: steady-state sets basin damage so `regeneration_debt` and `sustainable_yield_signal` can actually discriminate (AMBER/RED transitions); single-step stress layers reserve-drawdown cost on top of that.
- **`audit/efficiency_report_audit.py`** — `audit_efficiency_report()` now also attaches `metabolic_verdict` to the result dict, alongside `physics_verdict`. Revenue/operating-cost are scaled from the scenario's energy ratio, so absolute profit numbers are not meaningful — but the band signal and basin trajectory are.
- **`AI/equation_bridge.py`** — `SystemMeasurement.check_metabolic_health(revenue, regeneration_paid, stress)` derives operating cost from the measured ER (`operating_cost = revenue * (1 - ER)`) and runs the bridge.

### Money-signal bridge
A fifth bridge fieldlinks Math-Econ into the `money_signal/` subsystem of [JinnZ2/metabolic-accounting](https://github.com/JinnZ2/metabolic-accounting). Same discovery logic as `metabolic_bridge.py` — probes the same conventional locations and sets `_HAS_MONEY_SIGNAL = False` on failure. Deliberately imports only `money_signal.dimensions` and `money_signal.coupling` (leaf modules, zero side effects); skips `money_signal.accounting_bridge` because it mutates `sys.path` at import time and hard-depends on `term_audit/`.

- **`audit/money_signal_bridge.py`** — exposes `default_context()` (neutral `DimensionalContext` baseline) and `money_signal_metrics(ctx=None)` which returns `{"minsky", "magnitude", "has_sign_flips"}` — the three raw primitives that feed upstream's `signal_quality`. Exposing them raw rather than collapsed avoids the `term_audit` dependency and gives callers more information than a single float.
- **`audit/efficiency_report_audit.py`** — `audit_efficiency_report()` attaches `money_signal_metrics` to the result dict, alongside `physics_verdict` and `metabolic_verdict`.
- **`AI/equation_bridge.py`** — `SystemMeasurement.check_money_signal(ctx=None)` forwards to the bridge.

### Investment-signal bridge
A sixth bridge fieldlinks Math-Econ into the `investment_signal/` subsystem of metabolic-accounting. Same discovery logic as `metabolic_bridge.py`; sets `_HAS_INVESTMENT_SIGNAL = False` on failure. At the pinned commit upstream uses absolute imports (`from money_signal.coupling import ...`) and ships an `__init__.py`, so no shim is needed — flat imports work. Earlier upstream commits lacked these, which is why the bridge landed separately from money_signal.

- **`audit/investment_signal_bridge.py`** — exposes `default_money_context()` / `default_investment_context()` (neutral `DimensionalContext` + `InvestmentContext` baselines) and `investment_signal_metrics(input_money, expected_output_money, ctx=None)` which builds two money-only `SubstrateVector`s (zeros across the other six substrates), calls `assemble_investment_signal`, and returns a plain dict with the 17 fields most useful for judgment (`time_binding_integrity`, `derivative_signal_reliability`, `money_minsky`, `is_financialized`, `substrate_invisible`, `dependency_broken`, `failure_count`, `failure_reasons`, etc.). For non-money substrate mixes, callers should invoke upstream's `assemble_investment_signal` directly.
- **`AI/equation_bridge.py`** — `SystemMeasurement.check_investment_signal(input_money, expected_output_money, ctx=None)` forwards to the bridge.

### tests/test_bridges.py
27 unittest tests verifying all six bridges end-to-end: import wiring, output shape, graceful fallback when any upstream is absent, and correct delegation through `SystemMeasurement` methods. Run with `python tests/test_bridges.py`. The 10 tests covering `equation_bridge` skip automatically in environments without numpy.

### data/fetch_and_compute.py, data/sensitivity_analysis.py
External data ingestion and Monte Carlo sensitivity analysis across weight and threshold ranges for the composite indices defined in `README.md`.

### docs/economics/dynamic_cpi_r/code/dynamic_cpi_indicator.py
Refactored Dynamic CPI-R estimator with synthetic data generation, adaptive weighting, backtest runner, and optional Flask app factory.

## Code Conventions

### Python Style
- **Type hints** throughout (modern Python 3.7+ style)
- **Dataclasses** (`@dataclass`) for configuration and data objects
- **Enums** for state machines and categorical values
- **PyTorch `nn.Module`** subclasses for custom layers and loss functions
- **snake_case** for variables, functions, **and Python filenames** (PEP 8; required so modules are importable by name)
- **PascalCase** for classes
- **Descriptive names** emphasizing physical / thermodynamic meaning
- Comments explain **why** (thermodynamic limits, physical constraints), not just what

### Documentation Style
- Markdown with structured headers and `---` section dividers
- **kebab-case** for Markdown filenames (e.g. `ideology-thermodynamics.md`)
- Mathematical equations in code blocks
- Real-world examples with numerical calculations
- Plain English explanations alongside formal notation

## Build and Test

**No formal build system, test suite, or CI/CD pipeline.** This is a research repository — scripts are meant to be run directly or imported for analysis:

```bash
python AI/money_free_model.py
python AI/temporal_energy.py
python Space-Kessler/coupled_risk.py
python audit/system_audit.py
python audit/efficiency_report_audit.py
python calibration/test_calibration.py   # 11 falsification tests
python calibration/self_audit.py         # repo audits itself

# PhysicsGuard test suite (requires pytest)
cd physics_guard && pytest tests/        # 76 tests

# Integration tests for the three PhysicsGuard bridges
python tests/test_bridges.py             # 10 tests (4 skip without numpy)
```

CI runs all three suites on push / PR via `.github/workflows/tests.yml`.

There are no linting or formatting configurations. No `requirements.txt` or `pyproject.toml` exists — install dependencies manually:

```bash
pip install torch numpy pandas matplotlib scipy
```

Scripts that import sibling modules (e.g. `system_audit` importing `field_system`) are written to be run from their own directory, since the repository is intentionally not packaged.

## Key Concepts for AI Assistants

1. **Thermodynamic grounding:** All economic models are rooted in physical constraints (energy conservation, time limits, biological needs). Do not introduce abstractions that violate these.
2. **Semantic decontamination:** A central thesis is that economic terminology carries ideological bias. When working with this codebase, preserve the distinction between physical measurement and semantic labeling.
3. **13 core equations** are defined in `README.md` (VE/VL, SID, RI, DI, LWR, MSI, BSC, MM, ISR, UFR, ER, HHI, SD) with composite index OSDI, and mirrored machine-readably in `equations.yaml`.
4. **No monetary proxies:** `money_free_model.py` explicitly avoids money as a unit of account, tracking energy, time, and physical resources directly.
5. **Reading entry points:** Start with `README.md` for the thesis, `navigation.md` for guided reading paths, then explore specific topics.

## Working with This Repository

- **Adding PyTorch computational models:** Place in `AI/`. Follow existing patterns: dataclasses for config, type hints, PyTorch for computational graphs, comments explaining physical constraints.
- **Adding stdlib-only physical sub-models:** Place in `core/`. These complement `AI/` but run without PyTorch.
- **Adding audit / protocol scripts:** Place in `audit/`. Standard-library modules that import each other directly.
- **Adding falsifiable diagnostics:** Place in `calibration/`. Every dimension scorer must expose a `falsifier` string describing what input would flip its verdict, and should have a matching test in `test_calibration.py`.
- **Adding inter-module data shapes:** Place a versioned dataclass contract in `schemas/` before the third consumer starts passing the dict around.
- **Adding data ingestion or sensitivity analysis:** Place in `data/`.
- **Adding analysis essays:** Place Markdown files in the root directory (or `labor_thermodynamics/` for labor-specific specs).
- **Space / orbital work:** Place in `Space-Kessler/`.
- **Do not** introduce package management or build tooling unless explicitly requested — the repository is intentionally lightweight.
- **Cross-repo material:** Several modules originated in [`JinnZ2/thermodynamic-accountability-framework`](https://github.com/JinnZ2/thermodynamic-accountability-framework) and [`JinnZ2/PhysicsGuard`](https://github.com/JinnZ2/PhysicsGuard) (both CC0). [`JinnZ2/metabolic-accounting`](https://github.com/JinnZ2/metabolic-accounting) is fieldlinked via `audit/metabolic_bridge.py` (defensive, not vendored). When porting more, keep the `License: CC0` headers intact so provenance is traceable.

## Stable surface tag

The tag **`equations-v1`** is the canonical pinning point for downstream
repositories (e.g. `JinnZ2/thermodynamic-accountability-framework`).  What the
tag covers — and the rules for when to bump it — are declared in `SURFACE.md`
at the repo root.

**Key rules for contributors:**

- **Do not delete or force-move `equations-v*` tags.** Moving a tag is a
  breaking change for every downstream repo that has pinned to it.
- When making a breaking change to any in-scope item (equation name/formula,
  `equations.yaml` keys/units/ranges, `schemas/field_system_contract.py` field
  names/types, HHI/ER conventions), create a new major tag (`equations-v2`,
  …) and update the `surface_version` field in `equations.yaml` metadata.
- When adding a backward-compatible item (new equation, new schema field with a
  default), create a new minor tag (`equations-v1.1`, …) and update
  `surface_version`.
- Calibration knobs (OSDI weights, normalization constants, threshold choices)
  do **not** require a tag bump.

## Invariant: vendored subtrees must not import Math-Econ

Math-Econ has no `requirements.txt` and is not pip-installable — it is
intentionally research code. The vendored subtrees (`physics_guard/`,
`calibration/`, `core/`, `labor_thermodynamics/`) must stay pure so they
can be re-synced from their upstream repos without accidentally pulling
Math-Econ with them.

**Rule:** imports only flow **Math-Econ → vendored**, never **vendored →
Math-Econ**. If you need the reverse direction (vendored code reacting to
Math-Econ state), pass data into the vendored function from a Math-Econ
module instead of importing back.

`tests/test_bridges.py::ImportDirectionInvariant` enforces this via AST
scan of every `.py` file under each vendored subtree, and fails CI if any
of them import a Math-Econ module name.
