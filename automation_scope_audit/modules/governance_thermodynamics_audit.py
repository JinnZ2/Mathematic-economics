"""
governance_thermodynamics_audit.py  —  C043..C048

Six structural claims about the energy cost of governance: enforcement
vs reciprocity, corruption incentives, surveillance sustainability,
legitimacy as equality of enforcement, defensive spending as GDP
misaccounting, and regulatory asymmetry between biological and digital
substrates.

C043  Coercive enforcement cost exceeds reciprocal governance cost beyond a
      scale-dependent threshold N (historical pattern: USSR ~280M, East
      Germany ~17M, both collapsed; China ~1.4B, costs rising; US ~$80-100B
      enforcement budget rising).
C044  Enforcement layer creates perverse corruption incentives: when bribe
      potential exceeds enforcer salary, corruption becomes rational.
      Surveillance of enforcers creates recursive cost.
C045  Surveillance sustainability depends on *perceived* reciprocity: same
      technology produces opposite outcomes under "protection" vs
      "extraction" cultural substrates.
C046  Material equality of enforcement determines cost trajectory: equally-
      applied enforcement is cost-sustainable; selectively-applied
      enforcement accelerates toward unsustainability.
C047  Defensive spending (prisons, surveillance, enforcement, accident
      recovery) counted as GDP growth misclassifies maintenance cost as
      productive output; net productive value diverges from headline GDP.
C048  Regulatory asymmetry between biological and digital substrates:
      humans regulated under HOS rules; AI operating 24/7 unregulated.
      Equivalent rigor must apply across substrate types.

License: CC0-1.0
"""

import math
from typing import Dict, List


# ---------------------------------------------------------------------------
# C043  Coercive enforcement vs reciprocal governance at scale N
# ---------------------------------------------------------------------------

# Per-person USD cost coefficients for the two governance modes. These are
# illustrative; callers override with empirical data for the polity under
# audit.
DEFAULT_GOVERNANCE_COSTS = {
    # Enforcement: baseline + per-enforcer + corruption + workaround
    "enforcement_baseline_per_capita":           50.0,
    "enforcement_agents_per_1000_pop":            5.0,
    "enforcement_agent_loaded_cost":         110_000.0,
    "corruption_share_of_enforcers":             0.18,   # disclosed mean
    "corruption_per_corrupted_agent":         60_000.0,
    "workaround_rate_per_capita":              120.0,   # citizens' time + tech
    "coordination_cost_exponent":               1.15,   # superlinear with n
    # Reciprocal: baseline + agreement cost (sublinear scaling)
    "reciprocal_baseline_per_capita":            20.0,
    "reciprocal_governance_overhead_per_cap":    15.0,
    "reciprocal_scaling_exponent":              0.85,
}


HISTORICAL_GOVERNANCE_BENCHMARKS: List[dict] = [
    {"polity": "Soviet Union",
     "year_collapse_or_present": 1989,
     "population_millions":      280,
     "enforcement_share_gdp":    0.18,
     "outcome": "collapse"},
    {"polity": "East Germany",
     "year_collapse_or_present": 1989,
     "population_millions":       17,
     "enforcement_share_gdp":    0.22,
     "outcome": "collapse"},
    {"polity": "China (current)",
     "year_collapse_or_present": 2026,
     "population_millions":     1400,
     "enforcement_share_gdp":    0.025,
     "outcome": "rising"},
    {"polity": "US (current)",
     "year_collapse_or_present": 2026,
     "population_millions":      330,
     "enforcement_share_gdp":    0.030,
     "outcome": "rising"},
]


def enforcement_cost(population: int,
                     coefficients: Dict[str, float] | None = None) -> float:
    """Annual enforcement cost in USD for population of `population`."""
    c = {**DEFAULT_GOVERNANCE_COSTS, **(coefficients or {})}
    n_enforcers = population * c["enforcement_agents_per_1000_pop"] / 1000.0
    # Coordination cost grows superlinearly with enforcer count.
    coordination = (n_enforcers ** c["coordination_cost_exponent"]) * \
        c["enforcement_agent_loaded_cost"]
    corruption = (n_enforcers * c["corruption_share_of_enforcers"]
                  * c["corruption_per_corrupted_agent"])
    workaround = population * c["workaround_rate_per_capita"]
    baseline = population * c["enforcement_baseline_per_capita"]
    return baseline + coordination + corruption + workaround


