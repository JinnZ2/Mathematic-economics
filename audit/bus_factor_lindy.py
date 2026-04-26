"""
bus_factor_lindy.py

Empirical survival prior for a business, combining two well-grounded
heuristics:

  BUS FACTOR  (software-engineering origin; aka "truck number")
    Number of people whose simultaneous loss would halt operations.
    Higher = more robust to personnel departure. Mathematically a
    minimum-cover problem on the knowledge-coverage bipartite graph;
    here we approximate from cross-training and succession-plan
    coverage observable in BusinessState.

  LINDY EFFECT  (Mandelbrot, popularized by Taleb)
    For non-perishable systems with power-law lifetime distributions,
    the future life expectancy is proportional to current age:
        P(survive at least t more | survived age T) = (T / (T + t))^alpha
    Empirically validated for technologies, books, and firms; alpha ~ 1
    is a common starting point. A 100-year-old firm has a much higher
    prior on continued existence than a 5-year-old firm, all else equal.

Combined:
  P(survive next horizon) ~ P_lindy(T, h) * (1 - personnel_departure_risk(h))

This complements business_resilience_framework.cascade_vulnerability_scan
by giving a forward-looking probability rather than a categorical rating.

License: CC0 1.0 Universal
"""

from typing import Dict

from business_resilience_framework import BusinessState, reference_profiles


# -----------------------------------------------------------------------------
# BUS FACTOR
# -----------------------------------------------------------------------------

def bus_factor_estimate(b: BusinessState) -> Dict[str, float]:
    """
    Approximate bus factor and concentration risk from observable signals:
      cross_trained_pct                  -- coverage redundancy
      succession_plan_coverage           -- documented backups
      knowledge_holders_within_5yr_retire -- fraction departing soon

    effective_bus_factor:
      headcount * cross_trained_pct * succession_plan_coverage
      (people with overlapping knowledge AND documented backups can
       substitute; unbacked knowledge holders count toward concentration
       risk, not coverage)

    critical_uncovered_count:
      headcount * (1 - cross_trained_pct) * (1 - succession_plan_coverage)
      (rough count of people whose departure breaks something with no
       documented substitute)

    departure_risk_5y:
      fraction of CRITICAL-uncovered headcount expected to leave in 5y
    """
    eff = b.headcount * b.cross_trained_pct * b.succession_plan_coverage
    uncovered = b.headcount * (1.0 - b.cross_trained_pct) * (1.0 - b.succession_plan_coverage)
    # critical knowledge holders departing soon
    departing = uncovered * b.knowledge_holders_within_5yr_retire
    return {
        "effective_bus_factor": round(max(1.0, eff), 1),
        "critical_uncovered_count": round(max(0.0, uncovered), 1),
        "critical_uncovered_pct": round(uncovered / b.headcount if b.headcount > 0 else 0.0, 3),
        "departing_within_5y_count": round(departing, 1),
        "rating": (
            "robust"   if eff >= 50 and uncovered / max(1, b.headcount) < 0.10 else
            "fragile"  if uncovered / max(1, b.headcount) < 0.30 else
            "critical"
        ),
    }


# -----------------------------------------------------------------------------
# LINDY EFFECT
# -----------------------------------------------------------------------------

def lindy_survival_probability(
    current_age_years: float,
    horizon_years: float,
    alpha: float = 1.0,
) -> float:
    """
    Conditional survival probability for a non-perishable system with
    power-law lifetime distribution:

        P(survive >= t more | survived T) = (T / (T + t))^alpha

    For alpha=1 this reduces to T/(T+t). Higher alpha means stronger
    Lindy effect (older systems much more robust). alpha < 1 weakens it.
    """
    if current_age_years <= 0:
        return 0.0
    if horizon_years <= 0:
        return 1.0
    return (current_age_years / (current_age_years + horizon_years)) ** alpha


