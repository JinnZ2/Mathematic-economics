"""
institutional_dynamics_audit.py  —  C022, C023, C024

Beyond the physical scaling cost (C021), institutions of a certain scale
develop dynamics that bias the entire field of inquiry. Three coupled
mechanisms:

C022 (institutional lock-in / gatekeeping): an institution that has
invested capital in specific infrastructure / processes at scale N is
incentivized to defend that scale rather than optimize. It controls
funding and regulatory approval; projects that reinforce its scale get
funded, projects that show smaller scale is more efficient do not.

  Threshold: institution size > optimal_scale_point * 1.2.
  Falsifier: institution-backed research showing smaller scale is more
  efficient (rare because the institution funding the research is
  invested in scale).

C023 (knowledge exclusion): knowledge threatening institutional scale is
labeled "not scalable"; holders without institutional affiliation cannot
get funding; no funding -> no large-scale studies -> "no evidence" ->
excluded from policy -> regulatory approval goes to scale-dependent
solutions -> cycle reinforces.

  Threshold: substrate-exclusion-ratio = excluded_substrates / total
  substrates documented in field >= 0.5.
  Falsifier: substantive funded program studying decentralized /
  symbiotic / degraded-mode alternatives at parity with institution-
  scaled programs.

C024 (collapse cycle / accelerated brittleness): as an institution
grows past its optimum, internal coordination cost rises and adaptive
capacity falls. The institution's response to external variation is
to double down on the existing model; it becomes MORE brittle as it
grows. When failure comes, it cascades fast because the institution
cannot pivot.

  Empirical pattern: Roman Empire, Soviet Union, Blockbuster, Kodak,
  ICE-locked automotive, 2008 financial sector, ad-revenue-locked
  mega-scale tech.

  Threshold: adaptive_capacity_score <= 0.3 AND ratio_to_optimum > 1.5.
  Falsifier: large institution successfully adapts to fundamental
  market / resource constraint without collapse.

License: CC0-1.0
"""

from typing import Dict, List

try:
    from . import scaling_audit
except ImportError:        # running as a script, not a package member
    import scaling_audit  # type: ignore[no-redef]


# Default substrate inventory: empirical knowledge categories that are
# routinely funded by institutions vs systematically excluded as
# "not scalable". `excluded` is a boolean per category.
DEFAULT_SUBSTRATE_INVENTORY: List[dict] = [
    {"substrate": "centralized_AI_dispatch",            "excluded": False},
    {"substrate": "hyperscale_fleet_telemetry",         "excluded": False},
    {"substrate": "OEM_software_lock_in",               "excluded": False},
    {"substrate": "cloud_inference_infrastructure",     "excluded": False},
    {"substrate": "regulatory_capture_lobbying",        "excluded": False},

    {"substrate": "distributed_system_efficiency",      "excluded": True},
    {"substrate": "human_AI_symbiosis",                 "excluded": True},
    {"substrate": "degraded_mode_operation",            "excluded": True},
    {"substrate": "edge_case_resilience",               "excluded": True},
    {"substrate": "small_scale_optimization",           "excluded": True},
    {"substrate": "owner_operator_economics",           "excluded": True},
    {"substrate": "physical_redundancy_vs_software",    "excluded": True},
]


# Historical patterns for the collapse-cycle claim. Each carries:
#   institution: name
#   peak_scale_relative: scale relative to its optimum at peak (>1 = above)
#   phase_at_failure: 1-5 per the spec
#   adaptive_response_observed: whether the institution adapted or doubled-down
HISTORICAL_COLLAPSE_PATTERNS: List[dict] = [
    {"institution": "Roman Empire",         "peak_scale_relative": 6.5,
     "phase_at_failure": 5, "adaptive_response_observed": "doubled_down"},
    {"institution": "Soviet Union",         "peak_scale_relative": 4.2,
     "phase_at_failure": 5, "adaptive_response_observed": "doubled_down"},
    {"institution": "Blockbuster",          "peak_scale_relative": 3.8,
     "phase_at_failure": 5, "adaptive_response_observed": "doubled_down"},
    {"institution": "Kodak",                "peak_scale_relative": 4.5,
     "phase_at_failure": 5, "adaptive_response_observed": "doubled_down"},
    {"institution": "ICE_automotive_majors","peak_scale_relative": 5.1,
     "phase_at_failure": 4, "adaptive_response_observed": "partial"},
    {"institution": "Financial_2008",       "peak_scale_relative": 7.0,
     "phase_at_failure": 5, "adaptive_response_observed": "doubled_down"},
    {"institution": "Mega_tech_ad_revenue", "peak_scale_relative": 6.0,
     "phase_at_failure": 3, "adaptive_response_observed": "doubled_down"},
]


