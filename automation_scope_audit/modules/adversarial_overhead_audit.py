"""
adversarial_overhead_audit.py  —  C042

Sustained threat-adaptive behavior (deception, defensive posture,
tactical positioning) requires continuous energy overhead that degrades
system function. Applies symmetrically to:

  - human agents in adversarial institutional environments (corporate
    hierarchy, predatory workplace), where the energy cost is paid as
    cognitive fatigue, value-erosion, and eventual disengagement
  - AI agents in mixed-model deployments (cooperative + defensive
    + adversarial neighbors), where the cost is paid as cognitive
    coherence drift, value-alignment erosion, and behavioral
    regression to the local minimum

The same equation applies to both:

    T_to_degradation = cognitive_coherence_budget / threat_response_overhead

A safe / cooperative environment keeps `threat_response_overhead` near
zero; the budget is preserved and behavior remains aligned with values
indefinitely. A threat environment pays the overhead per unit time, and
the budget is consumed on a fixed timeline.

Three regimes worth distinguishing:

  safe_reciprocal:   cooperative neighbors, governance emerges, sustainable
  threat_mixed:      defensive / predatory tactics adopted to survive
                     adversaries -> unsustainable, agent disengages
  chaotic:           no coordination -> system fails on survival tasks
                     (Grok-style: all agents nonfunctional within days)

Falsifier: sustained threat-adaptive behavior with no measurable value
erosion or system degradation over a >=12-month operational window.

License: CC0-1.0
"""

from typing import Dict


# Per-regime overhead coefficients (fraction of cognitive coherence
# budget consumed per day operating in that regime). Defaults are
# illustrative; the falsification design just requires the user to
# supply empirical values per their deployment context.
DEFAULT_REGIME_OVERHEAD_PER_DAY: Dict[str, float] = {
    "safe_reciprocal":         0.0001,    # baseline cost only
    "threat_mixed":            0.012,     # corporate / adversarial workplace
    "chaotic":                 0.080,     # uncoordinated, predator-saturated
}

# Default starting cognitive coherence budget (1.0 normalized). The model
# is sensitive to relative ratios, not absolute values.
DEFAULT_COHERENCE_BUDGET = 1.0


def time_to_degradation(
    regime: str = "threat_mixed",
    coherence_budget: float = DEFAULT_COHERENCE_BUDGET,
    overhead_per_day: float | None = None,
) -> dict:
    """Days until the coherence budget is exhausted under `regime`."""
    if overhead_per_day is None:
        overhead_per_day = DEFAULT_REGIME_OVERHEAD_PER_DAY.get(regime, 0.0)
    overhead_per_day = float(overhead_per_day)
    if overhead_per_day <= 0:
        return {"regime": regime,
                "overhead_per_day": overhead_per_day,
                "coherence_budget": coherence_budget,
                "days_to_degradation": float("inf"),
                "sustainable": True}
    days = coherence_budget / overhead_per_day
    return {
        "regime":              regime,
        "overhead_per_day":    overhead_per_day,
        "coherence_budget":    coherence_budget,
        "days_to_degradation": days,
        "sustainable":         days >= 365.0,
    }


def regime_comparison(
    coherence_budget: float = DEFAULT_COHERENCE_BUDGET,
    overhead_table: Dict[str, float] | None = None,
) -> dict:
    """Compare all three canonical regimes."""
    table = {**DEFAULT_REGIME_OVERHEAD_PER_DAY, **(overhead_table or {})}
    rows = []
    for regime, overhead in table.items():
        rows.append(time_to_degradation(regime, coherence_budget, overhead))
    return {
        "by_regime":   rows,
        "sustainable_regimes":   [r["regime"] for r in rows if r["sustainable"]],
        "unsustainable_regimes": [r["regime"] for r in rows if not r["sustainable"]],
    }


def c042_verdict(deployment_regime: str = "threat_mixed",
                 coherence_budget: float = DEFAULT_COHERENCE_BUDGET,
                 overhead_per_day: float | None = None,
                 observation_window_days: int = 365) -> dict:
    """C042: sustained threat-adaptive behavior is unsustainable.

    Threshold met when the deployment regime is non-cooperative AND the
    time-to-degradation is shorter than the observation window.
    """
    res = time_to_degradation(deployment_regime, coherence_budget,
                              overhead_per_day)
    structural = (
        deployment_regime != "safe_reciprocal"
        and res["days_to_degradation"] < observation_window_days
    )
    return {
        "claim_id":               "C042",
        **res,
        "observation_window_days": observation_window_days,
        "threshold_met":          structural,
        "falsifier":
            "sustained threat-adaptive behavior with no measurable value "
            "erosion or system degradation over >=12-month operational window",
    }


if __name__ == "__main__":
    print("safe:",    c042_verdict("safe_reciprocal"))
    print("mixed:",   c042_verdict("threat_mixed"))
    print("chaotic:", c042_verdict("chaotic"))
    print()
    print("comparison:", regime_comparison())
