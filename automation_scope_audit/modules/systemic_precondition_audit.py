"""
systemic_precondition_audit.py  —  C025, C026

Two coupled claims about the substrate that automation deployment
silently assumes:

C025 (Earth-system fragility): every large autonomous fleet is built on
preconditions — stable climate, stable supply chains, stable geopolitics,
stable power grid, stable satellite coverage, stable regulatory
environment, stable currency. If ANY precondition fails, the centralized
backend can no longer hold the deployment together, and thousands of
vehicles become simultaneously inoperable.

C026 (economic-model double-bind): the economic model the deployment
needs (continuous growth, stable capital access, stable labor markets,
stable demand, stable resource availability) is itself destabilized by
the deployment. Automation eliminates labor, reducing purchasing power,
reducing demand, breaking the growth thesis that justified the
deployment. Rare-earth concentration in a single jurisdiction scales as
fleet size scales. Backend electricity competes with grid stability
during the renewable transition.

Falsifier (C025): an autonomous deployment that remains operational
through a 24-hour regional power outage AND a satellite signal loss AND
a 72-hour regional internet disruption AND a 6-month critical-parts
supply break AND a geopolitical rare-earth embargo.

Falsifier (C026): an automation deployment that does not depend on
continuous growth, has supply-chain diversification adequate to absorb
any single jurisdiction's restriction, and demonstrates resilience to
economic shock without external bailout.

License: CC0-1.0
"""

import re
from typing import Dict, List


# Seven canonical Earth-system / institutional preconditions every
# autonomous deployment silently assumes. Each row carries:
#   annual_failure_probability: probability of a major disruption in the
#       precondition in any given year (2026-2036 trend-adjusted, not
#       historical 1990-2020).
#   cascade_severity: 0.0-1.0 fraction of fleet rendered inoperable by
#       a single failure event.
#   monitoring_indicator: a real-world signal an analyst could watch.
PRECONDITIONS: List[dict] = [
    {"name": "climate_stability",
     "annual_failure_probability": 0.35,
     "cascade_severity":           0.45,
     "monitoring_indicator":       "NOAA billion-dollar disaster count, route-day weather closure rate"},
    {"name": "supply_chain_stability",
     "annual_failure_probability": 0.55,
     "cascade_severity":           0.55,
     "monitoring_indicator":       "semiconductor lead times, rare-earth export licensing, freight insurance rates"},
    {"name": "geopolitics_stability",
     "annual_failure_probability": 0.40,
     "cascade_severity":           0.65,
     "monitoring_indicator":       "sanctions index, trade-route incident count, military buildup at chokepoints"},
    {"name": "power_grid_stability",
     "annual_failure_probability": 0.30,
     "cascade_severity":           0.85,
     "monitoring_indicator":       "NERC frequency excursion rate, renewable ramp incidents, regional brownout count"},
    {"name": "satellite_signal_stability",
     "annual_failure_probability": 0.15,
     "cascade_severity":           0.90,
     "monitoring_indicator":       "orbital debris count (Kessler), GPS jamming reports, LEO collision events"},
    {"name": "regulatory_stability",
     "annual_failure_probability": 0.50,
     "cascade_severity":           0.40,
     "monitoring_indicator":       "FMCSA / state DOT rulemaking cadence, EV mandate volatility, AI restriction proposals"},
    {"name": "currency_finance_stability",
     "annual_failure_probability": 0.20,
     "cascade_severity":           0.50,
     "monitoring_indicator":       "FX volatility, credit-spread blowouts, CBDC rollout pace, de-dollarization index"},
]


# Per-precondition sensitivity to underlying Earth-system trends, encoded
# as a dict of trend -> sensitivity multiplier (1.0 = baseline, >1.0 =
# additional pressure from that trend, <1.0 = trend offsets pressure).
EARTH_SYSTEM_SENSITIVITY_TABLE: Dict[str, Dict[str, float]] = {
    "climate_stability":          {"warming_trend": 1.8, "ocean_circulation_drift": 1.4,
                                    "biosphere_loss": 1.2, "renewable_transition": 1.1},
    "supply_chain_stability":     {"warming_trend": 1.3, "resource_nationalism": 1.7,
                                    "geopolitical_realignment": 1.5},
    "geopolitics_stability":      {"warming_trend": 1.2, "resource_nationalism": 1.6,
                                    "geopolitical_realignment": 2.0, "demographic_shift": 1.3},
    "power_grid_stability":       {"warming_trend": 1.4, "renewable_transition": 1.5,
                                    "AI_demand_surge": 1.6},
    "satellite_signal_stability": {"kessler_density": 1.8, "geopolitical_realignment": 1.5,
                                    "space_militarization": 1.4},
    "regulatory_stability":       {"warming_trend": 1.3, "AI_restrictions": 1.5,
                                    "labor_movement": 1.2, "geopolitical_realignment": 1.3},
    "currency_finance_stability": {"de_dollarization": 1.5, "CBDC_rollout": 1.3,
                                    "credit_cycle": 1.4},
}


