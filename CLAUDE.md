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
│   └── system_audit.py                 # Six Sigma-style audit on field_system outputs
├── data/                               # External data fetch + sensitivity analysis
│   ├── fetch_and_compute.py
│   ├── sensitivity_analysis.py
│   └── plots/                          # Generated figures (PNG)
├── docs/
│   └── economics/
│       └── dynamic_cpi_r/              # Dynamic CPI-R estimator (the "-R" suffix is the metric name)
│           ├── code/                   # Working module + validation script
│           ├── drafts/                 # Earlier prototype fragments
│           └── examples/               # Generated API payload
├── README.md                           # Core thesis with 13 equations and composite indices
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
```

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

- **Adding computational models:** Place in `AI/`. Follow existing patterns: dataclasses for config, type hints, PyTorch for computational graphs, comments explaining physical constraints.
- **Adding audit / protocol scripts:** Place in `audit/`. These are standard-library Python modules that can import each other directly.
- **Adding data ingestion or sensitivity analysis:** Place in `data/`.
- **Adding analysis essays:** Place Markdown files in the root directory.
- **Space / orbital work:** Place in `Space-Kessler/`.
- **Do not** introduce package management or build tooling unless explicitly requested — the repository is intentionally lightweight.
