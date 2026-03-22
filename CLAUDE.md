# CLAUDE.md

## Project Overview

This is an academic research repository applying mathematical and thermodynamic frameworks to economic analysis. The core thesis is that economic systems should be analyzed mathematically (measuring energy flows, time allocation, and physical constraints) rather than through semantic labels that obscure structural realities.

**License:** CC0 1.0 Universal (public domain)

## Repository Structure

```
Mathematic-economics/
├── AI/                                 # Computational models (Python/PyTorch)
│   ├── money-free-model.py             # Economic accounting without monetary proxies
│   ├── semantic-decontamination.py     # Intercept semantically-contaminated tokens for NLP
│   ├── temporal-energy.py              # Labor as time-energy flow with physics constraints
│   ├── atomic-thermodynamic-accounting.md
│   ├── hidden-critical-factors.md
│   ├── money.md
│   └── work.md
├── Space-Kessler/                      # Orbital mechanics / risk analysis
│   ├── coupled-risk.py                 # Subsystem coupling risk model
│   └── time-evolve-3d.py              # 3D temporal evolution simulation
├── README.md                           # Core thesis with 13 equations and composite indices
├── navigation.md                       # Reading guide for different audiences
├── paradox.md                          # Contradictions in economic definitions
├── analysis.md                         # Economic analysis
├── addendum-1.md - addendum-3.md       # Extended analysis documents
├── ideology-thermodynamics.md          # Thermodynamic lens on social systems
├── thermodynamic-governance.md         # Governance and labor analysis
├── signal-distortion.md                # Signal/distortion concepts
├── LICENSE                             # CC0 1.0
└── trust.html                          # Placeholder
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

### AI/money-free-model.py
Complete economic accounting without monetary proxies. Key classes: `PhysicalConstraints`, `ResourceDepletion`, `EnergyLedger`. Tracks energy flows and sustainability (regeneration minus extraction).

### AI/semantic-decontamination.py
Intercepts and decomposes semantically-contaminated tokens. Uses `PowerPosition` and `CulturalFramework` enums for context-dependent token multiplexing. Designed to sit between NLP input and embedding layers.

### AI/temporal-energy.py
Models labor as time-energy flow under physics constraints. Key classes: `TemporalConstraints`, `ActivityCost`, `EnergyBalanceLayer` (custom PyTorch loss). Enforces conservation laws in economic modeling.

### Space-Kessler/coupled-risk.py
Risk analysis for orbital debris scenarios. Models subsystem coupling across debris states, maneuver loads, and solar activity.

### Space-Kessler/time-evolve-3d.py
3D temporal evolution simulation for orbital mechanics.

## Code Conventions

### Python Style
- **Type hints** throughout (modern Python 3.7+ style)
- **Dataclasses** (`@dataclass`) for configuration and data objects
- **Enums** for state machines and categorical values
- **PyTorch `nn.Module`** subclasses for custom layers and loss functions
- **snake_case** for variables and functions
- **PascalCase** for classes
- **kebab-case** for file names
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
python AI/money-free-model.py
python AI/temporal-energy.py
python Space-Kessler/coupled-risk.py
```

There are no linting or formatting configurations. No `requirements.txt` or `pyproject.toml` exists — install dependencies manually if needed:

```bash
pip install torch numpy pandas matplotlib
```

## Key Concepts for AI Assistants

1. **Thermodynamic grounding:** All economic models are rooted in physical constraints (energy conservation, time limits, biological needs). Do not introduce abstractions that violate these.
2. **Semantic decontamination:** A central thesis is that economic terminology carries ideological bias. When working with this codebase, preserve the distinction between physical measurement and semantic labeling.
3. **13 core equations** are defined in README.md (VE/VL, SID, RI, DI, LWR, MSI, BSC, MM, ISR, UFR, ER, HHI, SD) with composite index OSDI.
4. **No monetary proxies:** The money-free-model explicitly avoids using money as a unit of account, instead tracking energy, time, and physical resources directly.
5. **Reading entry points:** Start with README.md for the thesis, navigation.md for guided reading paths, then explore specific topics.

## Working with This Repository

- **Adding new models:** Place Python implementations in `AI/`. Follow existing patterns: dataclasses for config, type hints, PyTorch for computational graphs, comments explaining physical constraints.
- **Adding analysis documents:** Place Markdown files in the root directory. Use structured headers and include both formal equations and plain English explanations.
- **Space/orbital work:** Place in `Space-Kessler/`.
- **Do not** introduce package management or build tooling unless explicitly requested — the repository is intentionally lightweight.

## Known Fixes Applied (2026-03-22)

All three `AI/` Python scripts had identical structural issues from markdown-to-Python conversion:

- **Embedded markdown fences:** Stray `` ``` `` lines throughout the files (removed)
- **Broken `__name__` guard:** `if **name** == "**main**":` → `if __name__ == "__main__":`
- **Smart quotes:** Unicode `\u201c`/`\u201d`/`\u2019` used as string delimiters → ASCII `"`
- **Indentation:** Class/method bodies at module-level indentation → properly nested
- **money-free-model.py specific:**
  - `depletion_rate` renamed to `regeneration_rate` (variable held regeneration data)
  - Fixed matmul dimension mismatch in `CausalDependencyGraph` (added `resource_to_needs` projection)
  - Fixed `collapse_timeline_days` key reference → `sustainability_timeline_days`
  - Fixed `torch.tensor()` copy-construct warnings
  - Fixed `.item()` call on multi-element tensor in print output

All three scripts now run cleanly: `python AI/money-free-model.py`, `python AI/semantic-decontamination.py`, `python AI/temporal-energy.py`.
