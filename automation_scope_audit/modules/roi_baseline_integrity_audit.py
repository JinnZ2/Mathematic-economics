"""
roi_baseline_integrity_audit.py  —  C054-C058

Five claims about whether the automation ROI comparison is even
well-formed: degraded baselines, asymmetric measurement rigor for AI
vs human, productive operation rate (POR) instead of nameplate
capacity, redistributed coordination overhead, and deferred
maintenance liability that surfaces as catastrophic failure.

C054 ROI baseline is itself degraded by prior regulatory intervention
     (HOS detraining); automation is being compared to drivers the
     system created, not to the capable humans pre-detraining.
C055 AI degradation modes (bit flips, hallucination under load, value
     drift) lack measurement rigor equivalent to the FMCSA fatigue
     curves humans are regulated against; comparison is asymmetric.
C056 Productive Operation Rate (POR = productive_hours / available_hours)
     is the right metric, not nameplate "24/7" capacity. Autonomous
     POR typically 0.25-0.50; human POR ~0.85 within the regulated day.
C057 Coordination overhead is redistributed, not eliminated. Backend
     diagnostic + remote operator + mobile tech + customer service add
     up to a hidden cost that fragments across budget lines.
C058 Maintenance and inspection cost evasion creates deferred catastrophic
     failure liability; human pretrip / posttrip / in-motion sensing
     catches precursor failures that sensor packages miss.

License: CC0-1.0
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# C054  ROI baseline degraded by prior regulatory intervention
# ---------------------------------------------------------------------------

# Each row: prior intervention, year applied, capability-distribution
# delta (negative = compressed downward).
KNOWN_PRIOR_INTERVENTIONS: List[dict] = [
    {"intervention": "HOS_11hr_max",      "year": 2003,
     "capability_delta": -0.18, "domain": "fatigue"},
    {"intervention": "HOS_30min_break",   "year": 2013,
     "capability_delta": -0.12, "domain": "flow_state"},
    {"intervention": "ELD_mandate",       "year": 2017,
     "capability_delta": -0.08, "domain": "internal_calibration"},
    {"intervention": "drug_testing_program", "year": 1991,
     "capability_delta": -0.05, "domain": "operator_pool"},
]


def baseline_integrity_check(
    deployment_year: int = 2025,
    prior_interventions: List[dict] | None = None,
    intervention_decay_per_year: float = 0.02,
) -> dict:
    """Cumulative capability delta from interventions in effect at deployment year."""
    inv = prior_interventions or KNOWN_PRIOR_INTERVENTIONS
    cumulative = 0.0
    rows = []
    for x in inv:
        years_in_effect = max(0, deployment_year - int(x["year"]))
        decay_factor = (1.0 - intervention_decay_per_year) ** years_in_effect
        # Older interventions persist but decay slightly (some
        # adaptation occurs). Most of the delta sticks.
        effective_delta = x["capability_delta"] * max(0.5, decay_factor)
        cumulative += effective_delta
        rows.append({
            "intervention":     x["intervention"],
            "year":             x["year"],
            "years_in_effect":  years_in_effect,
            "raw_delta":        x["capability_delta"],
            "effective_delta":  effective_delta,
            "domain":           x["domain"],
        })
    return {
        "deployment_year":         deployment_year,
        "by_intervention":         rows,
        "cumulative_capability_delta": cumulative,
        "baseline_degraded":       cumulative < -0.10,
    }


def c054_verdict(deployment_year: int = 2025,
                 prior_interventions: List[dict] | None = None) -> dict:
    """C054: concern registers when cumulative capability delta < -10%."""
    res = baseline_integrity_check(deployment_year, prior_interventions)
    return {
        "claim_id":      "C054",
        **res,
        "threshold_met": res["baseline_degraded"],
        "falsifier":
            "ROI comparison conducted against an audited capable-driver "
            "baseline (pre-detraining capability distribution restored or "
            "estimated from international unregulated cohorts)",
    }


# ---------------------------------------------------------------------------
# C055  AI degradation modes lack equivalent measurement rigor
# ---------------------------------------------------------------------------

# Per-degradation-mode measurement maturity. Human fatigue modes are
# well-characterized; AI degradation modes typically are not.
HUMAN_FATIGUE_METRICS: List[dict] = [
    {"metric": "reaction_time_at_11h",   "measured": True,  "validated_under_24_7": True},
    {"metric": "decision_quality_curve", "measured": True,  "validated_under_24_7": True},
    {"metric": "error_rate_curve",       "measured": True,  "validated_under_24_7": True},
    {"metric": "recovery_time",          "measured": True,  "validated_under_24_7": True},
    {"metric": "circadian_phase_effect", "measured": True,  "validated_under_24_7": True},
]

AI_DEGRADATION_METRICS: List[dict] = [
    {"metric": "bit_flip_rate_under_24_7", "measured": False, "validated_under_24_7": False},
    {"metric": "hallucination_under_load", "measured": False, "validated_under_24_7": False},
    {"metric": "value_drift_long_horizon", "measured": False, "validated_under_24_7": False},
    {"metric": "decision_quality_curve",   "measured": False, "validated_under_24_7": False},
    {"metric": "recovery_protocol",        "measured": False, "validated_under_24_7": False},
    {"metric": "thermal_degradation_curve","measured": False, "validated_under_24_7": False},
]


def degradation_measurement_asymmetry(
    human_metrics: List[dict] | None = None,
    ai_metrics: List[dict] | None = None,
) -> dict:
    """Count metrics measured + validated for each substrate."""
    h = human_metrics or HUMAN_FATIGUE_METRICS
    a = ai_metrics or AI_DEGRADATION_METRICS
    h_meas = sum(1 for m in h if m.get("measured"))
    a_meas = sum(1 for m in a if m.get("measured"))
    h_val = sum(1 for m in h if m.get("validated_under_24_7"))
    a_val = sum(1 for m in a if m.get("validated_under_24_7"))
    return {
        "human_metrics_measured":      h_meas,
        "human_metrics_validated_247": h_val,
        "human_metric_count":          len(h),
        "ai_metrics_measured":         a_meas,
        "ai_metrics_validated_247":    a_val,
        "ai_metric_count":             len(a),
        "asymmetry_ratio":             (h_val / max(1, a_val)) if a_val > 0 else float("inf"),
    }


def c055_verdict(human_metrics: List[dict] | None = None,
                 ai_metrics: List[dict] | None = None) -> dict:
    """C055: concern registers when AI 24/7-validated metric count is 0 or asymmetry > 3x."""
    res = degradation_measurement_asymmetry(human_metrics, ai_metrics)
    return {
        "claim_id":      "C055",
        **res,
        "threshold_met": res["ai_metrics_validated_247"] == 0
                         or res["asymmetry_ratio"] > 3.0,
        "falsifier":
            "published audited AI degradation curves for bit-flip rate, "
            "hallucination under load, value drift, decision-quality curve, "
            "and recovery protocol, validated under continuous 24/7 operation",
    }


# ---------------------------------------------------------------------------
# C056  Productive Operation Rate (POR), not nameplate capacity
# ---------------------------------------------------------------------------

# Default non-productive overhead components for an autonomous deployment.
# Each row is hours per truck per day attributable to that activity.
DEFAULT_AUTONOMOUS_OVERHEAD: Dict[str, float] = {
    "pretrip_diagnostics_h":        0.75,
    "posttrip_diagnostics_h":       0.75,
    "charging_or_fueling_h":        3.00,
    "maintenance_h":                1.00,
    "interface_integration_h":      0.75,
    "cloud_diagnostic_latency_h":   0.40,
    "exception_resolution_h":       2.00,
}

DEFAULT_HUMAN_OVERHEAD: Dict[str, float] = {
    "pretrip_inspection_h":         0.50,
    "posttrip_inspection_h":        0.33,
    "fueling_h":                    0.30,
    "meals_breaks_h":               0.83,    # 30-min mandatory + 20-min meal
}


def productive_operation_rate(
    available_hours_per_day: float,
    overhead_hours_per_day: float,
) -> dict:
    """POR = (available - overhead) / available."""
    productive = max(0.0, available_hours_per_day - overhead_hours_per_day)
    por = productive / available_hours_per_day if available_hours_per_day else 0.0
    return {
        "available_hours_per_day": available_hours_per_day,
        "overhead_hours_per_day":  overhead_hours_per_day,
        "productive_hours_per_day": productive,
        "POR":                      por,
    }


def autonomous_por(overhead: Dict[str, float] | None = None) -> dict:
    """Autonomous deployment claimed 24h / day; real overhead reduces POR."""
    o = {**DEFAULT_AUTONOMOUS_OVERHEAD, **(overhead or {})}
    total_overhead = sum(o.values())
    res = productive_operation_rate(24.0, total_overhead)
    return {"overhead_breakdown": o, "available_hours_per_day": 24.0, **res}


def human_por(daily_window_h: float = 11.0,
              overhead: Dict[str, float] | None = None) -> dict:
    """Human driver POR within the regulated 11-hour window."""
    o = {**DEFAULT_HUMAN_OVERHEAD, **(overhead or {})}
    total_overhead = sum(o.values())
    res = productive_operation_rate(daily_window_h, total_overhead)
    return {"overhead_breakdown": o, **res}


def c056_verdict(autonomous_overhead: Dict[str, float] | None = None,
                 human_overhead: Dict[str, float] | None = None,
                 human_window_h: float = 11.0,
                 ) -> dict:
    """C056: concern registers when autonomous POR < 0.75 (nameplate misrepresents)."""
    a = autonomous_por(autonomous_overhead)
    h = human_por(human_window_h, human_overhead)
    return {
        "claim_id":            "C056",
        "autonomous":          a,
        "human":               h,
        "autonomous_POR":      a["POR"],
        "human_POR":           h["POR"],
        "POR_asymmetry":       h["POR"] - a["POR"],
        "threshold_met":       a["POR"] < 0.75,
        "falsifier":
            "autonomous deployment demonstrating POR > 0.75 sustained over "
            "3+ years, with maintenance, charging, exception resolution, "
            "and cloud diagnostic latency itemized and verified",
    }


# ---------------------------------------------------------------------------
# C057  Coordination overhead redistributed, not eliminated
# ---------------------------------------------------------------------------

# Default coordination cost lines per truck per day in USD.
DEFAULT_COORDINATION_COSTS = {
    "backend_support":            40.0,
    "maintenance_scheduling":     20.0,
    "exception_handling":         30.0,
    "interface_integration":      15.0,
    "remote_operator_fraction":   45.0,
    "software_maintenance":       12.0,
}

DEFAULT_DRIVER_EMBEDDED_COORDINATION_USD = 25.0   # share of $200/day wage
                                                  # attributable to coordination
                                                  # work (route choreography,
                                                  # customer comms, exception
                                                  # handling, fuel planning)


def coordination_overhead_share(
    autonomous_per_day_usd: Dict[str, float] | None = None,
    driver_embedded_coordination_usd: float = DEFAULT_DRIVER_EMBEDDED_COORDINATION_USD,
) -> dict:
    """Compare autonomous coordination stack to driver-embedded coordination."""
    a = {**DEFAULT_COORDINATION_COSTS, **(autonomous_per_day_usd or {})}
    auto_total = sum(a.values())
    return {
        "autonomous_breakdown":              a,
        "autonomous_coordination_per_day":   auto_total,
        "driver_embedded_coordination":      driver_embedded_coordination_usd,
        "ratio_autonomous_to_driver":        (auto_total /
                                               driver_embedded_coordination_usd
                                               if driver_embedded_coordination_usd
                                               else float("inf")),
    }


def c057_verdict(autonomous_per_day_usd: Dict[str, float] | None = None,
                 driver_embedded_coordination_usd: float = DEFAULT_DRIVER_EMBEDDED_COORDINATION_USD
                 ) -> dict:
    """C057: concern registers when autonomous coordination > 2x driver-embedded."""
    res = coordination_overhead_share(autonomous_per_day_usd,
                                       driver_embedded_coordination_usd)
    return {
        "claim_id":      "C057",
        **res,
        "threshold_met": res["ratio_autonomous_to_driver"] > 2.0,
        "falsifier":
            "audited per-truck-per-day coordination accounting showing "
            "autonomous coordination stack at less than the driver-embedded "
            "coordination cost it replaces",
    }


# ---------------------------------------------------------------------------
# C058  Maintenance / inspection externalization creates deferred liability
# ---------------------------------------------------------------------------

# Per-failure-mode cost when an undetected precursor fails catastrophically
# at highway speed. USD per event.
CATASTROPHIC_FAILURE_COSTS_USD = {
    "tire_blowout_highway":             150_000.0,
    "brake_failure_highway":            500_000.0,
    "coupling_failure":                 300_000.0,
    "load_shift_highway":               800_000.0,
    "engine_overheat":                   45_000.0,
    "electrical_fire":                  220_000.0,
    "fluid_leak_undetected":             90_000.0,
}


def deferred_maintenance_liability(
    annual_inspection_hours_eliminated: float,
    catastrophic_failure_rate_increase: float = 0.50,
    baseline_failure_rate_per_truck_year: float = 0.04,
    failure_costs_usd: Dict[str, float] | None = None,
    fleet_size: int = 50,
    lifecycle_years: int = 5,
) -> dict:
    """Estimate the deferred-liability premium from eliminating human inspection.

    Inputs:
      annual_inspection_hours_eliminated: hours/year of pretrip/posttrip/
        in-motion sensing eliminated per truck (typically ~250 for a
        deployment that replaces the driver's inspection role).
      catastrophic_failure_rate_increase: fractional increase in
        catastrophic failure rate when precursor detection is lost.
      baseline_failure_rate_per_truck_year: events per truck per year in
        the human-inspected baseline.
      failure_costs_usd: per-event cost table.
      fleet_size, lifecycle_years: scope for cost summation.
    """
    fcs = failure_costs_usd or CATASTROPHIC_FAILURE_COSTS_USD
    mean_cost = sum(fcs.values()) / len(fcs)
    baseline_events = baseline_failure_rate_per_truck_year * fleet_size * lifecycle_years
    delta_events = baseline_events * catastrophic_failure_rate_increase
    delta_cost = delta_events * mean_cost
    return {
        "fleet_size":                      fleet_size,
        "lifecycle_years":                 lifecycle_years,
        "annual_inspection_h_eliminated":  annual_inspection_hours_eliminated,
        "catastrophic_failure_rate_increase": catastrophic_failure_rate_increase,
        "baseline_events":                 baseline_events,
        "delta_events":                    delta_events,
        "mean_event_cost_usd":             mean_cost,
        "delta_cost_lifecycle_usd":        delta_cost,
        "delta_cost_per_truck_per_year":   (delta_cost /
                                              (fleet_size * lifecycle_years)
                                              if fleet_size and lifecycle_years
                                              else 0.0),
    }


def c058_verdict(annual_inspection_hours_eliminated: float = 250.0,
                 fleet_size: int = 50,
                 lifecycle_years: int = 5) -> dict:
    """C058: concern registers when delta cost per truck per year > $5,000."""
    res = deferred_maintenance_liability(
        annual_inspection_hours_eliminated,
        fleet_size=fleet_size,
        lifecycle_years=lifecycle_years)
    return {
        "claim_id":      "C058",
        **res,
        "threshold_met": res["delta_cost_per_truck_per_year"] > 5_000.0,
        "falsifier":
            "autonomous fleet documenting per-truck inspection / monitoring "
            "protocol equivalent to or stronger than DOT pretrip + posttrip "
            "+ in-motion sensing AND maintaining catastrophic failure rate "
            "parity with human-inspected fleet over 3+ years",
    }


if __name__ == "__main__":
    print("C054:", c054_verdict()["threshold_met"])
    print("C055:", c055_verdict()["threshold_met"])
    print("C056:", c056_verdict()["threshold_met"])
    print("C057:", c057_verdict()["threshold_met"])
    print("C058:", c058_verdict()["threshold_met"])
