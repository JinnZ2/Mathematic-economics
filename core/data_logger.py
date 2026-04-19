#!/usr/bin/env python3
"""
Parasitic Energy Debt Accounting

Institutions extract work from organisms. When the extracted work is not
compensated with matching energy return (wages, rest, resources), the
deficit accumulates in the organism's substrate as debt. Systemic friction
events — yard searches, dispatch errors, mechanical failures — raise the
metabolic cost of the work that IS compensated, compounding the debt.

Core equation (from CLAUDE.md):

    energy_debt = unpaid_hours * metabolic_rate * (1 + friction_events * 0.15)

This module keeps the math in one small pure function and wraps it in an
accounting class that logs per-shift entries so debt can be summed across
a week, a quarter, a career.

Dependencies: stdlib only.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Dict


FRICTION_MULTIPLIER_PER_EVENT = 0.15


# -----------------------------
# Pure computation
# -----------------------------

def compute_energy_debt(unpaid_hours: float,
                        metabolic_rate: float = 1.0,
                        friction_events: int = 0,
                        friction_weight: float = FRICTION_MULTIPLIER_PER_EVENT) -> float:
    """Parasitic energy debt in abstract metabolic units.

    unpaid_hours:      hours worked but not compensated
    metabolic_rate:    baseline energy burn per hour (1.0 = nominal mammal)
    friction_events:   count of systemic failures during the unpaid work
    friction_weight:   per-event multiplier on top of the base debt
    """
    unpaid_hours = max(0.0, unpaid_hours)
    friction_events = max(0, int(friction_events))
    base = unpaid_hours * metabolic_rate
    return base * (1.0 + friction_events * friction_weight)


# -----------------------------
# Shift records + accounting
# -----------------------------

@dataclass
class ShiftRecord:
    day: date
    unpaid_hours: float
    friction_events: int
    debt: float
    note: str = ""


@dataclass
class EnergyAccounting:
    """Running ledger of parasitic energy debt across shifts."""
    metabolic_rate: float = 1.0
    friction_weight: float = FRICTION_MULTIPLIER_PER_EVENT
    shifts: List[ShiftRecord] = field(default_factory=list)

    def log_shift(self, unpaid_hours: float, friction_events: int = 0,
                  day: Optional[date] = None, note: str = "") -> ShiftRecord:
        """Record one shift and return its ShiftRecord."""
        debt = compute_energy_debt(
            unpaid_hours=unpaid_hours,
            metabolic_rate=self.metabolic_rate,
            friction_events=friction_events,
            friction_weight=self.friction_weight,
        )
        record = ShiftRecord(
            day=day or datetime.now().date(),
            unpaid_hours=max(0.0, unpaid_hours),
            friction_events=max(0, int(friction_events)),
            debt=round(debt, 3),
            note=note,
        )
        self.shifts.append(record)
        return record

    def calculate_parasitic_load(self, unpaid_hours: float,
                                 friction_events: int = 0) -> float:
        """Backwards-compatible single-shift calculation (no logging)."""
        return compute_energy_debt(
            unpaid_hours=unpaid_hours,
            metabolic_rate=self.metabolic_rate,
            friction_events=friction_events,
            friction_weight=self.friction_weight,
        )

    def total_debt(self) -> float:
        """Sum of debt across all logged shifts."""
        return round(sum(s.debt for s in self.shifts), 3)

    def total_unpaid_hours(self) -> float:
        return round(sum(s.unpaid_hours for s in self.shifts), 3)

    def total_friction_events(self) -> int:
        return sum(s.friction_events for s in self.shifts)

    def summary(self) -> Dict[str, object]:
        """Aggregate snapshot across all logged shifts."""
        n = len(self.shifts)
        return {
            "shift_count":          n,
            "total_unpaid_hours":   self.total_unpaid_hours(),
            "total_friction":       self.total_friction_events(),
            "total_energy_debt":    self.total_debt(),
            "mean_debt_per_shift":  round(self.total_debt() / n, 3) if n else 0.0,
        }

    def reset(self) -> None:
        """Clear the ledger."""
        self.shifts.clear()


# -----------------------------
# Example usage
# -----------------------------

if __name__ == "__main__":
    ledger = EnergyAccounting()

    # Case study: a rough 70-hour week
    ledger.log_shift(unpaid_hours=6,  friction_events=1, note="Mon")
    ledger.log_shift(unpaid_hours=7,  friction_events=2, note="Tue")
    ledger.log_shift(unpaid_hours=5,  friction_events=0, note="Wed")
    ledger.log_shift(unpaid_hours=6,  friction_events=3, note="Thu — yard search")
    ledger.log_shift(unpaid_hours=4,  friction_events=0, note="Fri")
    ledger.log_shift(unpaid_hours=2,  friction_events=1, note="Sat")

    for s in ledger.shifts:
        print(f"  {s.note:<28s}  unpaid={s.unpaid_hours}h  "
              f"friction={s.friction_events}  debt={s.debt}")

    summary = ledger.summary()
    print("--- weekly summary")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Legacy single-shot API still works
    one_off = ledger.calculate_parasitic_load(unpaid_hours=30, friction_events=5)
    print(f"--- one-off 70-hour-week equivalent: {one_off} units of Sovereign Entropy")