def lindy_curve(current_age_years: float, max_horizon: int = 10, alpha: float = 1.0) -> Dict[int, float]:
    """Year-by-year survival probabilities out to max_horizon."""
    return {
        h: round(lindy_survival_probability(current_age_years, h, alpha), 4)
        for h in range(1, max_horizon + 1)
    }


# -----------------------------------------------------------------------------
# COMBINED SURVIVAL PRIOR
# -----------------------------------------------------------------------------

def combined_survival_prior(
    b: BusinessState,
    current_age_years: float,
    horizon_years: float = 5.0,
    lindy_alpha: float = 1.0,
) -> Dict[str, float]:
    """
    Combine Lindy survival prior with personnel-departure risk.
    Treats them as independent: the firm survives if the institution
    persists (Lindy) AND the critical knowledge base doesn't walk out
    over the horizon.

    departure_risk_over_horizon:
      assumes the 5-year departure fraction scales linearly with horizon
      (rough; conservative for short horizons, optimistic for long ones)
    """
    bus = bus_factor_estimate(b)
    lindy = lindy_survival_probability(current_age_years, horizon_years, lindy_alpha)

    # 5y departure -> per-horizon
    departure_fraction_5y = (
        bus["departing_within_5y_count"] / max(1.0, b.headcount)
    )
    departure_over_horizon = min(1.0, departure_fraction_5y * (horizon_years / 5.0))
    survival_personnel = 1.0 - departure_over_horizon

    combined = lindy * survival_personnel
    return {
        "lindy_survival": round(lindy, 4),
        "personnel_survival": round(survival_personnel, 4),
        "combined": round(combined, 4),
        "current_age_years": current_age_years,
        "horizon_years": horizon_years,
        "rating": (
            "high_confidence"   if combined >= 0.85 else
            "moderate"          if combined >= 0.65 else
            "fragile"           if combined >= 0.40 else
            "critical"
        ),
    }


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== LINDY SURVIVAL CURVES ===")
    for age in [1, 5, 25, 100]:
        curve = lindy_curve(age, max_horizon=10)
        sample = {h: curve[h] for h in (1, 5, 10)}
        print(f"  age={age:>3}y  P(survive +1y)={sample[1]}  +5y={sample[5]}  +10y={sample[10]}")

    print("\n=== BUS FACTOR ESTIMATES ===")
    for b in reference_profiles():
        bus = bus_factor_estimate(b)
        print(f"\n  {b.name}")
        print(f"    headcount:                 {b.headcount}")
        print(f"    effective_bus_factor:      {bus['effective_bus_factor']}")
        print(f"    critical_uncovered_count:  {bus['critical_uncovered_count']}  "
              f"({bus['critical_uncovered_pct']*100:.1f}% of headcount)")
        print(f"    departing_within_5y_count: {bus['departing_within_5y_count']}")
        print(f"    rating:                    {bus['rating']}")

    print("\n=== COMBINED SURVIVAL PRIOR (5-year horizon) ===")
    # Use illustrative ages: legacy firm = 70y, PE roll-up = 4y
    cases = [
        (reference_profiles()[0], 70.0),
        (reference_profiles()[1], 4.0),
    ]
    for b, age in cases:
        rep = combined_survival_prior(b, current_age_years=age, horizon_years=5.0)
        print(f"\n  {b.name}  (age={age}y)")
        print(f"    P(lindy survival, 5y):        {rep['lindy_survival']}")
        print(f"    P(personnel survival, 5y):    {rep['personnel_survival']}")
        print(f"    P(combined, 5y):              {rep['combined']}")
        print(f"    rating:                       {rep['rating']}")

    print("\n=== PRINCIPLE ===")
    print("  Lindy: P(survive +t | age T) = (T/(T+t))^alpha")
    print("  Bus factor: number of people whose loss halts the firm")
    print("  Both are empirical priors from large-population observation,")
    print("  not models. They give a forward-looking survival probability")
    print("  to complement the categorical ratings from cascade_vulnerability_scan.")
