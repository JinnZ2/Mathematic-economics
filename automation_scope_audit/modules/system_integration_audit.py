"""
system_integration_audit.py  —  C059

Automation is only thermodynamically efficient when (1) the total
all-categories energy input is *lower* than the human-integrated
baseline AND (2) resilience does not decrease. Conventional ROI
narratives compare *transport energy* only and ignore the cost of
replicating the other six functions a driver performs as integrated
side effects: condition monitoring, problem detection, micro-decision
making, coordination, self-maintenance, and adaptation.

The bee-pollination analogy. A bee's metabolic cost is already being
paid (the bee is foraging anyway); pollination is a side-effect of an
integrated agent doing what it evolved to do. Hand-pollination
replaces a free side-effect with an explicit, energy-expensive
operation. The result is energetically inferior even when the
hand-pollination produces the same fruit.

Same structure in trucking. A driver performs seven integrated
functions on a metabolic budget that's already being paid; an
autonomous deployment separates each function into its own
energy-hungry system (sensors, cloud backend, remote operators,
support technicians, mobile mechanics) whose energy cost is paid in
addition to the truck's fuel.

C059 Test: the autonomous deployment must satisfy BOTH
  (a) total_energy_autonomous_MJ_per_day < total_energy_human_MJ_per_day
  (b) resilience_autonomous >= resilience_human

The default daily energy budgets are calibrated to the worked example
in the user spec: human ~1,155 MJ/day; autonomous ~2,224 MJ/day (~2x).
Override via the function arguments.

Falsifier: autonomous deployment achieving >10% energy savings vs the
human-operated baseline AND maintaining or improving resilience to
edge cases, with all categories itemized and third-party audited.

License: CC0-1.0
"""

from typing import Dict


# Seven canonical functions an experienced human driver performs as
# integrated side effects of operating the truck. The autonomous
# deployment must replicate each one separately.
INTEGRATED_FUNCTIONS = [
    "transport",
    "condition_monitoring",
    "problem_detection",
    "micro_decision_making",
    "coordination",
    "self_maintenance",
    "adaptation_to_novel_conditions",
]


# Per-category daily energy budget for a human-integrated operation
# (MJ per truck per day). Calibrated to the user's worked example:
# 10 MJ metabolism + 1,140 MJ truck fuel + 5 MJ amortized maintenance
# = ~1,155 MJ/day for one truck operated by one driver.
DEFAULT_HUMAN_MJ_PER_DAY: Dict[str, float] = {
    "driver_metabolism":         10.0,
    "truck_fuel":             1_140.0,   # 30 gal x 38 MJ/gal
    "amortized_maintenance":      5.0,
}


# Per-category daily energy budget for the autonomous deployment. The
# truck still burns fuel (transport), but now every other function is
# externalized into a separately-powered system.
DEFAULT_AUTONOMOUS_MJ_PER_DAY: Dict[str, float] = {
    "truck_fuel":                1_140.0,
    "charging_electrical_infra":    100.0,
    "cloud_backend_share":          864.0,   # 50 trucks * 24 h * 10 kWh
    "remote_diagnostics_support":    50.0,
    "sensor_manufacturing_amort":    30.0,
    "facility_networking_amort":     40.0,
}


def integrated_daily_energy_budget(
    role: str = "human",
    overrides: Dict[str, float] | None = None,
) -> dict:
    """Return total daily MJ for `role` ('human' or 'autonomous')."""
    if role == "human":
        base = {**DEFAULT_HUMAN_MJ_PER_DAY, **(overrides or {})}
    elif role == "autonomous":
        base = {**DEFAULT_AUTONOMOUS_MJ_PER_DAY, **(overrides or {})}
    else:
        raise KeyError(f"unknown role: {role!r}")
    return {
        "role":                 role,
        "by_category_MJ":       base,
        "total_MJ_per_day":     sum(base.values()),
    }


