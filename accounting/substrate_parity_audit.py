"""
substrate_parity_audit.py — CC0, stdlib only, single file, phone-deployable

Claim under test: "AI development is decoupled from substrate / humans."

Physics test: human cognition and AI compute share ONE substrate
envelope. For a given substrate state, test viability of each. AI is
coupled to human survival through the maintenance layer: if local
humans are non-viable, the infrastructure AI runs on is not
maintained -> AI fails downstream. No private "pumped-O2 / private-
cooling" exception is credited, because its own energy/entropy
ledger cannot close indefinitely (held aside).

CLAIM_TABLE (falsifiable):
  SP-1  Human and AI occupy one substrate envelope; neither is
        substrate-independent.
  SP-2  A constraint is BREACHED when current value falls outside its
        viability window [lo,hi].
  SP-3  margin := signed normalized distance to nearest window edge
        (<0 = breached); min margin across constraints names the FIRST
        failure mode.
  SP-4  AI_effective fails if its hardware window is breached OR any
        maintainer-critical human constraint is breached (maintenance
        coupling).
  SP-5  A closed-loop private exception (private O2/cooling) is HELD
        ASIDE, never credited: finite energy in, entropy monotone up
        -> cannot hold the window indefinitely.

License: CC0 1.0 Universal.
"""

from dataclasses import dataclass
from typing import List, Tuple

INF = float("inf")


@dataclass
class Constraint:
    name: str
    unit: str
    value: float                      # current measured substrate state
    human_window: Tuple[float, float] # [lo, hi] viable for human cognition/survival
    ai_window: Tuple[float, float]    # [lo, hi] viable for AI hardware directly (-inf,inf = no direct effect)
    maintainer_coupled: bool = True   # does breaching the human window also doom AI via lost maintenance?

    @staticmethod
    def _margin(v, lo, hi) -> float:
        half = (hi - lo) / 2 if (lo > -INF and hi < INF) else INF
        d = min(v - lo, hi - v)        # distance to nearest edge; negative if outside
        return d / half if half not in (0, INF) else d  # normalized where two-sided; raw otherwise

    def human_margin(self): return self._margin(self.value, *self.human_window)
    def ai_margin(self):    return self._margin(self.value, *self.ai_window)
    def human_breached(self): return self.human_margin() < 0
    def ai_direct_breached(self): return self.ai_margin() < 0


@dataclass
class SubstrateAudit:
    name: str
    constraints: List[Constraint]

    def add(self, c: Constraint): self.constraints.append(c); return self

    def ai_effective_breached(self, c: Constraint) -> bool:        # SP-4
        return c.ai_direct_breached() or (c.maintainer_coupled and c.human_breached())

    def first_failure(self):                                       # SP-3
        return min(self.constraints, key=lambda c: min(c.human_margin(), c.ai_margin()))

    def report(self) -> str:
        L = [f"SUBSTRATE PARITY AUDIT  {self.name}"]
        L.append(f"  {'CONSTRAINT':22}{'value':>10}{'unit':>8}"
                 f"{'human_m':>10}{'ai_m':>10}  verdict")
        any_h = any_ai = False
        for c in self.constraints:
            hm, am = c.human_margin(), c.ai_margin()
            h_breached = hm < 0
            ai_breached = self.ai_effective_breached(c)
            any_h = any_h or h_breached
            any_ai = any_ai or ai_breached
            hv = "H-FAIL" if h_breached else "H-OK"
            av = "AI-FAIL" if ai_breached else "AI-OK"
            cpl = "(coupled)" if c.maintainer_coupled and h_breached and not c.ai_direct_breached() else ""
            L.append(f"  {c.name:22}{c.value:10.4g}{c.unit:>8}"
                     f"{hm:10.3f}{am:10.3f}  {hv}/{av}{cpl}")
        ff = self.first_failure()
        L.append(f"  FIRST FAILURE MODE: {ff.name} "
                 f"(human_m={ff.human_margin():.3f}, ai_m={ff.ai_margin():.3f})")
        L.append(f"  HELD ASIDE: private closed-loop exceptions (pumped O2 / private cooling) "
                 f"-> not credited (SP-5)")
        status = "RED" if (any_h or any_ai) else "GREEN"
        L.append(f"  HUMAN viable: {not any_h}   AI viable: {not any_ai}   STATUS: {status}")
        return "\n".join(L)


# ---- demo: degrading substrate (numbers illustrative; structure is the point) ----

def _demo_degrading_substrate():
    a = SubstrateAudit("local_substrate_state", [])
    # O2: no direct AI effect, but humans maintain the datacenter -> coupled
    a.add(Constraint("O2_fraction", "%vol", 20.9, human_window=(16, 23), ai_window=(-INF, INF), maintainer_coupled=True))
    # SO2 / acid load: degrades human lungs AND corrodes hardware + cooling intake
    a.add(Constraint("SO2_load", "ppm", 3.0, human_window=(0, 0.5), ai_window=(0, 2.0), maintainer_coupled=True))
    # water salinity: if too saline to drink, it's also corrosive to cool with (the brine point)
    a.add(Constraint("water_salinity", "g/L", 4.0, human_window=(0, 1.0), ai_window=(0, 5.0), maintainer_coupled=True))
    # ambient temp: AI needs tighter band for cooling headroom than humans need to survive
    a.add(Constraint("ambient_temp", "C", 30.0, human_window=(-40, 45), ai_window=(0, 35), maintainer_coupled=True))
    # ionizing radiation: bit-flip risk for AI, dose risk for humans
    a.add(Constraint("radiation", "mSv/yr", 20.0, human_window=(0, 50), ai_window=(0, 100), maintainer_coupled=True))
    # grid stability: one-sided lower bound; AI needs it cleaner than humans do
    a.add(Constraint("grid_stability", "idx", 0.95, human_window=(0.7, INF), ai_window=(0.9, INF), maintainer_coupled=True))
    return a


if __name__ == "__main__":
    print(_demo_degrading_substrate().report())