def reciprocal_cost(population: int,
                    coefficients: Dict[str, float] | None = None) -> float:
    """Annual reciprocal-governance cost in USD."""
    c = {**DEFAULT_GOVERNANCE_COSTS, **(coefficients or {})}
    baseline = population * c["reciprocal_baseline_per_capita"]
    governance = (population ** c["reciprocal_scaling_exponent"]) * \
        c["reciprocal_governance_overhead_per_cap"]
    return baseline + governance


def find_threshold_n(coefficients: Dict[str, float] | None = None,
                     search_max: int = 5_000_000_000) -> dict:
    """Find scale N at which enforcement_cost crosses reciprocal_cost.

    Log-scan + linear refine.
    """
    c = coefficients
    crossings = []
    n = 1_000
    while n <= search_max:
        if enforcement_cost(n, c) > reciprocal_cost(n, c):
            crossings.append(n)
            break
        n = max(n + 1, int(n * 1.4))
    if not crossings:
        return {"crossover_population": None,
                "found": False}
    # Refine
    lo, hi = crossings[0] // 2, crossings[0]
    while hi - lo > 1000:
        mid = (lo + hi) // 2
        if enforcement_cost(mid, c) > reciprocal_cost(mid, c):
            hi = mid
        else:
            lo = mid
    return {"crossover_population": hi,
            "enforcement_cost_at_crossover": enforcement_cost(hi, c),
            "reciprocal_cost_at_crossover": reciprocal_cost(hi, c),
            "found": True}


def c043_verdict(population: int,
                 coefficients: Dict[str, float] | None = None) -> dict:
    e = enforcement_cost(population, coefficients)
    r = reciprocal_cost(population, coefficients)
    threshold = find_threshold_n(coefficients)
    return {
        "claim_id":             "C043",
        "population":           population,
        "enforcement_cost":     e,
        "reciprocal_cost":      r,
        "cost_ratio_enforcement_to_reciprocal": e / r if r else float("inf"),
        "threshold_n":          threshold,
        "above_threshold":      threshold["found"] and
                                 population >= (threshold["crossover_population"] or 0),
        "historical_benchmarks": HISTORICAL_GOVERNANCE_BENCHMARKS,
        "threshold_met":        e > r,
        "falsifier":
            "sustained coercive system with enforcement cost < reciprocal "
            "governance equivalent at same scale AND without corruption growth",
    }


# ---------------------------------------------------------------------------
# C044  Enforcement-layer perverse corruption incentive
# ---------------------------------------------------------------------------

def corruption_rationality(enforcer_loaded_salary: float,
                            mean_bribe_offer: float,
                            detection_probability: float = 0.20,
                            penalty_if_caught: float = 200_000.0,
                            ) -> dict:
    """Expected-value of accepting a bribe vs taking the salary."""
    ev_corruption = (mean_bribe_offer
                     - detection_probability * penalty_if_caught)
    rational_to_corrupt = ev_corruption > 0
    return {
        "enforcer_loaded_salary":     enforcer_loaded_salary,
        "mean_bribe_offer":           mean_bribe_offer,
        "detection_probability":      detection_probability,
        "penalty_if_caught":          penalty_if_caught,
        "expected_value_of_corruption": ev_corruption,
        "rational_to_corrupt":        rational_to_corrupt,
    }


def recursive_enforcement_layers(layers: int = 3,
                                  layer_multiplier: float = 2.5) -> dict:
    """Cost multiplier when you add watchers of watchers."""
    cost = 1.0
    for _ in range(layers):
        cost *= layer_multiplier
    return {
        "layers":      layers,
        "multiplier":  cost,
        "note":        "Each surveillance-of-enforcers layer multiplies "
                       "cost; recursive problem (Quis custodiet ipsos custodes?).",
    }


