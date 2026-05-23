"""
cognitive_monoculture_audit.py  —  C018, C019

Replacing a heterogeneous human-AI division of labor with an AI-dominant
monoculture creates two coupled problems the steady-state efficiency
math ignores:

C018 (cognitive monoculture risk): when AI handles the routine task
surface, human domain expertise atrophies. Neuroplasticity optimizes
away unused skills; institutional memory fades; degraded-mode operation
disappears. When the AI hits a scenario outside its envelope, the
humans who would normally recover have lost the ability to do so.

  Worked example (aviation): autopilot handles cruise, pilots deskill
  over years, sensor fails or wind shear hits, manual recovery fails.

  Worked example (trucking): autonomous haul handles fixed routes,
  dispatchers deskill at alternate-route planning, anomalous weather
  closes the primary route, operation gridlocks.

C019 (energy cost of monoculture transition): a hybrid symbiosis state
(humans handle exceptions, AI handles routine) carries a steady-state
redundancy cost. The monoculture state appears cheaper at steady state
but pays a recovery cost when edge cases occur — humans must re-learn
the skill, AI must learn the new pattern, the system is offline during
both learning phases, and downstream costs cascade.

  Honest eROI must include:
      edge_case_frequency * (human_reskill_cost + AI_retrain_cost
                             + downtime_cost + cascade_cost)
  alongside routine-operation savings.

License: CC0-1.0
"""

from typing import Dict, List


# Empirical skill-atrophy curves from aviation autopilot studies (FAA
# 2013-2017 deskilling reports), surgical robotics, autonomous-vehicle
# safety-driver attention research, and a small literature on dispatch
# / yard-management deskilling. Numbers are fractional retention of the
# skill after `years` of AI handling that task class.
SKILL_ATROPHY_CURVES: Dict[str, List[float]] = {
    # year 0 = baseline, value at index k = retention after k years
    "manual_route_planning":      [1.0, 0.88, 0.74, 0.62, 0.52, 0.44, 0.38, 0.33],
    "anomaly_diagnosis":          [1.0, 0.84, 0.70, 0.58, 0.48, 0.40, 0.34, 0.29],
    "field_mechanical_repair":    [1.0, 0.92, 0.82, 0.71, 0.62, 0.55, 0.49, 0.45],
    "customer_negotiation":       [1.0, 0.95, 0.88, 0.81, 0.74, 0.68, 0.62, 0.58],
    "regulatory_field_judgment":  [1.0, 0.90, 0.78, 0.66, 0.56, 0.48, 0.42, 0.37],
    "degraded_mode_operation":    [1.0, 0.80, 0.62, 0.48, 0.38, 0.30, 0.24, 0.20],
}


# Default symbiosis vs monoculture cost stacks (annual USD per vehicle).
DEFAULT_SYMBIOSIS_COSTS = {
    "routine_operation":   42_000.0,
    "human_redundancy":    18_000.0,
    "exception_handling":   6_000.0,
    "skill_maintenance":    2_500.0,
}

DEFAULT_MONOCULTURE_COSTS = {
    "routine_operation":   28_000.0,   # AI handles routine cheaper
    "human_monitor":        6_500.0,   # passive monitor only
    "ai_training_amortized": 4_000.0,
    "skill_maintenance":      400.0,   # negligible — humans not exercising the skill
}


# Default edge-case profile: frequency per vehicle-year and recovery cost
# components in USD. Recovery cost includes human re-skilling (training
# cost + lost productivity during ramp), AI retraining (data labeling +
# compute + validation), system downtime, and downstream cascade.
DEFAULT_EDGE_CASE_PROFILE = {
    "annual_frequency_per_vehicle": 0.8,
    "human_reskill_cost_usd":       18_000.0,
    "ai_retrain_cost_usd":          45_000.0,
    "downtime_cost_per_event_usd":  22_000.0,
    "downstream_cascade_usd":       30_000.0,
    "recovery_failure_probability": 0.18,
    "recovery_failure_cost_usd":   250_000.0,
}


def skill_retention(skill: str, years: float) -> float:
    """Fractional retention of `skill` after `years` of AI-handled operation.

    Linear interpolation between integer years on the curve; clamps at the
    ends. Unknown skill raises KeyError.
    """
    curve = SKILL_ATROPHY_CURVES.get(skill)
    if curve is None:
        raise KeyError(f"no atrophy curve for skill: {skill!r}")
    if years <= 0:
        return curve[0]
    if years >= len(curve) - 1:
        return curve[-1]
    lo = int(years)
    hi = lo + 1
    frac = years - lo
    return curve[lo] * (1.0 - frac) + curve[hi] * frac


def weighted_domain_retention(skill_weights: Dict[str, float],
                              years: float) -> dict:
    """Trip-weighted average retention across the skill portfolio."""
    total_weight = sum(skill_weights.values())
    if total_weight <= 0:
        return {"weighted_retention": 1.0, "per_skill": {}}
    per_skill = {s: skill_retention(s, years) for s in skill_weights}
    weighted = sum(skill_weights[s] * per_skill[s] for s in skill_weights) \
        / total_weight
    return {
        "years":               years,
        "weighted_retention":  weighted,
        "per_skill":           per_skill,
        "skill_weights":       skill_weights,
    }


