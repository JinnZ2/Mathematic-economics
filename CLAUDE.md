# CLAUDE.md

## Project Overview

This is an academic research repository applying mathematical and thermodynamic frameworks to economic analysis. The core thesis is that economic systems should be analyzed mathematically (measuring energy flows, time allocation, and physical constraints) rather than through semantic labels that obscure structural realities.

**License:** CC0 1.0 Universal (public domain)

## Repository Structure

```
Mathematic-economics/
├── AI/                             # Computational models (Python/PyTorch)
│   ├── Money-free-model.py         # Economic accounting without monetary proxies
│   ├── Semantic-decontamination.py # Intercept semantically-contaminated tokens for NLP
│   ├── Temporal-energy.py          # Labor as time-energy flow with physics constraints
│   ├── Atomic-thermodynamic-accounting.md
│   ├── Hidden-critical-factors.md
│   ├── Money.md
│   └── Work.md
├── Space-Kessler/                  # Orbital mechanics / risk analysis
│   ├── Coupled_risk.py             # Subsystem coupling risk model
│   └── Time-evolve-3d.py           # 3D temporal evolution simulation
├── README.md                       # Core thesis with 13 equations and composite indices
├── Navigation.md                   # Reading guide for different audiences
├── Paradox.md                      # Contradictions in economic definitions
├── Analysis.md                     # Economic analysis
├── Addendum1.md - Addendum3.md     # Extended analysis documents
├── Ideology-thermodynamics.md      # Thermodynamic lens on social systems
├── Thermodynamic-governance.md     # Governance and labor analysis
├── Signal-distortion.md            # Signal/distortion concepts
├── LICENSE                         # CC0 1.0
└── Trust.html                      # Placeholder
```

## Languages and Dependencies

**Primary languages:** Python 3.7+, Markdown

**Python dependencies (no requirements.txt — import directly):**
- `torch` / `torch.nn` — PyTorch for computational graphs and custom layers
- `numpy` — numerical computing
- `pandas` — data manipulation
- `matplotlib` — visualization
- Standard library: `typing`, `dataclasses`, `enum`, `itertools`

## Key Python Modules

### AI/Money-free-model.py (622 lines)
Complete economic accounting without monetary proxies. Key classes: `PhysicalConstraints`, `ResourceDepletion`, `EnergyLedger`. Tracks energy flows and sustainability (regeneration minus extraction).

### AI/Semantic-decontamination.py (723 lines)
Intercepts and decomposes semantically-contaminated tokens. Uses `PowerPosition` and `CulturalFramework` enums for context-dependent token multiplexing. Designed to sit between NLP input and embedding layers.

### AI/Temporal-energy.py (479 lines)
Models labor as time-energy flow under physics constraints. Key classes: `TemporalConstraints`, `ActivityCost`, `EnergyBalanceLayer` (custom PyTorch loss). Enforces conservation laws in economic modeling.

### Space-Kessler/Coupled_risk.py (63 lines)
Risk analysis for orbital debris scenarios. Models subsystem coupling across debris states, maneuver loads, and solar activity.

### Space-Kessler/Time-evolve-3d.py (82 lines)
3D temporal evolution simulation for orbital mechanics.

## Code Conventions

### Python Style
- **Type hints** throughout (modern Python 3.7+ style)
- **Dataclasses** (`@dataclass`) for configuration and data objects
- **Enums** for state machines and categorical values
- **PyTorch `nn.Module`** subclasses for custom layers and loss functions
- **Snake_case** for variables and functions
- **PascalCase** for classes
- **Descriptive names** emphasizing physical/thermodynamic meaning
- Comments explain **why** (thermodynamic limits, physical constraints), not just what

### Documentation Style
- Markdown with structured headers and `---` section dividers
- Mathematical equations in code blocks
- Real-world examples with numerical calculations
- Plain English explanations alongside formal notation

## Build and Test

**No formal build system, test suite, or CI/CD pipeline.** This is a research repository — scripts are meant to be run directly or imported for analysis:

```bash
python AI/Money-free-model.py
python AI/Temporal-energy.py
python Space-Kessler/Coupled_risk.py
```

There are no linting or formatting configurations. No `requirements.txt` or `pyproject.toml` exists — install dependencies manually if needed:

```bash
pip install torch numpy pandas matplotlib
```

## Key Concepts for AI Assistants

1. **Thermodynamic grounding:** All economic models are rooted in physical constraints (energy conservation, time limits, biological needs). Do not introduce abstractions that violate these.
2. **Semantic decontamination:** A central thesis is that economic terminology carries ideological bias. When working with this codebase, preserve the distinction between physical measurement and semantic labeling.
3. **13 core equations** are defined in README.md (VE/VL, SID, RI, DI, LWR, MSI, BSC, MM, ISR, UFR, ER, HHI, SD) with composite index OSDI.
4. **No monetary proxies:** The Money-free-model explicitly avoids using money as a unit of account, instead tracking energy, time, and physical resources directly.
5. **Reading entry points:** Start with README.md for the thesis, Navigation.md for guided reading paths, then explore specific topics.

## Working with This Repository

- **Adding new models:** Place Python implementations in `AI/`. Follow existing patterns: dataclasses for config, type hints, PyTorch for computational graphs, comments explaining physical constraints.
- **Adding analysis documents:** Place Markdown files in the root directory. Use structured headers and include both formal equations and plain English explanations.
- **Space/orbital work:** Place in `Space-Kessler/`.
- **Do not** introduce package management or build tooling unless explicitly requested — the repository is intentionally lightweight.