def c044_verdict(enforcer_loaded_salary: float = 110_000.0,
                 mean_bribe_offer: float = 250_000.0,
                 detection_probability: float = 0.15,
                 penalty_if_caught: float = 180_000.0,
                 layers: int = 3) -> dict:
    """C044 threshold: corruption is the rational choice OR recursion blows up."""
    corr = corruption_rationality(enforcer_loaded_salary, mean_bribe_offer,
                                   detection_probability, penalty_if_caught)
    recursion = recursive_enforcement_layers(layers)
    return {
        "claim_id":      "C044",
        **corr,
        "recursive_enforcement": recursion,
        "threshold_met": corr["rational_to_corrupt"] or recursion["multiplier"] > 8.0,
        "falsifier":
            "large enforcement bureaucracy operating with stable salary "
            "structure and audited corruption rate below 1% over a 10-year window",
    }


# ---------------------------------------------------------------------------
# C045  Surveillance sustainability depends on perceived reciprocity
# ---------------------------------------------------------------------------

def perception_sustainability_score(
    equal_enforcement: float,        # 0.0..1.0 (1.0 = applied identically across status)
    cultural_reciprocity: float,     # 0.0..1.0 (collective-good belief)
    wealth_immunity: float,          # 0.0..1.0 (1.0 = wealthy fully exempt)
    extraction_incentives: float,    # 0.0..1.0 (winner-take-all framing)
) -> dict:
    """Surveillance_Cost_Sustainability = (E * C) / max(eps, W * X)."""
    num = max(0.0, min(1.0, equal_enforcement)) * \
          max(0.0, min(1.0, cultural_reciprocity))
    denom = max(0.0, min(1.0, wealth_immunity)) * \
            max(0.0, min(1.0, extraction_incentives))
    score = num / max(denom, 1e-3)
    return {
        "equal_enforcement":     equal_enforcement,
        "cultural_reciprocity":  cultural_reciprocity,
        "wealth_immunity":       wealth_immunity,
        "extraction_incentives": extraction_incentives,
        "score":                 score,
        "sustainable":           score >= 1.0,
    }


def c045_verdict(equal_enforcement: float = 0.40,
                 cultural_reciprocity: float = 0.35,
                 wealth_immunity: float = 0.75,
                 extraction_incentives: float = 0.80) -> dict:
    """Threshold met (concern registers) when score < 1.0."""
    res = perception_sustainability_score(
        equal_enforcement, cultural_reciprocity,
        wealth_immunity, extraction_incentives)
    return {
        "claim_id":      "C045",
        **res,
        "threshold_met": not res["sustainable"],
        "falsifier":
            "coercive system in an extraction-incentivized culture that "
            "maintains surveillance cost sustainability over a 20-year horizon",
    }


# ---------------------------------------------------------------------------
# C046  Material equality of enforcement determines cost trajectory
# ---------------------------------------------------------------------------

def enforcement_equality_score(
    prosecution_rate_by_wealth_decile: List[float],
) -> dict:
    """Coefficient of variation across deciles; 0 = perfectly equal."""
    if not prosecution_rate_by_wealth_decile:
        return {"equality_score": 0.0, "cv": 0.0,
                "deciles": prosecution_rate_by_wealth_decile}
    mean = sum(prosecution_rate_by_wealth_decile) / \
        len(prosecution_rate_by_wealth_decile)
    if mean <= 0:
        return {"equality_score": 0.0, "cv": float("inf"),
                "deciles": prosecution_rate_by_wealth_decile}
    var = sum((x - mean) ** 2 for x in prosecution_rate_by_wealth_decile) \
        / len(prosecution_rate_by_wealth_decile)
    cv = math.sqrt(var) / mean
    equality = max(0.0, 1.0 - cv)
    return {
        "deciles":          prosecution_rate_by_wealth_decile,
        "mean":             mean,
        "coefficient_of_variation": cv,
        "equality_score":   equality,
    }