# Default 2026-2036 trend intensities, on a 0.0-1.0 scale (1.0 = trend is
# fully realized within the window). These are illustrative defaults.
DEFAULT_EARTH_SYSTEM_TRENDS: Dict[str, float] = {
    "warming_trend":           0.75,
    "ocean_circulation_drift": 0.30,
    "biosphere_loss":          0.55,
    "renewable_transition":    0.65,
    "resource_nationalism":    0.70,
    "geopolitical_realignment": 0.65,
    "demographic_shift":       0.50,
    "AI_demand_surge":         0.85,
    "kessler_density":         0.35,
    "space_militarization":    0.40,
    "AI_restrictions":         0.55,
    "labor_movement":          0.45,
    "de_dollarization":        0.45,
    "CBDC_rollout":            0.40,
    "credit_cycle":            0.50,
}


# Degraded-mode capability per deployment type.
DEGRADED_MODE_CAPABILITY = {
    "human_driver_only":         {"no_connectivity":  True,  "no_satellites": True,
                                    "no_grid":         True,  "no_remote_compute": True,
                                    "verdict":         "FULL_DEGRADED_MODE"},
    "hybrid_with_safety_driver": {"no_connectivity":  True,  "no_satellites": True,
                                    "no_grid":         False, "no_remote_compute": False,
                                    "verdict":         "PARTIAL_DEGRADED_MODE"},
    "fully_remote_operator":     {"no_connectivity":  False, "no_satellites": False,
                                    "no_grid":         False, "no_remote_compute": False,
                                    "verdict":         "NO_DEGRADED_MODE"},
    "autonomous_no_driver":      {"no_connectivity":  False, "no_satellites": False,
                                    "no_grid":         False, "no_remote_compute": False,
                                    "verdict":         "NO_DEGRADED_MODE"},
}


# Patterns indicating a claim *does* acknowledge precondition assumptions.
PRECONDITION_ACKNOWLEDGMENT_PATTERNS = [
    r"\bassumes?\s+(?:stable|continuous|uninterrupted)",
    r"\b(?:depends?|conditional)\s+on\b",
    r"\bprecondition",
    r"\b(?:contingent|requires?)\s+(?:upon|on)",
    r"\bin\s+the\s+absence\s+of\s+(?:disruption|shock|cascade|failure)",
    r"\bbaseline\s+assumption",
]


# Five economic-model destabilization mechanisms the deployment itself
# creates. Each row: name, score_multiplier (used to combine into total),
# description.
ECONOMIC_MODEL_DESTABILIZATIONS: List[dict] = [
    {"mechanism": "labor_displacement_reduces_demand",
     "destabilization_strength": 0.80,
     "description": "Automation eliminates labor, reducing consumer "
                    "purchasing power, reducing demand for the freight "
                    "the automation moves."},
    {"mechanism": "capex_intensity_dependence_on_capital_markets",
     "destabilization_strength": 0.65,
     "description": "Backend infrastructure requires sustained capital "
                    "markets, but capital markets are fragile to "
                    "geopolitical shock."},
    {"mechanism": "rare_earth_concentration",
     "destabilization_strength": 0.85,
     "description": "Rare-earth concentration (one jurisdiction controls "
                    "~80% production) creates a supply vulnerability that "
                    "scales with fleet size."},
    {"mechanism": "backend_electricity_vs_grid",
     "destabilization_strength": 0.60,
     "description": "Backend electricity demand competes with grid "
                    "stability during the renewable transition."},
    {"mechanism": "circular_growth_dependency",
     "destabilization_strength": 0.75,
     "description": "Automation is justified by growth, but automation "
                    "itself breaks the growth model — circular."},
]