def function_integration_score(
    autonomous_function_status: Dict[str, str] | None = None,
) -> dict:
    """Score how many of the 7 canonical functions are integrated
    side-effects (vs separated into their own energy-hungry systems).

    `autonomous_function_status` maps each function to one of:
        "integrated"   — same system handles it as side-effect (rare)
        "separated"    — its own subsystem with its own energy cost
        "outsourced"   — handed off to external party (cloud, contractor)

    Human-integrated baseline has all 7 functions in "integrated" state.
    Default autonomous deployment has 0 integrated, 7 separated.
    """
    default_status = {f: "separated" for f in INTEGRATED_FUNCTIONS}
    default_status["transport"] = "integrated"      # truck does its own driving
    status = {**default_status, **(autonomous_function_status or {})}
    integrated = sum(1 for v in status.values() if v == "integrated")
    separated = sum(1 for v in status.values() if v == "separated")
    outsourced = sum(1 for v in status.values() if v == "outsourced")
    return {
        "by_function":      status,
        "integrated_count": integrated,
        "separated_count":  separated,
        "outsourced_count": outsourced,
        "integration_score": integrated / len(INTEGRATED_FUNCTIONS),
    }


def resilience_proxy(role: str = "human",
                     integration_score: float = 0.0,
                     degraded_mode_capacity: float = 0.5) -> float:
    """Composite resilience proxy on [0, 1].

    Human integrated baseline: integration_score=1.0, degraded_mode=1.0
    -> resilience 1.0. Autonomous default: integration_score~0.14
    (only transport integrated), degraded_mode_capacity from C040
    (typically 0.05-0.30) -> resilience 0.10-0.20.
    """
    if role == "human":
        # Human integrated baseline doesn't depend on the AUTONOMOUS
        # integration score; pegged near 1.0 by construction.
        return 0.90
    return max(0.0, min(1.0,
                         0.5 * integration_score + 0.5 * degraded_mode_capacity))


def c059_verdict(
    human_overrides: Dict[str, float] | None = None,
    autonomous_overrides: Dict[str, float] | None = None,
    autonomous_function_status: Dict[str, str] | None = None,
    autonomous_degraded_mode_capacity: float = 0.10,
) -> dict:
    """Compose the C059 verdict.

    Threshold met (structural concern registers) when EITHER:
      - autonomous_total_MJ_per_day > human_total_MJ_per_day, OR
      - autonomous_resilience < human_resilience
    """
    h = integrated_daily_energy_budget("human", human_overrides)
    a = integrated_daily_energy_budget("autonomous", autonomous_overrides)
    fi = function_integration_score(autonomous_function_status)
    h_resilience = resilience_proxy("human")
    a_resilience = resilience_proxy("autonomous",
                                     integration_score=fi["integration_score"],
                                     degraded_mode_capacity=
                                     autonomous_degraded_mode_capacity)
    energy_inefficient = a["total_MJ_per_day"] > h["total_MJ_per_day"]
    resilience_loss = a_resilience < h_resilience
    return {
        "claim_id":           "C059",
        "human_budget":       h,
        "autonomous_budget":  a,
        "energy_ratio_autonomous_to_human":
            a["total_MJ_per_day"] / h["total_MJ_per_day"]
            if h["total_MJ_per_day"] else float("inf"),
        "function_integration": fi,
        "human_resilience":     h_resilience,
        "autonomous_resilience": a_resilience,
        "energy_inefficient":   energy_inefficient,
        "resilience_loss":      resilience_loss,
        "threshold_met":        energy_inefficient or resilience_loss,
        "falsifier":
            "autonomous deployment achieving >10% energy savings vs the "
            "human-operated baseline AND maintaining or improving "
            "resilience to edge cases, with all energy categories itemized "
            "and third-party audited",
    }


if __name__ == "__main__":
    r = c059_verdict()
    print(f"human MJ/day:     {r['human_budget']['total_MJ_per_day']:.0f}")
    print(f"autonomous MJ/day: {r['autonomous_budget']['total_MJ_per_day']:.0f}")
    print(f"ratio:            {r['energy_ratio_autonomous_to_human']:.2f}")
    print(f"integration:      {r['function_integration']['integration_score']:.2f}")
    print(f"resilience H:     {r['human_resilience']:.2f}")
    print(f"resilience A:     {r['autonomous_resilience']:.2f}")
    print(f"threshold_met:    {r['threshold_met']}")
