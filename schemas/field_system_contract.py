"""Field-system contract -- stable shape of the state dict consumed by
`audit/field_system.py` and the report dict it returns.

The audit/ modules (`field_system.report`, `system_audit.SixSigmaAudit`,
`efficiency_report_audit.audit_efficiency_report`) all pass the same 11-key
state dict around. This module makes that shape explicit and
type-checkable without forcing the consumers to adopt dataclass inputs.

Scope of stability:
    - FieldSystemState: 11 named fields, float-typed, with documented ranges.
    - FieldSystemReport: the dict shape returned by `field_system.report()`.
    - YieldAnalysis: the inner dict returned by `field_system.effective_yield()`.

Calibration knobs that are explicitly NOT part of the contract (may change
without bumping CONTRACT_VERSION major):
    - BASELINES.water_retention_min (0.4), BASELINES.energy_ratio_min (1.0).
    - ecological_amplification cap (2.0 default).

Versioning: breaking changes to field names, types, or meaning bump major.
Adding fields with backward-compatible defaults bumps minor.

Dependencies: stdlib only.
License: CC0 1.0 Universal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True)
class FieldSystemState:
    """Regenerative-system state vector.

    All fields are float. Ranges below are soft guidance; the field_system
    itself enforces constraints separately via `constraints()` and `drift()`.
    """

    soil_trend: float               # change per unit time; positive = building
    water_retention: float          # [0, 1]
    input_energy: float             # arbitrary units, >= 0
    output_yield: float             # arbitrary units, >= 0
    disturbance: float              # [0, 1]
    waste_factor: float             # [0, 1]
    nutrient_density: float         # [0, 1]
    production_area: float          # acres
    ecological_area: float          # acres
    coupling_strength: float        # [0, 1]
    ecological_amplification: float  # >= 1.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldSystemState":
        return cls(**{k: float(data[k]) for k in cls.__dataclass_fields__})


@dataclass(frozen=True)
class YieldAnalysis:
    """Inner shape returned by `field_system.effective_yield()`."""

    adjusted_yield: float
    ecological_amplification_factor: float
    effective_yield_per_acre: float
    total_nourishment_units: float

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "YieldAnalysis":
        return cls(**{k: float(data[k]) for k in cls.__dataclass_fields__})


@dataclass(frozen=True)
class FieldSystemReport:
    """Shape returned by `field_system.report()`.

    `constraints` and `drift` keys are bools keyed by constraint name;
    `suggestions` contains `issues` (bool map) and `actions` (list of str).
    """

    state: Dict[str, float]
    constraints: Dict[str, bool]
    drift: Dict[str, bool]
    score: float
    suggestions: Dict[str, Any]
    yield_analysis: YieldAnalysis

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldSystemReport":
        return cls(
            state=dict(data["state"]),
            constraints=dict(data["constraints"]),
            drift=dict(data["drift"]),
            score=float(data["score"]),
            suggestions=dict(data["suggestions"]),
            yield_analysis=YieldAnalysis.from_dict(data["yield_analysis"]),
        )