def c022_verdict(institution_size: int,
                 optimal_size: int | None = None,
                 scaling_coefficients: Dict[str, float] | None = None,
                 over_optimum_tolerance: float = 0.20,
                 ) -> dict:
    """Institutional lock-in / gatekeeping verdict.

    Threshold: institution size > optimal_size * (1 + over_optimum_tolerance).
    """
    if optimal_size is None:
        optimal_size = scaling_audit.optimal_fleet_size(
            scaling_coefficients)["optimal_fleet_size"]
    threshold_scale = optimal_size * (1.0 + over_optimum_tolerance)
    return {
        "claim_id":            "C022",
        "institution_size":    institution_size,
        "optimal_size":        optimal_size,
        "over_optimum_threshold": threshold_scale,
        "ratio_to_optimum":    institution_size / optimal_size
                                if optimal_size else float("inf"),
        "threshold_met":       institution_size > threshold_scale,
        "falsifier":
            "institution-backed research showing smaller scale is more "
            "efficient (rare because institution funding research is "
            "invested in scale)",
    }


def c023_verdict(substrate_inventory: List[dict] | None = None) -> dict:
    """Knowledge exclusion verdict.

    Threshold: at least half of documented substrates are excluded from
    institutional funding / publication / policy channels.
    """
    inv = substrate_inventory or DEFAULT_SUBSTRATE_INVENTORY
    total = len(inv)
    excluded = [s["substrate"] for s in inv if s.get("excluded", False)]
    included = [s["substrate"] for s in inv if not s.get("excluded", False)]
    exclusion_ratio = (len(excluded) / total) if total else 0.0
    return {
        "claim_id":         "C023",
        "total_substrates": total,
        "excluded_substrates": excluded,
        "included_substrates": included,
        "exclusion_ratio":  exclusion_ratio,
        "threshold_met":    exclusion_ratio >= 0.5,
        "falsifier":
            "substantive funded program studying decentralized / symbiotic / "
            "degraded-mode alternatives at parity with institution-scaled programs",
    }


def adaptive_capacity_score(institution_size: int,
                            optimal_size: int,
                            adaptive_response: str = "doubled_down",
                            ) -> float:
    """Map institution state onto a 0.0-1.0 adaptive capacity score.

    Baseline at-optimum: 1.0. Decreases linearly as ratio increases past
    1.5x optimum, hitting 0.0 at ~5x optimum. Modulated by the observed
    response pattern: doubling down -> halved, partial -> multiplier 0.6,
    successful adaptation -> multiplier 1.2 capped at 1.0.
    """
    if optimal_size <= 0:
        return 0.0
    ratio = institution_size / optimal_size
    if ratio <= 1.5:
        base = 1.0
    elif ratio >= 5.0:
        base = 0.0
    else:
        base = max(0.0, 1.0 - (ratio - 1.5) / 3.5)
    modifier = {
        "doubled_down":      0.5,
        "partial":           0.6,
        "successful_adapt":  1.2,
    }.get(adaptive_response, 0.8)
    return max(0.0, min(1.0, base * modifier))


def c024_verdict(institution_size: int,
                 optimal_size: int | None = None,
                 adaptive_response: str = "doubled_down",
                 scaling_coefficients: Dict[str, float] | None = None,
                 ) -> dict:
    """Collapse-cycle / brittleness verdict.

    Threshold: adaptive_capacity_score <= 0.3 AND ratio_to_optimum > 1.5.
    """
    if optimal_size is None:
        optimal_size = scaling_audit.optimal_fleet_size(
            scaling_coefficients)["optimal_fleet_size"]
    ratio = institution_size / optimal_size if optimal_size else float("inf")
    score = adaptive_capacity_score(institution_size, optimal_size,
                                     adaptive_response)
    if ratio <= 1.0:
        phase = "1_growth"
    elif ratio <= 1.5:
        phase = "2_maturity"
    elif ratio <= 2.5:
        phase = "3_lock_in"
    elif ratio <= 5.0:
        phase = "4_brittleness"
    else:
        phase = "5_collapse_pending"
    return {
        "claim_id":             "C024",
        "institution_size":     institution_size,
        "optimal_size":         optimal_size,
        "ratio_to_optimum":     ratio,
        "adaptive_capacity_score": score,
        "phase":                phase,
        "historical_patterns":  HISTORICAL_COLLAPSE_PATTERNS,
        "threshold_met":        score <= 0.3 and ratio > 1.5,
        "falsifier":
            "large institution successfully adapts to fundamental market / "
            "resource constraint without collapse",
    }


if __name__ == "__main__":
    print("C022 small (50):",     c022_verdict(50))
    print("C022 mega (50000):",   c022_verdict(50_000))
    print("C023:",                c023_verdict())
    print("C024 small (50):",     c024_verdict(50))
    print("C024 brittle (5000):", c024_verdict(5_000))
    print("C024 mega (50000):",   c024_verdict(50_000))
