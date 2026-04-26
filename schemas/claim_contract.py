"""Claim contract -- machine-checkable mirror of the CLAIM template
declared in `DIFFERENTIAL_FRAME.md` at the repo root.

The frame stipulates that every assertion in this repo is a differential
equation bounded by conditions. This module gives that template a
type-checkable form so structured claim attribution composes with the
rest of the codebase (companions: `field_system_contract.py` for
field_system shapes; `calibration/schema.py` for falsifier-bearing
diagnostics).

Adopt incrementally: existing modules that already encode this frame
through their structure (dataclass fields with units, falsifier strings
in `calibration/`, scope blocks in `study_scope_audit`) need not be
refactored. Use this when a new model wants the explicit, validated form.

Scope of stability:
    - Claim, ClaimBounds, CycleClass: stable field names and types.
    - Validation rules: every required list field must be non-empty;
      bounds must have all three sub-fields; cycle_class must match
      the enum.

Versioning: breaking changes to field names, types, or required-ness
bump major. Adding fields with backward-compatible defaults bumps minor.

Dependencies: stdlib only.
License: CC0 1.0 Universal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


CONTRACT_VERSION = "1.0.0"


class CycleClass(str, Enum):
    """The temporal class of the rate equation. Determines how
    permanence-shaped the curve looks under casual observation:
    century-scale curves can be misread as permanence."""

    DAY = "day"
    SEASON = "season"
    GENERATION = "generation"
    CENTURY = "century"
    GEOLOGIC = "geologic"


@dataclass(frozen=True)
class ClaimBounds:
    """Where, when, and at what resolution a claim's rate equation holds.

    All three are required: a claim with one missing bound is incomplete
    and a downstream consumer should refuse to pin to it.
    """

    spatial: str   # where the equation holds
    temporal: str  # which cycle / time horizon
    scale: str     # resolution at which dX/dt is measured


@dataclass(frozen=True)
class Claim:
    """Structured form of an assertion in this repo.

    Required (non-empty):
        observable, rate_equation, bounds, conditions, invalid_if,
        measured_by, cycle_class.

    Optional:
        relational_web (a leaf claim with no documented couplings is
        still well-formed; keep the field but allow empty).
    """

    observable: str
    rate_equation: str
    bounds: ClaimBounds
    conditions: List[str]
    invalid_if: List[str]
    measured_by: List[str]
    cycle_class: CycleClass
    relational_web: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.observable:
            raise ValueError("Claim.observable must be non-empty")
        if not self.rate_equation:
            raise ValueError("Claim.rate_equation must be non-empty")
        if not self.conditions:
            raise ValueError("Claim.conditions must list at least one condition")
        if not self.invalid_if:
            raise ValueError("Claim.invalid_if must list at least one falsifying boundary")
        if not self.measured_by:
            raise ValueError("Claim.measured_by must list at least one observable signal")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["cycle_class"] = self.cycle_class.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Claim":
        bounds_data = data["bounds"]
        return cls(
            observable=str(data["observable"]),
            rate_equation=str(data["rate_equation"]),
            bounds=ClaimBounds(
                spatial=str(bounds_data["spatial"]),
                temporal=str(bounds_data["temporal"]),
                scale=str(bounds_data["scale"]),
            ),
            conditions=list(data["conditions"]),
            invalid_if=list(data["invalid_if"]),
            measured_by=list(data["measured_by"]),
            cycle_class=CycleClass(data["cycle_class"]),
            relational_web=list(data.get("relational_web", [])),
        )
