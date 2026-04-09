# Dynamic CPI-R transfer from Mathematic-economics

This folder contains the newly added CPI and inflation-weighting materials transferred from `Mathematic-economics` into the Thermodynamic Accountability Framework repository. The transfer preserves the files, but it also separates them by maturity so the target repository remains organized and transparent about what is runnable versus what is still exploratory.

| Path | Status | Purpose |
|---|---|---|
| `code/dynamic_cpi_indicator.py` | Working | A refactored Dynamic CPI-R estimator with synthetic data generation, adaptive weighting logic, a backtest runner, payload generation, and an optional Flask app factory. |
| `code/test_dynamic_cpi_indicator.py` | Working | A lightweight executable validation script for the refactored module. |
| `drafts/dynamic_inflation_weight.py` | Draft / incomplete | An earlier or more schematic inflation-weighting prototype with multiple unresolved references. |
| `drafts/iteration_module.py` | Draft fragment | An extension fragment intended to augment `DynamicCPI_R`, but not usable on its own. |
| `examples/api.json` | Generated example payload | An example JSON payload now regenerated from the working module rather than maintained as a manual placeholder. |
| `AUDIT.md` | Audit note | Summary of the original transfer audit and file readiness assessment. |

The separation is intentional. The target repository conventions reserve `core/` for standard-library modules and use documentation areas for theory and structured archival material. Because these transferred files are economics-focused and still experimental rather than framework-core modules, they remain under `docs/economics/dynamic_cpi_r/` even after the refactor.

## Running the implementation

The working module can now be executed directly from the repository root.

| Command | Purpose |
|---|---|
| `python3 docs/economics/dynamic_cpi_r/code/dynamic_cpi_indicator.py` | Runs the synthetic backtest and refreshes `examples/api.json`. |
| `python3 docs/economics/dynamic_cpi_r/code/test_dynamic_cpi_indicator.py` | Runs the lightweight validation checks. |

## Remaining limitations

| Area | Current limitation | Why it matters |
|---|---|---|
| Data inputs | The current implementation uses synthetic price, weight, credit, and rent-anchor series. | It demonstrates functioning logic, but it is not yet connected to live or historical external datasets. |
| Package placement | The module remains in the documentation area rather than a formal importable package path. | This preserves repository organization, but production promotion would require a clearer package boundary. |
| API layer | The Flask app is optional and factory-based, but it is not yet wired into a persistent service or deployment path. | The code can expose payloads, but it is not yet a full operational endpoint. |
| Research status | The draft files are preserved separately and have not been promoted into the working module. | This keeps provenance clear, but some prototype ideas still need explicit evaluation before adoption. |

The next recommended step is to connect the estimator to real input series, then decide whether it should remain a documented research artifact or be promoted into a first-class framework module.
