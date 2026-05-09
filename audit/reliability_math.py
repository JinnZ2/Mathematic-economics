"""
reliability_math.py

Standard reliability-engineering formulas applied to business supply
chains and operations. Lets a firm compute the actual numerical payoff
of redundancy instead of asserting "redundancy is good."

Formulas (textbook reliability theory, e.g. Lewis "Reliability Engineering"):

  R_series   = product(R_i)
  R_parallel = 1 - product(1 - R_i)
  R_k_of_n   = sum_{i=k..n} C(n,i) * p^i * (1-p)^(n-i)
  MTBF (constant hazard, series) = 1 / sum(lambda_i)
                                 = 1 / sum(1/MTBF_i)

These complement business_resilience_framework.cascade_vulnerability_scan:
that module flags SPOFs qualitatively; this one prices them.

License: CC0 1.0 Universal
"""

from dataclasses import dataclass
from math import comb
from typing import Dict, List


# -----------------------------------------------------------------------------
# CORE RELIABILITY PRIMITIVES
# -----------------------------------------------------------------------------

def series_reliability(reliabilities: List[float]) -> float:
    """All components must work. R_series = product(R_i)."""
    r = 1.0
    for x in reliabilities:
        r *= x
    return r


def parallel_reliability(reliabilities: List[float]) -> float:
    """At least one component must work. R_parallel = 1 - product(1 - R_i)."""
    q = 1.0
    for x in reliabilities:
        q *= (1.0 - x)
    return 1.0 - q


def k_of_n_reliability(n: int, k: int, p: float) -> float:
    """
    Probability that at least k of n identical components survive,
    each with reliability p. Useful for "we can tolerate failure of
    up to (n-k) suppliers" type questions.
    """
    if k > n or k < 0:
        raise ValueError("require 0 <= k <= n")
    return sum(comb(n, i) * (p ** i) * ((1.0 - p) ** (n - i)) for i in range(k, n + 1))


def series_mtbf(mtbfs: List[float]) -> float:
    """
    Series MTBF under constant-hazard (exponential) assumption:
      lambda_total = sum(1/MTBF_i)
      MTBF_total   = 1 / lambda_total
    Returns infinity if any input is infinite (i.e. one perfect component
    in a series chain doesn't fail; series MTBF is bounded by the worst).
    """
    if not mtbfs:
        return float("inf")
    total_lambda = sum(1.0 / m for m in mtbfs if m > 0)
    return 1.0 / total_lambda if total_lambda > 0 else float("inf")


# -----------------------------------------------------------------------------
# REDUNDANCY PAYOFF CURVES
# -----------------------------------------------------------------------------

def redundancy_payoff_curve(p: float, max_n: int = 6) -> Dict[int, float]:
    """
    Reliability of n parallel components each with per-unit reliability p.
    Shows diminishing returns: doubling n past a point yields tiny gains.
    """
    return {n: round(parallel_reliability([p] * n), 6) for n in range(1, max_n + 1)}


def redundancy_break_even(
    p: float,
    target: float,
    max_n: int = 100,
) -> int:
    """
    Smallest number of parallel redundant components needed to reach
    the target reliability, given per-unit reliability p.
    Returns -1 if unreachable in max_n attempts.
    """
    if p >= target:
        return 1
    if p <= 0.0:
        return -1
    for n in range(2, max_n + 1):
        if parallel_reliability([p] * n) >= target:
            return n
    return -1


# -----------------------------------------------------------------------------
# SUPPLY CHAIN MODEL
# -----------------------------------------------------------------------------

@dataclass
class CriticalInput:
    """
    A critical input to the business with one or more suppliers.
    Each supplier has a per-period reliability (probability it delivers
    on time and to spec). The input is available if AT LEAST ONE
    supplier delivers (parallel logic).
    """
    name: str
    suppliers: List[float]  # per-supplier reliability, 0..1


@dataclass
class SupplyChain:
    """
    A set of critical inputs all of which are required for production.
    System reliability = series across inputs, parallel within each input.
    """
    name: str
    inputs: List[CriticalInput]