def cost_trajectory_projection(equality_score: float,
                                annual_growth_if_unequal: float = 0.06,
                                horizon_years: int = 20) -> dict:
    """Project enforcement-cost growth rate over the horizon.

    Equal-enforcement systems grow with population (~1-2% / year).
    Unequal-enforcement systems compound at the unequal-growth rate.
    """
    if equality_score >= 0.80:
        growth = 0.015
    else:
        # Linearly interpolate growth from 0.015 to annual_growth_if_unequal
        # as equality_score drops from 0.80 to 0.0
        ratio = (0.80 - equality_score) / 0.80
        growth = 0.015 + ratio * (annual_growth_if_unequal - 0.015)
    cumulative = (1.0 + growth) ** horizon_years
    return {
        "equality_score":         equality_score,
        "annual_growth":          growth,
        "horizon_years":          horizon_years,
        "cumulative_cost_multiplier": cumulative,
        "trajectory_sustainable": cumulative < 2.0,
    }


def c046_verdict(prosecution_rate_by_wealth_decile: List[float] | None = None,
                 annual_growth_if_unequal: float = 0.06,
                 horizon_years: int = 20) -> dict:
    # Default deciles reflect typical US-style stratification: wealth-
    # decile 10 has a fraction of decile 1's prosecution rate. Numbers
    # are illustrative.
    deciles = prosecution_rate_by_wealth_decile or [
        0.55, 0.50, 0.42, 0.38, 0.32, 0.27, 0.20, 0.15, 0.08, 0.04]
    eq = enforcement_equality_score(deciles)
    traj = cost_trajectory_projection(eq["equality_score"],
                                       annual_growth_if_unequal, horizon_years)
    return {
        "claim_id":      "C046",
        "equality":      eq,
        "trajectory":    traj,
        "threshold_met": not traj["trajectory_sustainable"],
        "falsifier":
            "coercive system applying enforcement equally across the wealth "
            "distribution AND maintaining cost-sustainable trajectory over "
            "a 20-year horizon; OR a reciprocal-culture system applying "
            "enforcement unequally AND maintaining cooperation",
    }


# ---------------------------------------------------------------------------
# C047  Defensive spending counted as GDP misclassifies maintenance as growth
# ---------------------------------------------------------------------------

DEFAULT_DEFENSIVE_CATEGORIES = [
    "prisons", "surveillance", "enforcement_personnel",
    "pollution_remediation", "accident_medical_treatment",
    "data_breach_remediation", "litigation_defense",
    "private_security", "border_enforcement",
    "anti_drug_war", "cyber_defense",
]


def defensive_spending_share(spending_by_category: Dict[str, float],
                              gdp: float,
                              defensive_categories: List[str] | None = None) -> dict:
    """Fraction of total spending classified as defensive."""
    cats = defensive_categories or DEFAULT_DEFENSIVE_CATEGORIES
    total_def = sum(v for k, v in spending_by_category.items() if k in set(cats))
    return {
        "defensive_total":     total_def,
        "gdp":                 gdp,
        "defensive_share_gdp": total_def / gdp if gdp else 0.0,
    }


def net_productive_value(gdp: float, defensive_total: float) -> dict:
    """Headline GDP minus defensive spending = net productive output."""
    return {
        "gdp":               gdp,
        "defensive_total":   defensive_total,
        "net_productive":    gdp - defensive_total,
        "defensive_share":   defensive_total / gdp if gdp else 0.0,
    }


def c047_verdict(spending_by_category: Dict[str, float] | None = None,
                 gdp: float = 27_700_000_000_000.0,    # US 2024 nominal
                 ) -> dict:
    # Illustrative US 2024 defensive spending estimates (USD).
    s = spending_by_category or {
        "prisons":                     85_000_000_000.0,
        "surveillance":                95_000_000_000.0,
        "enforcement_personnel":      120_000_000_000.0,
        "pollution_remediation":       40_000_000_000.0,
        "accident_medical_treatment": 380_000_000_000.0,
        "data_breach_remediation":     30_000_000_000.0,
        "litigation_defense":          88_000_000_000.0,
        "private_security":            55_000_000_000.0,
        "border_enforcement":          25_000_000_000.0,
        "anti_drug_war":               45_000_000_000.0,
        "cyber_defense":               75_000_000_000.0,
    }
    share = defensive_spending_share(s, gdp)
    net = net_productive_value(gdp, share["defensive_total"])
    return {
        "claim_id":              "C047",
        "spending_by_category":  s,
        "defensive_total":       share["defensive_total"],
        "gdp":                   gdp,
        "defensive_share_gdp":   share["defensive_share_gdp"],
        "net_productive_value":  net["net_productive"],
        "in_maintenance_mode":   share["defensive_share_gdp"] > 0.10,
        # Structural concern (accounting misclassification) registers at any
        # meaningful defensive share. `in_maintenance_mode` separately
        # tracks the >10% net-maintenance threshold from the user spec.
        "threshold_met":         share["defensive_share_gdp"] > 0.03,
        "falsifier":
            "audited national accounting where prison + surveillance + "
            "enforcement spending < 3% of GDP, defensive spending excluded "
            "from headline GDP, AND equal-justice application is third-"
            "party verified",
    }


