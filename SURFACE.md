# Stable Surface Declaration

**Current surface tag:** `equations-v1`

This file declares what is and is not part of the versioned stable surface that
downstream repositories (e.g. `JinnZ2/thermodynamic-accountability-framework`)
can pin to.  The tag `equations-v1` marks the commit at which this surface was
first declared.  Downstream consumers should pin to a named tag rather than
tracking `main`, so that re-syncs are explicit and breakage is visible.

---

## In scope — breaking changes bump the major tag

Changing any item below requires creating a new tag (e.g. `equations-v2`) rather
than moving or deleting the existing one.  **Deleting or force-moving a tag is
itself a breaking change.**

### 13 structural equations (`README.md` / `equations.yaml`)

| ID | Name |
|----|------|
| VE/VL | Value Extraction to Value Labor Ratio |
| SID | Socialist Infrastructure Dependency |
| RI | Resource Independence |
| DI | Democratic Index |
| LWR | Labor-to-Wealth Ratio |
| MSI | Market Structure Index |
| BSC | Basic Security Coverage |
| MM | Market Manipulation |
| ISR | Infrastructure Spending Ratio |
| UFR | Universal Freedom Rating |
| ER | Enforcement Ratio |
| HHI | Herfindahl-Hirschman Index |
| SD | Subsistence Dependency |

Specifically: the **name**, **formula**, and **documented meaning** of each
equation are in scope.  A rename, formula change, or semantic reinterpretation
is a breaking change.

### Composite index OSDI

OSDI aggregates SID, MSI, ISR, BSC, and MM.  The identity of the five
component equations is in scope.  The component weights and normalization
constants are **not** in scope (see below).

### `equations.yaml` — keys, units, and documented ranges

The top-level keys (`id`, `name`, `formula`, `variables`, `range`,
`thresholds`, `data_sources`, `falsification`), the unit strings, and the
documented `range` bounds for each equation are in scope.  The
`surface_version` field in the `metadata` block reflects the current surface
tag and must be updated when a new tag is declared.

### `schemas/field_system_contract.py`

The following are in scope:

- `FieldSystemState` — all 11 field names, their `float` type, and their
  documented ranges.
- `YieldAnalysis` — all 4 field names and their `float` type.
- `FieldSystemReport` — all 6 field names and their declared types.
- `CONTRACT_VERSION` — the existing `"1.0.0"` string; major bumps here
  correspond to major tag bumps.

### HHI and ER conventions

- HHI is expressed in **percentage-point-squared** units with reference
  thresholds at **1500** (moderate concentration) and **2500** (high
  concentration).
- ER range semantics: `[0, 1]` where 0 = no enforcement and 1 = full
  enforcement.

---

## Not in scope — may change without bumping the tag

The items below are calibration knobs or internal implementation details.
Changes to them do **not** require a new surface tag.

- **OSDI component weights** (`SID 0.3`, `MSI 0.2`, `ISR 0.2`, `BSC 0.15`,
  `MM 0.15` in `AI/equation_bridge.py`).
- **Normalization constants** (e.g. `ISR / 20`, `BSC / 5`, `MM / 10`).
- **Threshold choices** classified as "reference points, not empirically
  derived" in `README.md` §Limitations.
- **Internal-only helpers** in `audit/`, `calibration/`, `core/`, and
  `physics_guard/` — these are either vendored snapshots or research-mode
  code.
- **`equations.yaml` prose fields** (`description`, `notes`, `falsification`
  narrative text) — wording may be clarified without a tag bump.

---

## Versioning rules

| Change type | Action |
|-------------|--------|
| Breaking (rename, formula change, field removal, semantic reinterpretation of any in-scope item) | New major tag (`equations-v2`, `equations-v3`, …) |
| Backward-compatible addition (new equation, new field on an existing schema with a default) | New minor tag (`equations-v1.1`, `equations-v1.2`, …) |
| Calibration-knob update (weights, normalization, thresholds) | No tag required |

---

## How downstream repos should pin

```yaml
# Example: reference a specific surface tag in a sibling repo's README or CI
math_econ_surface: equations-v1
math_econ_ref: https://github.com/JinnZ2/Mathematic-economics/tree/equations-v1
```

To detect staleness in CI, compare the pinned tag against the latest
`equations-v*` tag in this repository.  If this repo now has `equations-v2`
and the sibling still pins `equations-v1`, the sibling's CI should emit a
warning so the re-sync is intentional.

---

*License: CC0 1.0 Universal — this file is in the public domain.*
