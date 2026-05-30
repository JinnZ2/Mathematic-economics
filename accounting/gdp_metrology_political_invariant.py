"""
gdp_metrology_political_invariant.py — CC0, stdlib only, single file, phone-deployable

Claim under test: "automation produces economic growth."

Physics test: genuine automation productivity = output per unit
energy (J). That ratio is substrate-physical -> it MUST be invariant
across currency, ownership, political system, and region. Where the
physical ratio is constant but the claimed monetary gain varies, the
gain spread is extraction / accounting artifact, NOT productivity.

CLAIM_TABLE (falsifiable):
  GM-1  Productivity signal := output_units / energy_in_J. Currency-
        free, substrate-physical.
  GM-2  For true automation, coeff. of variation of the signal across
        regimes <= cv_tol.
  GM-3  claimed_gain (currency, no physical-output delta behind it) is
        HELD ASIDE, never netted.
  GM-4  If signal CV <= cv_tol but claimed_gain CV > cv_tol, the gain
        spread = extraction artifact (magnitude reported), classification
        != productivity.
  GM-5  If the signal collapses toward 0 in a pre-industrial / off-grid
        substrate, the gain is substrate-DEPENDENT, not universal
        automation.

License: CC0 1.0 Universal.
"""

from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import List, Optional

PRE_INDUSTRIAL = "pre_industrial"   # off-grid / subsistence substrate marker


@dataclass
class Deployment:
    region: str
    political_system: str            # capitalist | socialist | mixed | command | pre_industrial | ...
    currency: str
    energy_in_J: float               # measured energy input
    output_units: float              # measured physical output (SAME unit across all deployments)
    claimed_gain: float = 0.0        # claimed monetary "growth" (currency) -> held aside (GM-3)
    labor_cost: float = 0.0          # informational only
    externalized_cost: float = 0.0   # informational only (dumped brine, emissions, etc.)

    def signal(self) -> float:       # GM-1
        return self.output_units / self.energy_in_J if self.energy_in_J else 0.0


def cv(xs: List[float]) -> float:    # coefficient of variation, dimensionless
    m = mean(xs)
    return (pstdev(xs) / m) if m else 0.0


@dataclass
class InvarianceAudit:
    name: str
    cv_tol: float = 0.05             # allowed spread for "invariant"
    deployments: List[Deployment] = field(default_factory=list)

    def add(self, d: Deployment): self.deployments.append(d); return self

    def industrial(self) -> List[Deployment]:
        return [d for d in self.deployments if d.political_system != PRE_INDUSTRIAL]

    def signal_cv(self, deployments: Optional[List[Deployment]] = None) -> float:
        deps = deployments if deployments is not None else self.industrial()
        return cv([d.signal() for d in deps])

    def gain_cv(self, deployments: Optional[List[Deployment]] = None) -> float:
        deps = deployments if deployments is not None else self.industrial()
        g = [d.claimed_gain for d in deps]
        return cv(g) if any(g) else 0.0

    def substrate_dependence(self) -> Optional[float]:   # GM-5
        pre = [d.signal() for d in self.deployments if d.political_system == PRE_INDUSTRIAL]
        ind = [d.signal() for d in self.industrial()]
        if not pre or not ind: return None
        m_ind = mean(ind)
        return mean(pre) / m_ind if m_ind else 0.0   # ->0 means gain needed the grid substrate

    def classify(self, deployments: Optional[List[Deployment]] = None) -> str:
        deps = deployments if deployments is not None else self.industrial()
        scv, gcv = self.signal_cv(deps), self.gain_cv(deps)
        if scv <= self.cv_tol and gcv <= self.cv_tol:
            return "PRODUCTIVITY (physics-invariant, monetary-invariant)"
        if scv <= self.cv_tol and gcv > self.cv_tol:
            return "EXTRACTION ARTIFACT (physics flat, money varies -> not automation gain)"  # GM-4
        if scv > self.cv_tol:
            return "NOT INVARIANT (physical signal varies by regime -> measuring governance, not automation)"
        return "INDETERMINATE"

    def status(self, deployments: Optional[List[Deployment]] = None) -> str:
        c = self.classify(deployments)
        if c.startswith("PRODUCTIVITY"): return "GREEN"
        if c.startswith("NOT INVARIANT"): return "YELLOW"
        return "RED"

    def report(self) -> str:
        ind = self.industrial()           # compute once, share across CV / classify calls
        L = [f"AUDIT {self.name}   cv_tol={self.cv_tol}"]
        L.append(f"  {'REGION':14}{'POLITICS':14}{'CCY':5}{'signal(out/J)':>16}{'claimed_gain':>16}")
        for d in self.deployments:
            L.append(f"  {d.region:14}{d.political_system:14}{d.currency:5}"
                     f"{d.signal():16.6g}{d.claimed_gain:16.6g}")
        L.append(f"  signal CV (industrial): {self.signal_cv(ind):.4f}   "
                 f"claimed_gain CV: {self.gain_cv(ind):.4f}")
        sd = self.substrate_dependence()
        if sd is not None:
            L.append(f"  pre-industrial/industrial signal ratio: {sd:.3f}"
                     + ("   <SUBSTRATE-DEPENDENT (GM-5)>" if sd < 0.5 else ""))
        L.append(f"  HELD ASIDE: claimed_gain is currency, never netted into physical signal (GM-3)")
        L.append(f"  CLASS: {self.classify(ind)}")
        L.append(f"  STATUS: {self.status(ind)}")
        return "\n".join(L)


# ---- demo: identical automation, 4 regimes + 1 off-grid -------------------
# Physical output/J ~flat; money diverges.

def _demo_automation_productivity():
    a = InvarianceAudit("automation_productivity_claim", cv_tol=0.05)
    # same machine, same physical throughput per joule everywhere it has grid substrate:
    a.add(Deployment("US",          "capitalist", "USD", energy_in_J=1.00e6, output_units=1000, claimed_gain=150))
    a.add(Deployment("Germany",     "mixed",      "EUR", energy_in_J=1.00e6, output_units=1000, claimed_gain=20))
    a.add(Deployment("Vietnam",     "socialist",  "VND", energy_in_J=1.00e6, output_units=1000, claimed_gain=140))
    a.add(Deployment("China",       "command",    "CNY", energy_in_J=1.00e6, output_units=1000, claimed_gain=35))
    # off-grid substrate: same machine starves without the grid -> signal collapses (GM-5):
    a.add(Deployment("rural_offgrid", PRE_INDUSTRIAL, "barter", energy_in_J=1.00e6, output_units=120, claimed_gain=0))
    return a


if __name__ == "__main__":
    print(_demo_automation_productivity().report())
