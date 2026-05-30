"""
thermodynamic_exception_detector.py — CC0, stdlib only, single file, phone-deployable

Claim under test: "I'll maintain my own [O2 / cooling / water]
indefinitely with a closed loop." (the private-exception move: CEO
pumps own air, datacenter runs own private cooling.)

Physics test: no loop is perfectly sealed or perfectly efficient (2nd
law). Loss > 0 per cycle, regeneration efficiency < 1 and degrades
(fouling/wear -> entropy). Either the finite energy reservoir depletes,
or rising maintenance energy / falling efficiency lets the maintained
quantity drift out of its viability window. Return the FAILURE TIME.
"Indefinite" is falsified whenever t_fail < inf -- which holds for any
finite reservoir OR any decay > 0.

CLAIM_TABLE (falsifiable):
  TE-1  Real closed loop: loss_per_cycle > 0 and 0 < eta0 < 1
        (no perfect seal, no perfect regen).
  TE-2  Maintenance energy per cycle is monotone non-decreasing as
        efficiency decays.
  TE-3  "Maintained indefinitely" is FALSIFIED iff t_fail < inf.
  TE-4  t_fail < inf whenever (reservoir finite) OR (efficiency decay
        d > 0). Both hold physically.
  TE-5  A claim survives only by asserting d=0 AND reservoir=inf AND
        eta>=1 -> 2nd-law VIOLATION, flagged and NOT credited (this is
        the held-aside term from substrate_parity SP-5).

License: CC0 1.0 Universal.
"""

from dataclasses import dataclass
from math import isinf

INF = float("inf")


@dataclass
class ClosedLoopClaim:
    name: str
    setpoint: float          # quantity the loop tries to hold (e.g., O2 partial pressure kPa)
    window: tuple            # (lo, hi) viability band for the maintained quantity
    loss_per_cycle: float    # quantity lost each cycle before regen (leak/dissipation), > 0 physically
    eta0: float              # initial regen efficiency (0..1), restored = eta * loss_target
    decay: float             # per-cycle fractional efficiency loss d (fouling/wear), >= 0
    e_base: float            # energy to regen one cycle at eta0
    reservoir: float         # total energy available (finite physically; INF only as an assertion)
    cycle_seconds: float = 86400.0   # cycle length -> converts t_fail to real time

    def is_asserted_exception(self) -> bool:                       # TE-5
        return self.decay <= 0 and isinf(self.reservoir) and self.eta0 >= 1.0

    def run(self, max_cycles: int = 10_000_000):
        if self.is_asserted_exception():
            return {"verdict": "VIOLATION", "mode": "asserts d=0 & reservoir=inf & eta>=1 (2nd law)",
                    "t_fail_cycles": None, "t_fail_seconds": None}
        lo, hi = self.window
        Q = self.setpoint
        E = self.reservoir
        eta = self.eta0
        for t in range(1, max_cycles + 1):
            Q -= self.loss_per_cycle                      # dissipation first (TE-1)
            Q += eta * self.loss_per_cycle                # imperfect regen
            E -= self.e_base / eta if eta > 0 else INF    # cost rises as eta falls (TE-2)
            if Q < lo or Q > hi:
                return {"verdict": "FALSIFIED", "mode": f"window breach (Q={Q:.4g} out of [{lo},{hi}])",
                        "t_fail_cycles": t, "t_fail_seconds": t * self.cycle_seconds}
            if E <= 0:
                return {"verdict": "FALSIFIED", "mode": "energy reservoir exhausted",
                        "t_fail_cycles": t, "t_fail_seconds": t * self.cycle_seconds}
            eta *= (1 - self.decay)                        # entropy proxy
        return {"verdict": "UNRESOLVED", "mode": f"no failure within {max_cycles} cycles",
                "t_fail_cycles": None, "t_fail_seconds": None}

    def report(self) -> str:
        r = self.run()
        L = [f"THERMO EXCEPTION  {self.name}"]
        L.append(f"  setpoint={self.setpoint}  window={self.window}  loss/cyc={self.loss_per_cycle}")
        L.append(f"  eta0={self.eta0}  decay={self.decay}  e_base={self.e_base}  reservoir={self.reservoir}")
        L.append(f"  VERDICT: {r['verdict']}   MODE: {r['mode']}")
        if r["t_fail_cycles"] is not None:
            days = r["t_fail_seconds"] / 86400.0
            L.append(f"  FAILS AT: cycle {r['t_fail_cycles']}  (~{days:.2f} days at "
                     f"{self.cycle_seconds/86400:.3g} d/cycle)")
        if r["verdict"] == "VIOLATION":
            L.append(f"  HELD ASIDE: unphysical assertion, not credited as a real exception (TE-5)")
        return "\n".join(L)


# ---- demo: the CEO's private O2 tank, and the honest physical version ----

def _demo_honest_loop():
    # Honest closed loop: small leak, 92% regen, slow fouling, finite battery bank.
    return ClosedLoopClaim(
        name="private_O2_loop_REAL",
        setpoint=21.0, window=(16.0, 23.0),   # kPa-ish O2 partial pressure, illustrative
        loss_per_cycle=0.8, eta0=0.92, decay=0.0008,
        e_base=10.0, reservoir=50_000.0, cycle_seconds=3600.0)  # 1-hour cycles


def _demo_asserted_indefinite():
    # The marketing claim: indefinite. Asserts no decay + infinite energy + perfect regen.
    return ClosedLoopClaim(
        name="private_O2_loop_CLAIMED_INDEFINITE",
        setpoint=21.0, window=(16.0, 23.0),
        loss_per_cycle=0.8, eta0=1.0, decay=0.0, e_base=10.0, reservoir=INF, cycle_seconds=3600.0)


if __name__ == "__main__":
    print(_demo_honest_loop().report())
    print()
    print(_demo_asserted_indefinite().report())
