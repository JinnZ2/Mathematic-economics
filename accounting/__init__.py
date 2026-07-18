"""
accounting — composable falsifiable-accounting modules

Domain-agnostic audit primitives used across the JinnZ2
substrate-primary toolchain. Each module declares its own claim
family with a stable prefix that does not enter the global
mathematic-economics C-series:

  atomic_accounting                   -> AA-1 .. AA-5
  gdp_metrology_political_invariant   -> GM-1 .. GM-5
  substrate_parity_audit              -> SP-1 .. SP-5
  thermodynamic_exception_detector    -> TE-1 .. TE-5
  cost_of_competition                 -> CC-1 .. CC-6
  electron_accounting                 -> EA-1 .. EA-4

These claim families are documented in `accounting/CLAIMS.md`.

License: CC0 1.0 Universal.
"""

from . import (
    atomic_accounting,
    gdp_metrology_political_invariant,
    substrate_parity_audit,
    thermodynamic_exception_detector,
    cost_of_competition,
    electron_accounting,
)

__all__ = [
    "atomic_accounting",
    "gdp_metrology_political_invariant",
    "substrate_parity_audit",
    "thermodynamic_exception_detector",
    "cost_of_competition",
    "electron_accounting",
]