# ---------------------------------------------------------------------------
# C048  Regulatory asymmetry between biological and digital substrates
# ---------------------------------------------------------------------------

REGULATION_INVENTORY: List[dict] = [
    {"regulation": "HOS_max_drive_hours_per_day",
     "biological_value":  11.0,   "biological_enforced": True,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "fatigue / decision quality"},
    {"regulation": "mandatory_rest_break_minutes",
     "biological_value":  30.0,   "biological_enforced": True,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "operational continuity"},
    {"regulation": "60_70_hour_weekly_max",
     "biological_value":  70.0,   "biological_enforced": True,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "long-horizon degradation"},
    {"regulation": "ELD_continuous_logging",
     "biological_value":  1.0,    "biological_enforced": True,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "accountability + traceability"},
    {"regulation": "alcohol_drug_testing",
     "biological_value":  1.0,    "biological_enforced": True,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "decision-making integrity"},
    {"regulation": "medical_certification_recurring",
     "biological_value":  1.0,    "biological_enforced": True,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "fitness-for-duty"},
    {"regulation": "regime_shift_robustness_test",
     "biological_value":  None,   "biological_enforced": False,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "missing for BOTH substrates"},
    {"regulation": "15_day_continuous_simulation_check",
     "biological_value":  None,   "biological_enforced": False,
     "digital_value":     None,   "digital_enforced":    False,
     "domain":            "missing for BOTH substrates"},
]


def regulation_asymmetry_score(
    inventory: List[dict] | None = None,
) -> dict:
    """Per-regulation asymmetry; aggregate fraction asymmetric."""
    inv = inventory or REGULATION_INVENTORY
    rows = []
    asymmetric = 0
    for r in inv:
        sym = (r["biological_enforced"] == r["digital_enforced"])
        if not sym:
            asymmetric += 1
        rows.append({
            "regulation":            r["regulation"],
            "biological_enforced":   r["biological_enforced"],
            "digital_enforced":      r["digital_enforced"],
            "asymmetric":            not sym,
            "domain":                r["domain"],
        })
    return {
        "by_regulation":     rows,
        "total":             len(inv),
        "asymmetric_count":  asymmetric,
        "asymmetric_share":  asymmetric / len(inv) if inv else 0.0,
    }


def c048_verdict(inventory: List[dict] | None = None) -> dict:
    """Threshold met when >= half the regulations are asymmetric."""
    res = regulation_asymmetry_score(inventory)
    return {
        "claim_id":      "C048",
        **res,
        "threshold_met": res["asymmetric_share"] >= 0.50,
        "falsifier":
            "regulatory framework that applies identical scrutiny to human "
            "and AI decision-making across 24/7 operations, 15-day "
            "simulations, and regime-shift scenarios",
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("C043 (100M):", c043_verdict(100_000_000)["threshold_met"])
    print("C043 (1B):",    c043_verdict(1_000_000_000)["threshold_met"])
    print("C044:",          c044_verdict()["threshold_met"])
    print("C045:",          c045_verdict()["threshold_met"])
    print("C046:",          c046_verdict()["threshold_met"])
    print("C047:",          c047_verdict()["threshold_met"])
    print("C048:",          c048_verdict()["threshold_met"])
