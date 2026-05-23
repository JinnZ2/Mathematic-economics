"""
regulatory_dynamics_audit.py  —  C049-C053

Five claims about lowest-common-denominator (LCD) regulatory dynamics:
how regulation designed for median capability eliminates high-capability
operators, compresses system resilience, captures lowest-stakeholder
incentives, externalizes regulation onto rules that erode internal
self-regulation, and follows a predictable degradation cycle that
autonomous deployments are entering.

C049 LCD regulation selects against high-capability operators (HOS
     designed for median fatigue threshold eliminates 18-hour-capable
     drivers; replacement pool is below evolutionary baseline).
C050 System resilience requires capability diversity:
     R = (max_cap - min_cap) * n_operators * autonomy
     Compressing capability distribution collapses R toward zero.
C051 Regulatory capture by lowest-capability stakeholders: best
     performers don't advocate for capability-bracketing regulation;
     worst performers + insurance + government do.
C052 Externalized regulation degrades internal self-regulation across
     domains (HOS clock -> atrophied fatigue calibration; GPS ->
     atrophied spatial reasoning; school schedule -> atrophied hunger
     awareness; algorithmic finance -> atrophied economic judgment).
C053 Regulatory degradation cycle: same 4-phase pattern (deployment ->
     accident -> regulation -> compression -> brittleness -> collapse)
     repeats for automation; predict which phase a deployment is in.

License: CC0-1.0
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# C049  LCD regulation selects against capability diversity
# ---------------------------------------------------------------------------

# Stylized hours-of-service capability distribution for a driver pool.
# Each row: capability_hours_per_day, share_of_population.
# Below-baseline ranges reflect the modern post-detraining detsribution;
# above-baseline ranges reflect the evolved human envelope.
DEFAULT_CAPABILITY_DISTRIBUTION: List[dict] = [
    {"hours": 6.0,  "share": 0.05, "tier": "below_median"},
    {"hours": 8.0,  "share": 0.20, "tier": "below_median"},
    {"hours": 10.0, "share": 0.30, "tier": "median"},
    {"hours": 12.0, "share": 0.20, "tier": "above_median"},
    {"hours": 14.0, "share": 0.12, "tier": "above_median"},
    {"hours": 16.0, "share": 0.08, "tier": "above_median"},
    {"hours": 18.0, "share": 0.05, "tier": "above_median"},
]


def capability_selection_pressure(
    distribution: List[dict] | None = None,
    regulation_threshold_hours: float = 11.0,
) -> dict:
    """How much of the above-median pool is eliminated by an LCD cap?

    An operator with capability above the cap is functionally
    downregulated to the cap. Above-median operators experience this as
    a meaningful capability reduction; many self-select out of the field.
    """
    dist = distribution or DEFAULT_CAPABILITY_DISTRIBUTION
    total_share = sum(d["share"] for d in dist)
    above = sum(d["share"] for d in dist
                 if d["hours"] > regulation_threshold_hours)
    below = sum(d["share"] for d in dist
                 if d["hours"] <= regulation_threshold_hours)
    return {
        "regulation_threshold_hours":  regulation_threshold_hours,
        "share_above_threshold":       above / total_share if total_share else 0.0,
        "share_below_threshold":       below / total_share if total_share else 0.0,
        "share_capability_downregulated": above / total_share if total_share else 0.0,
    }


def c049_verdict(distribution: List[dict] | None = None,
                 regulation_threshold_hours: float = 11.0,
                 elimination_threshold: float = 0.30) -> dict:
    """C049: concern registers when LCD eliminates > threshold% of above-median operators."""
    res = capability_selection_pressure(distribution, regulation_threshold_hours)
    return {
        "claim_id":      "C049",
        **res,
        "threshold_met": res["share_capability_downregulated"] > elimination_threshold,
        "falsifier":
            "HOS regulation that accommodates capability diversity "
            "WITHOUT sacrificing safety for below-median operators",
    }


# ---------------------------------------------------------------------------
# C050  System resilience requires capability diversity
# ---------------------------------------------------------------------------

def resilience_score(max_capability_hours: float,
                     min_capability_hours: float,
                     n_operators: int,
                     operator_autonomy: float,
                     ) -> dict:
    """R = (max - min) * N * autonomy.

    `operator_autonomy` is on [0, 1]: 1.0 = full self-regulation;
    0.0 = fully externalized (regulation determines all operating
    parameters). A compressed system (max == min) has R = 0 regardless
    of N and autonomy.
    """
    diversity = max(0.0, max_capability_hours - min_capability_hours)
    autonomy = max(0.0, min(1.0, operator_autonomy))
    r = diversity * n_operators * autonomy
    return {
        "max_capability_hours":  max_capability_hours,
        "min_capability_hours":  min_capability_hours,
        "diversity":             diversity,
        "n_operators":           n_operators,
        "operator_autonomy":     autonomy,
        "resilience_score":      r,
    }


def c050_verdict(max_capability_hours: float = 11.0,
                 min_capability_hours: float = 11.0,
                 n_operators: int = 100,
                 operator_autonomy: float = 0.30,
                 baseline_resilience_per_operator: float = 4.0,
                 ) -> dict:
    """C050: concern registers when per-operator resilience falls below baseline."""
    res = resilience_score(max_capability_hours, min_capability_hours,
                            n_operators, operator_autonomy)
    per_op = res["resilience_score"] / n_operators if n_operators else 0.0
    return {
        "claim_id":               "C050",
        **res,
        "per_operator_resilience": per_op,
        "baseline_required":       baseline_resilience_per_operator,
        "threshold_met":           per_op < baseline_resilience_per_operator,
        "falsifier":
            "regulatory framework that sets a common minimum (not maximum) "
            "while preserving capability diversity above the floor",
    }


# ---------------------------------------------------------------------------
# C051  Regulatory capture by lowest-capability stakeholders
# ---------------------------------------------------------------------------

# Canonical stakeholder coalition that typically advocates for capability-
# bracketing safety regulation; weight reflects approximate political
# influence in the US trucking context. Numbers are illustrative.
DEFAULT_STAKEHOLDER_WEIGHTS: List[dict] = [
    {"stakeholder": "best_performers",      "advocates_regulation": False, "weight": 0.05},
    {"stakeholder": "median_performers",    "advocates_regulation": False, "weight": 0.20},
    {"stakeholder": "below_median_performers", "advocates_regulation": True,  "weight": 0.10},
    {"stakeholder": "insurance_industry",   "advocates_regulation": True,  "weight": 0.25},
    {"stakeholder": "regulatory_agencies",  "advocates_regulation": True,  "weight": 0.20},
    {"stakeholder": "carrier_executive_class", "advocates_regulation": True,  "weight": 0.20},
]


def regulatory_capture_score(
    stakeholders: List[dict] | None = None,
) -> dict:
    """Weighted share of stakeholders advocating capability-bracketing regs."""
    st = stakeholders or DEFAULT_STAKEHOLDER_WEIGHTS
    total = sum(s["weight"] for s in st)
    for_share = sum(s["weight"] for s in st if s.get("advocates_regulation"))
    against_share = total - for_share
    return {
        "stakeholders":      st,
        "for_share":         for_share / total if total else 0.0,
        "against_share":     against_share / total if total else 0.0,
        "capture_imbalance": (for_share - against_share) / total if total else 0.0,
    }


def c051_verdict(stakeholders: List[dict] | None = None) -> dict:
    """C051: concern registers when low-capability advocates > 60% of weight."""
    res = regulatory_capture_score(stakeholders)
    return {
        "claim_id":      "C051",
        **res,
        "threshold_met": res["for_share"] > 0.60,
        "falsifier":
            "regulatory framework whose voting / advisory structure is "
            "dominated by top-decile performers AND that increases "
            "capability diversity rather than compressing it",
    }


# ---------------------------------------------------------------------------
# C052  Externalized regulation degrades internal self-regulation
# ---------------------------------------------------------------------------

# Cross-domain spillover: when one substrate's self-regulation is
# externalized, neuroplasticity optimizes away the unused capability.
# Each row: domain, externalization_intensity (0..1), measurable
# atrophy_indicator.
CROSS_DOMAIN_EXTERNALIZATION: List[dict] = [
    {"domain": "driving_fatigue_management",
     "externalization": 0.90, "atrophy_indicator": "drivers cannot estimate fatigue without HOS clock"},
    {"domain": "spatial_navigation",
     "externalization": 0.95, "atrophy_indicator": "GPS-only users disoriented when device removed"},
    {"domain": "financial_decision_making",
     "externalization": 0.80, "atrophy_indicator": "Fed surveys: 57% cannot do basic math; spending awareness declining"},
    {"domain": "information_synthesis",
     "externalization": 0.85, "atrophy_indicator": "college students unable to evaluate sources"},
    {"domain": "circadian_sleep_regulation",
     "externalization": 0.70, "atrophy_indicator": "alarm-dependence; melatonin/medication for sleep onset"},
    {"domain": "child_development_judgment",
     "externalization": 0.75, "atrophy_indicator": "parents defer to institutional schooling for assessment"},
    {"domain": "real_time_decision_making",
     "externalization": 0.65, "atrophy_indicator": "wait for AI recommendation; decision latency rising"},
    {"domain": "hunger_satiety_regulation",
     "externalization": 0.55, "atrophy_indicator": "school-schedule cohorts report inability to recognize hunger"},
]


def self_regulation_atrophy(domains: List[dict] | None = None) -> dict:
    """Weighted mean externalization intensity across documented domains."""
    inv = domains or CROSS_DOMAIN_EXTERNALIZATION
    if not inv:
        return {"mean_externalization": 0.0, "by_domain": []}
    mean_ext = sum(d["externalization"] for d in inv) / len(inv)
    return {
        "by_domain":          inv,
        "mean_externalization": mean_ext,
    }


def c052_verdict(domains: List[dict] | None = None) -> dict:
    """C052: concern registers when mean externalization > 0.5 across multi-domain panel."""
    res = self_regulation_atrophy(domains)
    return {
        "claim_id":      "C052",
        **res,
        "threshold_met": res["mean_externalization"] > 0.5,
        "falsifier":
            "population with high regulatory externalization across the "
            "documented domains AND maintained high internal self-regulation "
            "capacity on validated tests",
    }


# ---------------------------------------------------------------------------
# C053  Regulatory degradation cycle - predict the phase
# ---------------------------------------------------------------------------

# 4-phase cycle observed in trucking + likely repeating in autonomous
# trucking. Each phase carries marker conditions.
CYCLE_PHASES = [
    {"phase": 1, "name": "minimal_regulation",
     "markers": ["best operators at full capability",
                  "some incidents from worst operators",
                  "mixed but mostly functional"]},
    {"phase": 2, "name": "regulation_arrives",
     "markers": ["regulation designed by lowest-capability advocates",
                  "all operators constrained to median",
                  "best downregulated; worst protected"]},
    {"phase": 3, "name": "post_regulation_claim",
     "markers": ["regulators claim safety improved",
                  "system is more fragile (lost high-cap buffer)",
                  "edge cases failing more often"]},
    {"phase": 4, "name": "spiral_to_collapse",
     "markers": ["more regulation in response to edge failures",
                  "each round compresses capability further",
                  "system approaches lowest-capability bound and collapses"]},
]


def degradation_cycle_phase(
    year_since_deployment: int,
    regulation_intensity: float,
    high_capability_share_remaining: float,
) -> dict:
    """Classify the deployment's position in the 4-phase cycle.

    Heuristic: pre-regulation -> phase 1; regulation arriving and
    high-capability share dropping -> phase 2; regulation in place
    and edge-failures rising -> phase 3; sustained compression with
    falling capacity -> phase 4.
    """
    if regulation_intensity < 0.2 and year_since_deployment < 5:
        phase = 1
    elif regulation_intensity < 0.6 and high_capability_share_remaining > 0.3:
        phase = 2
    elif regulation_intensity < 0.85 and high_capability_share_remaining > 0.1:
        phase = 3
    else:
        phase = 4
    return {
        "year_since_deployment":           year_since_deployment,
        "regulation_intensity":            regulation_intensity,
        "high_capability_share_remaining": high_capability_share_remaining,
        "phase":                           phase,
        "phase_name":                      CYCLE_PHASES[phase - 1]["name"],
        "markers":                         CYCLE_PHASES[phase - 1]["markers"],
    }


def c053_verdict(year_since_deployment: int = 5,
                 regulation_intensity: float = 0.70,
                 high_capability_share_remaining: float = 0.15) -> dict:
    """C053: concern registers in phases 2-4 (collapse trajectory)."""
    res = degradation_cycle_phase(year_since_deployment,
                                    regulation_intensity,
                                    high_capability_share_remaining)
    return {
        "claim_id":      "C053",
        **res,
        "cycle_phases":  CYCLE_PHASES,
        "threshold_met": res["phase"] >= 2,
        "falsifier":
            "autonomous deployment 10+ years past initial regulatory "
            "tightening that maintains capability diversity, edge-case "
            "robustness, and operator retention at pre-regulation levels",
    }


if __name__ == "__main__":
    print("C049:", c049_verdict()["threshold_met"])
    print("C050:", c050_verdict()["threshold_met"])
    print("C051:", c051_verdict()["threshold_met"])
    print("C052:", c052_verdict()["threshold_met"])
    print("C053:", c053_verdict()["threshold_met"])
