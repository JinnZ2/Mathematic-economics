"""
atomic_accounting.py — CC0, stdlib only, phone-deployable, single file

Universal closure test: input flux == output flux + transformation cost
+ accounted remainder. Gap != 0 within tolerance -> ledger does not
close -> hidden term / cascade signal.

CLAIM_TABLE (falsifiable):
  AA-1  A ledger closes iff |sum(signed entries)| <= tol.
  AA-2  Mixed units in one ledger is a measurement error, not an
        accounting result.
  AA-3  An entry marked unfalsifiable (no physical unit / no source)
        cannot reduce the gap; it is held aside and reported, never
        netted.
  AA-4  Closure status is GREEN |gap|<=tol, YELLOW <=warn, RED
        otherwise.
  AA-5  A ledger that only closes after adding an unfalsifiable plug
        term is RED, not GREEN.

License: CC0 1.0 Universal.
"""

from dataclasses import dataclass, field
from typing import List

IN, OUT, COST = "IN", "OUT", "COST"   # OUT and COST drain the system (negative); IN feeds it (positive)
_SIGN = {IN: +1.0, OUT: -1.0, COST: -1.0}


@dataclass
class Entry:
    kind: str            # IN | OUT | COST
    mag: float           # magnitude, >=0, in `unit`
    unit: str            # physical unit string, e.g. "J", "kg", "USD", "bit"
    label: str
    falsifiable: bool = True   # False = asserted, no unit-true source -> held aside (AA-3)
    source: str = ""

    def signed(self) -> float:
        return _SIGN[self.kind] * self.mag


@dataclass
class Ledger:
    name: str
    unit: str                          # the single unit this ledger is denominated in (AA-2)
    tol: float = 0.0                   # closure tolerance, same unit
    warn: float = 0.0                  # yellow threshold, same unit
    entries: List[Entry] = field(default_factory=list)

    def add(self, kind, mag, unit, label, falsifiable=True, source=""):
        self.entries.append(Entry(kind, abs(mag), unit, label, falsifiable, source))
        return self

    # convenience
    def inflow(self, mag, label, source=""):  return self.add(IN,   mag, self.unit, label, True,  source)
    def outflow(self, mag, label, source=""): return self.add(OUT,  mag, self.unit, label, True,  source)
    def cost(self, mag, label, source=""):    return self.add(COST, mag, self.unit, label, True,  source)
    def assert_term(self, kind, mag, label):  return self.add(kind, mag, self.unit, label, False, "ASSERTED")

    def unit_errors(self) -> List[Entry]:
        return [e for e in self.entries if e.unit != self.unit]              # AA-2

    def held_aside(self) -> List[Entry]:
        return [e for e in self.entries if not e.falsifiable]                # AA-3

    def gap(self) -> float:
        # only falsifiable, unit-consistent entries net (AA-3)
        return sum(e.signed() for e in self.entries
                   if e.falsifiable and e.unit == self.unit)

    def status(self) -> str:
        # Single pass: collect unit-error / gap / held-aside flags together.
        has_unit_errors = False
        gap = 0.0
        has_held = False
        for e in self.entries:
            if e.unit != self.unit:
                has_unit_errors = True
            if not e.falsifiable:
                has_held = True
            elif e.unit == self.unit:
                gap += e.signed()
        if has_unit_errors:
            return "RED"                                                     # AA-2
        g = abs(gap)
        if g <= self.tol:
            return "RED" if has_held else "GREEN"     # AA-5: plug-rescued -> RED
        if g <= self.warn: return "YELLOW"
        return "RED"                                                         # AA-4

    def report(self) -> str:
        L = [f"LEDGER {self.name}  [{self.unit}]  tol={self.tol} warn={self.warn}"]
        for e in self.entries:
            flag = "" if e.falsifiable else "  <ASSERTED/held>"
            ue = "  <UNIT-ERR>" if e.unit != self.unit else ""
            L.append(f"  {e.kind:4} {e.signed():+18.4g} {e.unit:>6}  {e.label}{flag}{ue}")
        L.append(f"  {'GAP':4} {self.gap():+18.4g} {self.unit:>6}  (unaccounted, falsifiable-only)")
        held = self.held_aside()
        if held:
            L.append(f"  HELD ASIDE: {sum(e.signed() for e in held):+.4g} {self.unit} "
                     f"across {len(held)} asserted term(s) -> NOT netted")
        L.append(f"  STATUS: {self.status()}")
        return "\n".join(L)


# ---- demo 1: orbital/lunar compute energy budget --------------------------
# (numbers are placeholders; the point is the GAP)

def _demo_orbital_compute():
    base_compute_MW = 1.0
    lg = Ledger("orbital_compute_power", unit="MW", tol=0.05, warn=0.25)
    lg.inflow(base_compute_MW * 0.0, "claimed net deliverable", "press")  # narrative says ~0 overhead
    # real drains the narrative omits:
    lg.cost(base_compute_MW * 3,   "triple-modular-redundancy draw", "TMR for bit-flips")
    lg.cost(base_compute_MW * 3.0, "radiative cooling pump/loop (vacuum, no convection)", "thermo")
    lg.cost(base_compute_MW * 0.6, "shielding-mass amortized launch energy", "Orion dose > model")
    lg.cost(base_compute_MW * 0.3, "maintenance launch cadence + debris-avoidance dV", "Kessler")
    lg.inflow(base_compute_MW * 1, "claimed solar/nuclear supply", "spec")
    # the part nobody publishes -> assert it so it shows as an unfilled plug:
    lg.assert_term(IN, base_compute_MW * 6.9, "UNPUBLISHED power source to close budget")
    return lg


# ---- demo 2: Ashland fire-protection-fee case -----------------------------
# Fee charged for service not rendered. Closes only with a hypothetical
# plug; therefore RED per AA-5.

def _demo_ashland_fee(annual_fee: float = 240.0):
    lg = Ledger("ashland_fee", unit="USD", tol=0.0)
    lg.inflow(annual_fee, "fire-protection fee charged")
    lg.cost(0, "service delivered (no road/hydrant access)", "city admitted")
    lg.assert_term(IN, annual_fee, "hypothetical aerial response justification")
    return lg


if __name__ == "__main__":
    print(_demo_orbital_compute().report())
    print()
    print(_demo_ashland_fee().report())