def enumerate_preconditions(deployment_type: str = "autonomous_no_driver"
                            ) -> List[dict]:
    """Return every precondition the deployment assumes."""
    return [dict(p) for p in PRECONDITIONS]


def earth_system_sensitivity(precondition: str,
                             trends: Dict[str, float] | None = None
                             ) -> dict:
    """Score how a given precondition responds to Earth-system trends.

    Returns a dict mapping trend name to (sensitivity * trend_intensity).
    Trends not relevant to the precondition omit from the result.
    """
    trends = trends or DEFAULT_EARTH_SYSTEM_TRENDS
    sensitivities = EARTH_SYSTEM_SENSITIVITY_TABLE.get(precondition, {})
    if not sensitivities:
        raise KeyError(f"no sensitivity table for precondition: {precondition!r}")
    contributions = {}
    total = 0.0
    for trend, mult in sensitivities.items():
        intensity = float(trends.get(trend, 0.0))
        score = mult * intensity
        contributions[trend] = score
        total += score
    return {
        "precondition":    precondition,
        "trend_contributions": contributions,
        "aggregate_pressure":  total,
    }


def _adjusted_failure_probability(precondition: dict,
                                  trends: Dict[str, float] | None,
                                  ) -> float:
    """Adjust base annual failure probability by Earth-system pressure."""
    base = float(precondition["annual_failure_probability"])
    try:
        pressure = earth_system_sensitivity(precondition["name"],
                                            trends)["aggregate_pressure"]
    except KeyError:
        pressure = 0.0
    # Cap the multiplier at 3x base; floor at 0.5x base.
    multiplier = max(0.5, min(3.0, 1.0 + pressure / 5.0))
    return max(0.0, min(0.99, base * multiplier))


def cascade_probability_10yr(deployment_scale: int,
                             precondition_list: List[str] | None = None,
                             earth_system_trends: Dict[str, float] | None = None,
                             window_years: int = 10) -> dict:
    """Probability that at least one critical precondition fails in window.

    P(at least one fails in `window_years`) =
        1 - prod_i ((1 - adjusted_p_i) ** window_years)

    Also returns the expected number of cascade events and the share-of-
    fleet expected to be impacted, weighted by per-event cascade severity.
    `deployment_scale` modulates cascade severity: larger fleets have
    higher backend concentration so a single failure affects a larger
    share.
    """
    trends = earth_system_trends or DEFAULT_EARTH_SYSTEM_TRENDS
    pre = [p for p in PRECONDITIONS
           if (precondition_list is None or p["name"] in set(precondition_list))]

    no_failure_prob = 1.0
    rows = []
    expected_events = 0.0
    expected_fleet_impact = 0.0
    scale_factor = max(0.5, min(1.5, (deployment_scale / 1000.0) ** 0.25))
    for p in pre:
        adj = _adjusted_failure_probability(p, trends)
        no_failure_prob *= (1.0 - adj) ** window_years
        events = adj * window_years
        severity = p["cascade_severity"] * scale_factor
        expected_events += events
        expected_fleet_impact += events * severity
        rows.append({
            "precondition":         p["name"],
            "adjusted_annual_prob": adj,
            "expected_events_10yr": events,
            "cascade_severity_scaled": severity,
        })

    return {
        "deployment_scale":         deployment_scale,
        "window_years":             window_years,
        "preconditions":            rows,
        "p_no_failure":             no_failure_prob,
        "p_at_least_one_failure":   1.0 - no_failure_prob,
        "expected_events_in_window": expected_events,
        "expected_cumulative_fleet_impact": expected_fleet_impact,
    }


def degraded_mode_capability(deployment_type: str = "autonomous_no_driver"
                             ) -> dict:
    """Can the system operate if preconditions partially fail?"""
    if deployment_type not in DEGRADED_MODE_CAPABILITY:
        raise KeyError(f"unknown deployment_type: {deployment_type!r}; "
                       f"valid: {sorted(DEGRADED_MODE_CAPABILITY)}")
    return {
        "deployment_type": deployment_type,
        **DEGRADED_MODE_CAPABILITY[deployment_type],
    }


