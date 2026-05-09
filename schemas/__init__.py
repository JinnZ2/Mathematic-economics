"""Stable data contracts for inter-module shapes.

Each module in this package defines a versioned dataclass mirror of a shape
passed between other parts of the repo (or to / from sibling repos). The
point is to make the wire format explicit and type-checkable so consumers
don't silently drift out of sync with producers.

License: CC0 1.0 Universal (public domain).
"""

from schemas.claim_contract import (
    CONTRACT_VERSION as CLAIM_CONTRACT_VERSION,
    Claim,
    ClaimBounds,
    CycleClass,
)
from schemas.field_system_contract import (
    CONTRACT_VERSION as FIELD_SYSTEM_CONTRACT_VERSION,
    FieldSystemReport,
    FieldSystemState,
    YieldAnalysis,
)

__all__ = [
    "CLAIM_CONTRACT_VERSION",
    "Claim",
    "ClaimBounds",
    "CycleClass",
    "FIELD_SYSTEM_CONTRACT_VERSION",
    "FieldSystemReport",
    "FieldSystemState",
    "YieldAnalysis",
]
