"""
fragility_convexity.py

Falsifiable fragility test based on Taleb's convexity framework and
Jensen's inequality. A system is:

  FRAGILE      when its payoff function is concave (f'' < 0) to volatility:
               harm grows nonlinearly in stress.
  ROBUST       when its payoff is linear (f'' ~ 0): proportional response.
  ANTIFRAGILE  when its payoff is convex (f'' > 0): gains grow nonlinearly
               in stress.

Operational test (numerical second difference at the operating point):

  f''(x0) ~ ( f(x0+d) + f(x0-d) - 2*f(x0) ) / d^2
  fragility = -f''(x0)              (sign-flipped so positive = fragile)
  asymmetry =   2*f(x0) - f(x0+d) - f(x0-d)   (gain-loss imbalance under +/- d)

This complements business_resilience_framework: existing modules score
state; this scores BEHAVIOR UNDER STRESS, which is the actual question
when a shock arrives.

License: CC0 1.0 Universal
"""

from typing import Callable, Dict, List


# -----------------------------------------------------------------------------
# CORE CONVEXITY PRIMITIVES
# -----------------------------------------------------------------------------

def second_difference(payoff: Callable[[float], float], x0: float, d: float) -> float:
    """
    Numerical approximation of f''(x0).
    Negative => concave => fragile.
    Positive => convex  => antifragile.
    """
    return (payoff(x0 + d) + payoff(x0 - d) - 2.0 * payoff(x0)) / (d * d)


def fragility_index(payoff: Callable[[float], float], x0: float, d: float) -> float:
    """
    Sign-flipped second difference so:
      positive = fragile, negative = antifragile, zero = robust.
    """
    return -second_difference(payoff, x0, d)


def dose_response_asymmetry(payoff: Callable[[float], float], x0: float, d: float) -> float:
    """
    Gain-loss imbalance:
      asymmetry = (loss from -d shock) - (gain from +d shock)
                = (f(x0) - f(x0-d)) - (f(x0+d) - f(x0))
                = 2*f(x0) - f(x0+d) - f(x0-d)
    Positive value means losses exceed gains for symmetric shocks
    -- the signature of a fragile (concave) payoff.
    """
    return 2.0 * payoff(x0) - payoff(x0 + d) - payoff(x0 - d)


def classify_payoff(
    payoff: Callable[[float], float],
    x0: float,
    d: float,
    eps: float = 1e-6,
) -> str:
    f = fragility_index(payoff, x0, d)
    if f > eps:
        return "fragile"
    if f < -eps:
        return "antifragile"
    return "robust"


# -----------------------------------------------------------------------------
# REFERENCE PAYOFF FUNCTIONS
# -----------------------------------------------------------------------------

def linear_payoff(margin: float = 0.10):
    """Pure pass-through: profit = revenue * margin. Robust to volatility."""
    return lambda revenue: revenue * margin


def leveraged_payoff(
    fixed_cost: float = 0.80,
    variable_margin: float = 1.0,
    distress_threshold: float = 0.70,
    distress_penalty: float = 2.0,
):
    """
    Operating-leverage payoff with a distress region:
      profit = revenue*variable_margin - fixed_cost   above threshold
      profit = above - distress_penalty*(threshold-revenue)   below threshold
    The kink at the distress threshold (covenant breach, fire-sale of
    assets, emergency financing) makes the payoff concave near and below
    that point -- fragile to negative shocks. Far above the threshold
    the payoff is linear (robust).
    """
    def f(revenue: float) -> float:
        gross = revenue * variable_margin - fixed_cost
        if revenue < distress_threshold:
            return gross - distress_penalty * (distress_threshold - revenue)
        return gross
    return f


def jit_inventory_payoff(buffer: float = 0.05):
    """
    Just-in-time supply chain. Output = min(supply, demand=1.0).
    Above buffer, output saturates (no upside from extra supply).
    Below buffer, output collapses linearly. Concave -- fragile to
    supply shocks, no symmetric upside.
    """
    return lambda supply: min(supply, 1.0 + buffer) - max(0.0, 1.0 - supply) * 0.5


def optionality_payoff(threshold: float = 1.0):
    """
    Real-options payoff: profit = max(0, revenue - threshold).
    Convex -- you cap downside at zero and let upside run. Antifragile.
    """
    return lambda revenue: max(0.0, revenue - threshold)


def diversified_payoff(n_lines: int = 5, line_volatility: float = 0.20):
    """
    N independent revenue lines with idiosyncratic shocks. The aggregate
    is more linear (less convex) than any single line, but compared to
    a single-line system at equal expected revenue, the diversified
    system's higher-moment fragility shrinks ~1/sqrt(N). Reported here
    as the analytic limit: returns a near-linear function with small
    convex correction proportional to 1/n_lines.
    """
    correction = 0.10 / max(1, n_lines)
    return lambda revenue: revenue + correction * (revenue - 1.0) ** 2


# -----------------------------------------------------------------------------
# STRESS-TEST HARNESS
# -----------------------------------------------------------------------------

def stress_test(
    name: str,
    payoff: Callable[[float], float],
    x0: float = 1.0,
    deltas: List[float] = None,
) -> Dict[str, float]:
    """
    Run convexity diagnostics across multiple stress magnitudes.
    Reports fragility at each delta plus the classification.
    """
    if deltas is None:
        deltas = [0.05, 0.10, 0.20, 0.40]
    return {
        "name": name,
        "operating_point": x0,
        "fragility_by_delta": {
            d: round(fragility_index(payoff, x0, d), 4) for d in deltas
        },
        "asymmetry_by_delta": {
            d: round(dose_response_asymmetry(payoff, x0, d), 4) for d in deltas
        },
        "classification_at_d=0.20": classify_payoff(payoff, x0, 0.20),
    }


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    cases = [
        ("Linear pass-through (10% margin)",           linear_payoff(0.10),   1.0),
        ("Leveraged firm, comfortable margin",         leveraged_payoff(),    1.0),
        ("Leveraged firm, near distress threshold",    leveraged_payoff(),    0.75),
        ("JIT supply chain (5% buffer)",               jit_inventory_payoff(0.05), 1.0),
        ("Optionality / call-style payoff",            optionality_payoff(1.0),    1.05),
        ("Diversified (5 independent lines)",          diversified_payoff(5),      1.0),
    ]

    for name, fn, x0 in cases:
        report = stress_test(name, fn, x0)
        print(f"\n  {report['name']}")
        print(f"    classification (d=0.20): {report['classification_at_d=0.20']}")
        print(f"    fragility by delta:      {report['fragility_by_delta']}")
        print(f"    asymmetry by delta:      {report['asymmetry_by_delta']}")

    print("\n  INTERPRETATION")
    print("    fragility > 0  =>  losses exceed gains under symmetric shock (FRAGILE)")
    print("    fragility ~ 0  =>  proportional response (ROBUST)")
    print("    fragility < 0  =>  gains exceed losses under symmetric shock (ANTIFRAGILE)")