def precondition_stability_assumption_test(claim: str) -> dict:
    """Does the claim explicitly acknowledge precondition assumptions?

    Returns the matches and a boolean `acknowledged`. If False, the claim
    is effectively asserting stability without testing it — which makes
    C025 / C026 analysis applicable.
    """
    text = claim.lower()
    hits = [m.group(0) for p in PRECONDITION_ACKNOWLEDGMENT_PATTERNS
            for m in re.finditer(p, text, flags=re.IGNORECASE)]
    return {
        "claim":         claim,
        "matches":       hits,
        "acknowledged":  bool(hits),
    }


def economic_model_double_bind(mechanisms: List[dict] | None = None) -> dict:
    """Score the destabilization-from-deployment mechanisms."""
    mech = mechanisms or ECONOMIC_MODEL_DESTABILIZATIONS
    total_strength = sum(m["destabilization_strength"] for m in mech)
    active_count = sum(1 for m in mech if m["destabilization_strength"] >= 0.5)
    return {
        "mechanisms":      mech,
        "active_count":    active_count,
        "total_strength":  total_strength,
        "double_bind_present": active_count >= 3,
    }


def c025_verdict(deployment_scale: int,
                 deployment_type: str = "autonomous_no_driver",
                 claim_text: str = "",
                 earth_system_trends: Dict[str, float] | None = None,
                 window_years: int = 10,
                 ) -> dict:
    """Earth-system fragility verdict.

    Threshold logic by degraded-mode capability:
      NO_DEGRADED_MODE     -> concern registers whenever p_any >= 0.5.
                              (an autonomous-no-driver deployment cannot
                              absorb the precondition failure that is
                              statistically near-certain in the window)
      PARTIAL_DEGRADED_MODE -> concern registers when expected cumulative
                              fleet impact > 1.0 (multiple full
                              fleet-equivalents knocked out).
      FULL_DEGRADED_MODE    -> concern does not register. Human-driver
                              systems route around precondition failures
                              and the claim does not apply.
    """
    casc = cascade_probability_10yr(deployment_scale, None,
                                    earth_system_trends, window_years)
    degraded = degraded_mode_capability(deployment_type)
    ackn = precondition_stability_assumption_test(claim_text)
    expected_impact = casc["expected_cumulative_fleet_impact"]
    p_any = casc["p_at_least_one_failure"]
    verdict_kind = degraded["verdict"]
    if verdict_kind == "NO_DEGRADED_MODE":
        structural_concern = p_any >= 0.5
    elif verdict_kind == "PARTIAL_DEGRADED_MODE":
        structural_concern = expected_impact > 1.0
    else:
        structural_concern = False
    return {
        "claim_id":              "C025",
        "deployment_scale":      deployment_scale,
        "deployment_type":       deployment_type,
        "cascade_analysis":      casc,
        "degraded_mode":         degraded,
        "acknowledgment":        ackn,
        "expected_cumulative_fleet_impact": expected_impact,
        "p_at_least_one_failure": p_any,
        "threshold_met":         structural_concern,
        "falsifier":
            "autonomous deployment that remains operational through a 24-hour "
            "regional power outage AND satellite signal loss AND 72-hour "
            "regional internet disruption AND 6-month critical-parts supply "
            "break AND geopolitical rare-earth embargo",
    }


def c026_verdict(claim_text: str = "",
                 mechanisms: List[dict] | None = None,
                 ) -> dict:
    """Economic-model double-bind verdict.

    Threshold: three or more of the five destabilization mechanisms are
    structurally present.
    """
    bind = economic_model_double_bind(mechanisms)
    ackn = precondition_stability_assumption_test(claim_text)
    return {
        "claim_id":              "C026",
        "destabilization_count": bind["active_count"],
        "total_strength":        bind["total_strength"],
        "mechanisms":            bind["mechanisms"],
        "acknowledgment":        ackn,
        "double_bind_present":   bind["double_bind_present"],
        "threshold_met":         bind["double_bind_present"],
        "falsifier":
            "automation deployment that does not depend on continuous growth, "
            "has supply-chain diversification adequate to absorb any single "
            "jurisdiction's restriction, and demonstrates resilience to "
            "economic shock without external bailout",
    }


if __name__ == "__main__":
    print("C025 megafleet (50000):",
          c025_verdict(50_000, "autonomous_no_driver",
                        claim_text="At scale we deliver 12% efficiency"))
    print()
    print("C025 small human (50):",
          c025_verdict(50, "human_driver_only",
                        claim_text="depends on diesel supply and DOT permits"))
    print()
    print("C026 generic:", c026_verdict())