def supply_chain_reliability(sc: SupplyChain) -> Dict[str, float]:
    per_input = {ci.name: parallel_reliability(ci.suppliers) for ci in sc.inputs}
    system = series_reliability(list(per_input.values()))
    weakest_link = min(per_input.items(), key=lambda kv: kv[1])
    return {
        "per_input_reliability": {k: round(v, 6) for k, v in per_input.items()},
        "system_reliability": round(system, 6),
        "weakest_link": weakest_link[0],
        "weakest_link_reliability": round(weakest_link[1], 6),
    }


def add_supplier_payoff(
    sc: SupplyChain,
    input_name: str,
    new_supplier_reliability: float,
) -> Dict[str, float]:
    """
    Compute the marginal reliability gain from adding one more supplier
    to a specific critical input. Useful for prioritizing which input
    benefits most from redundancy investment.
    """
    before = supply_chain_reliability(sc)["system_reliability"]
    new_inputs = []
    for ci in sc.inputs:
        if ci.name == input_name:
            new_inputs.append(CriticalInput(ci.name, ci.suppliers + [new_supplier_reliability]))
        else:
            new_inputs.append(ci)
    after = supply_chain_reliability(SupplyChain(sc.name, new_inputs))["system_reliability"]
    return {
        "before": round(before, 6),
        "after": round(after, 6),
        "gain": round(after - before, 6),
    }


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== REDUNDANCY PAYOFF (per-unit p=0.95) ===")
    for n, r in redundancy_payoff_curve(0.95, max_n=6).items():
        print(f"  n={n}  R_parallel = {r}")

    print("\n=== HOW MANY REDUNDANT SUPPLIERS TO HIT 0.999 RELIABILITY? ===")
    for p in [0.80, 0.90, 0.95, 0.99]:
        n = redundancy_break_even(p, 0.999)
        print(f"  per-supplier p={p}  ->  need n={n} parallel suppliers")

    print("\n=== K-OF-N TOLERANCE (n=5 suppliers, each p=0.90) ===")
    for k in range(1, 6):
        r = k_of_n_reliability(5, k, 0.90)
        print(f"  need at least k={k} of 5  ->  R = {r:.6f}")

    sc = SupplyChain(
        name="Reference manufacturer",
        inputs=[
            CriticalInput("steel_alloy",        suppliers=[0.95]),
            CriticalInput("control_chips",      suppliers=[0.90, 0.85]),
            CriticalInput("specialty_lubricant", suppliers=[0.99]),
            CriticalInput("skilled_labor",      suppliers=[0.92, 0.92, 0.92]),
            CriticalInput("electric_grid",      suppliers=[0.995]),
        ],
    )

    print(f"\n=== SUPPLY CHAIN RELIABILITY: {sc.name} ===")
    rep = supply_chain_reliability(sc)
    for inp, r in rep["per_input_reliability"].items():
        print(f"  {inp:24s}  R = {r}")
    print(f"  SYSTEM:                   R = {rep['system_reliability']}")
    print(f"  weakest link: {rep['weakest_link']} (R={rep['weakest_link_reliability']})")

    print("\n=== MARGINAL PAYOFF: ADD ONE BACKUP SUPPLIER (R=0.90) ===")
    for ci in sc.inputs:
        delta = add_supplier_payoff(sc, ci.name, 0.90)
        print(f"  add backup to {ci.name:24s}  gain = {delta['gain']:+.6f}  ({delta['before']} -> {delta['after']})")

    print("\n  (the largest gain identifies where redundancy spend pays off most)")

    print("\n=== MTBF EXAMPLE (series of 4 components, MTBFs in days) ===")
    mtbfs = [3650.0, 1825.0, 7300.0, 730.0]  # ~10y, 5y, 20y, 2y
    print(f"  components MTBF: {mtbfs}")
    print(f"  series system MTBF: {series_mtbf(mtbfs):.1f} days  "
          f"({series_mtbf(mtbfs)/365.0:.2f} years)")
    print("  (system MTBF is bounded above by the WORST component)")