def edge_case_recovery_cost(profile: Dict[str, float] | None = None,
                            retention: float = 1.0) -> dict:
    """Annual expected recovery cost given retention level.

    Recovery cost scales inversely with retention: a 50%-retained human
    workforce costs roughly 2x more to bring back to operational
    competence than a 100%-retained workforce. The relationship is
    capped at 4x to avoid divergence as retention -> 0.
    """
    p = {**DEFAULT_EDGE_CASE_PROFILE, **(profile or {})}
    retention = max(0.05, min(1.0, retention))
    reskill_multiplier = min(4.0, 1.0 / retention)
    freq = p["annual_frequency_per_vehicle"]
    per_event = (p["human_reskill_cost_usd"] * reskill_multiplier
                 + p["ai_retrain_cost_usd"]
                 + p["downtime_cost_per_event_usd"]
                 + p["downstream_cascade_usd"])
    catastrophic = (p["recovery_failure_probability"]
                    * p["recovery_failure_cost_usd"])
    expected_per_event = per_event + catastrophic
    annual = freq * expected_per_event
    return {
        "edge_case_frequency_per_vehicle": freq,
        "per_event_recovery_cost_usd":     per_event,
        "expected_catastrophic_cost_usd":  catastrophic,
        "expected_per_event_total_usd":    expected_per_event,
        "annual_expected_cost_usd":        annual,
        "reskill_multiplier":              reskill_multiplier,
        "assumed_retention":               retention,
    }


def symbiosis_vs_monoculture(symbiosis: Dict[str, float] | None = None,
                             monoculture: Dict[str, float] | None = None,
                             edge_case_profile: Dict[str, float] | None = None,
                             retention: float = 0.45) -> dict:
    """Compare symbiosis steady-state vs monoculture-with-recovery cost."""
    sym = {**DEFAULT_SYMBIOSIS_COSTS, **(symbiosis or {})}
    mono = {**DEFAULT_MONOCULTURE_COSTS, **(monoculture or {})}
    sym_total = sum(sym.values())
    mono_steady = sum(mono.values())
    recovery = edge_case_recovery_cost(edge_case_profile, retention)
    mono_total = mono_steady + recovery["annual_expected_cost_usd"]
    apparent_savings = sym_total - mono_steady
    true_savings = sym_total - mono_total
    return {
        "symbiosis_total_usd":           sym_total,
        "monoculture_steady_state_usd":  mono_steady,
        "monoculture_with_recovery_usd": mono_total,
        "apparent_savings_usd":          apparent_savings,
        "true_savings_usd":              true_savings,
        "recovery_breakdown":            recovery,
        "monoculture_cheaper_with_recovery": mono_total < sym_total,
    }


def c018_verdict(skill_weights: Dict[str, float] | None = None,
                 years_into_transition: float = 5.0,
                 retention_threshold: float = 0.60) -> dict:
    """Cognitive monoculture risk verdict.

    Threshold: weighted domain retention below `retention_threshold`
    (default 60%) means the human workforce no longer has the capacity
    to recover when the AI fails — the structural concern registers.
    """
    weights = skill_weights or {
        "manual_route_planning":     0.20,
        "anomaly_diagnosis":         0.20,
        "field_mechanical_repair":   0.15,
        "customer_negotiation":      0.10,
        "regulatory_field_judgment": 0.15,
        "degraded_mode_operation":   0.20,
    }
    r = weighted_domain_retention(weights, years_into_transition)
    return {
        "claim_id":                "C018",
        "years_into_transition":   years_into_transition,
        "weighted_retention":      r["weighted_retention"],
        "per_skill_retention":     r["per_skill"],
        "retention_threshold":     retention_threshold,
        "threshold_met":           r["weighted_retention"] < retention_threshold,
        "falsifier":
            "deployment where AI-dominant system experiences edge-case "
            "failure AND humans successfully recover without catastrophic cost",
    }


def c019_verdict(skill_weights: Dict[str, float] | None = None,
                 years_into_transition: float = 5.0,
                 symbiosis: Dict[str, float] | None = None,
                 monoculture: Dict[str, float] | None = None,
                 edge_case_profile: Dict[str, float] | None = None) -> dict:
    """Energy / cost-of-recovery verdict.

    Threshold met when expected edge-case recovery cost (scaled by
    deskilling) exceeds the apparent monoculture savings — i.e. the
    monoculture is only cheaper if you ignore the recovery cost.
    """
    weights = skill_weights or {
        "manual_route_planning":     0.20,
        "anomaly_diagnosis":         0.20,
        "field_mechanical_repair":   0.15,
        "customer_negotiation":      0.10,
        "regulatory_field_judgment": 0.15,
        "degraded_mode_operation":   0.20,
    }
    retention = weighted_domain_retention(weights, years_into_transition)[
        "weighted_retention"]
    compare = symbiosis_vs_monoculture(symbiosis, monoculture,
                                       edge_case_profile, retention)
    return {
        "claim_id":                       "C019",
        "years_into_transition":          years_into_transition,
        "retention_used":                 retention,
        **compare,
        # Threshold: recovery cost > apparent savings, i.e. monoculture
        # is no longer cheaper once recovery is priced in.
        "threshold_met":                  (compare["recovery_breakdown"][
                                            "annual_expected_cost_usd"]
                                          > compare["apparent_savings_usd"]),
        "falsifier":
            "operational deployment where monoculture edge-case recovery "
            "cost is less than hybrid-redundancy steady-state cost",
    }


if __name__ == "__main__":
    print("C018 (year 5):", c018_verdict(years_into_transition=5.0))
    print("C019 (year 5):", c019_verdict(years_into_transition=5.0))
