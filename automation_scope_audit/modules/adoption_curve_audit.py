"""
adoption_curve_audit.py  —  C070, C071, C072

Three claims about how the gap between *popularity* (visible signals
the institution rewards) and *substrate health* (the underlying
physical / institutional reality) closes catastrophically at
predictable points on a timescale-invariant curve.

C070 Structural correctness is anti-correlated with popularity. What
     gets celebrated tracks extraction speed and concentration of
     control, not system resilience. Popular narratives at peak
     popularity coincide with peak hidden cost.
C071 Adoption curves follow an identical 4-phase thermodynamic shape
     regardless of timescale (3-month fashion through 80-year
     institutional). Curve: discovery -> adoption -> saturation ->
     collapse signal. Substrate metrics diverge from popularity
     metrics during phase 2; collapse becomes visible in phase 3.
C072 Institutions cannot see their own cycle because decision-maker
     tenure is shorter than the cycle timescale. Each generation
     makes the same structural bet (1960s "bigger = efficient" ->
     1990s "financialization = efficient" -> 2010s "AI = efficient"),
     sees early-phase metrics rising, retires before phase-3
     collapse. Successor declares "we learned" and bets again.

License: CC0-1.0
"""

import math
import statistics
from typing import Dict, List


# ---------------------------------------------------------------------------
# C070  Popularity-substrate divergence
# ---------------------------------------------------------------------------

# Default popularity-metric panel: weight per signal.
DEFAULT_POPULARITY_WEIGHTS: Dict[str, float] = {
    "github_stars":               1.0,
    "funding_rounds_usd":         1.5,
    "media_mentions":             0.8,
    "research_paper_citations":   1.0,
    "executive_endorsements":     1.2,
    "viral_social_media":         0.7,
}

# Default substrate-metric panel: weight per signal.
DEFAULT_SUBSTRATE_WEIGHTS: Dict[str, float] = {
    "energy_cost_per_unit_trend":         1.5,    # negative is healthy (decreasing)
    "failure_rate_trend":                 1.5,    # negative is healthy
    "resilience_to_disruption":           1.2,    # positive is healthy
    "human_skill_retention":              1.0,
    "biodiversity_substrate_health":      1.0,
    "knowledge_preservation":             1.0,
    "edge_case_robustness":               1.2,
}


def divergence_score(
    popularity_trend: Dict[str, float],     # signed rate per metric, e.g. +0.30 = +30%/yr
    substrate_trend: Dict[str, float],
    popularity_weights: Dict[str, float] | None = None,
    substrate_weights: Dict[str, float] | None = None,
) -> dict:
    """Weighted mean popularity trend vs weighted mean substrate trend.

    Convention: positive trend on popularity = popularity rising;
    positive trend on substrate = substrate IMPROVING; negative trend on
    substrate = substrate DEGRADING. Divergence registers when popularity
    rises while substrate degrades.
    """
    pw = {**DEFAULT_POPULARITY_WEIGHTS, **(popularity_weights or {})}
    sw = {**DEFAULT_SUBSTRATE_WEIGHTS, **(substrate_weights or {})}

    def weighted(trend: Dict[str, float], weights: Dict[str, float]) -> float:
        if not trend:
            return 0.0
        num = sum(trend.get(k, 0.0) * weights.get(k, 1.0) for k in trend)
        den = sum(weights.get(k, 1.0) for k in trend)
        return num / den if den else 0.0

    p_mean = weighted(popularity_trend, pw)
    s_mean = weighted(substrate_trend, sw)
    return {
        "popularity_trend_mean":  p_mean,
        "substrate_trend_mean":   s_mean,
        "divergence":             p_mean - s_mean,
        "popularity_up_substrate_down": p_mean > 0.10 and s_mean < -0.05,
    }


def c070_verdict(popularity_trend: Dict[str, float] | None = None,
                 substrate_trend: Dict[str, float] | None = None) -> dict:
    """C070: concern registers when popularity rises >10%/yr while substrate drops >5%/yr."""
    # Default trends reflect 2020-2026 AI deployment cohort: popularity
    # strongly up, substrate health declining (energy per token rising,
    # failure rate trend rising, resilience down, etc.).
    p_trend = popularity_trend or {
        "github_stars":             0.40,
        "funding_rounds_usd":       0.55,
        "media_mentions":           0.30,
        "research_paper_citations": 0.25,
        "executive_endorsements":   0.45,
        "viral_social_media":       0.30,
    }
    s_trend = substrate_trend or {
        "energy_cost_per_unit_trend":    -0.20,    # energy/unit rising (-20%/yr)
        "failure_rate_trend":            -0.15,
        "resilience_to_disruption":      -0.10,
        "human_skill_retention":         -0.12,
        "biodiversity_substrate_health": -0.08,
        "knowledge_preservation":        -0.06,
        "edge_case_robustness":          -0.10,
    }
    res = divergence_score(p_trend, s_trend)
    return {
        "claim_id":      "C070",
        **res,
        "threshold_met": res["popularity_up_substrate_down"],
        "falsifier":
            "popular framework / deployment achieving > 10%/year popularity "
            "growth AND > 5%/year substrate-health improvement over a "
            "5-year window, third-party audited",
    }


# ---------------------------------------------------------------------------
# C071  Adoption-curve thermodynamics
# ---------------------------------------------------------------------------

# Canonical 4-phase shape (normalized over [0, 1] timescale).
CANONICAL_PHASE_BOUNDARIES = [
    {"phase": 1, "name": "discovery",       "norm_t_lo": 0.00, "norm_t_hi": 0.25,
     "slope_sign": "+",  "second_derivative_sign": "+"},     # accelerating up
    {"phase": 2, "name": "adoption",        "norm_t_lo": 0.25, "norm_t_hi": 0.55,
     "slope_sign": "+",  "second_derivative_sign": "-"},     # rising, decelerating
    {"phase": 3, "name": "saturation",      "norm_t_lo": 0.55, "norm_t_hi": 0.80,
     "slope_sign": "+0", "second_derivative_sign": "-"},     # flat near peak
    {"phase": 4, "name": "collapse_signal", "norm_t_lo": 0.80, "norm_t_hi": 1.01,
     "slope_sign": "-",  "second_derivative_sign": "-"},     # declining
]

# Historical examples of the curve, with timescale and observed phases.
HISTORICAL_CURVE_EXAMPLES: List[dict] = [
    {"domain": "crocs_fashion",        "timescale_years":   8,
     "current_phase": 4, "narrative_at_peak": "ugly but comfortable"},
    {"domain": "iphone_smartphone",    "timescale_years":  18,
     "current_phase": 3, "narrative_at_peak": "every pocket"},
    {"domain": "aws_cloud_computing",  "timescale_years":  20,
     "current_phase": 3, "narrative_at_peak": "cloud is the future"},
    {"domain": "1980s_consolidation",  "timescale_years":  30,
     "current_phase": 4, "narrative_at_peak": "bigger is better"},
    {"domain": "1990s_financialization","timescale_years":  20,
     "current_phase": 4, "narrative_at_peak": "innovation solves risk"},
    {"domain": "2010s_AI_automation",  "timescale_years":  15,
     "current_phase": 2, "narrative_at_peak": "AI solves everything"},
    {"domain": "roman_empire",         "timescale_years": 300,
     "current_phase": 4, "narrative_at_peak": "Rome is eternal"},
    {"domain": "soviet_union",         "timescale_years":  70,
     "current_phase": 4, "narrative_at_peak": "catching up to West"},
]


def classify_phase(metric_time_series: List[float]) -> dict:
    """Classify position in the 4-phase curve from a metric time series.

    Heuristic: compute first-derivative sign (slope) and second-
    derivative sign (acceleration) from the most recent 5-point
    window of the time series.
    """
    if len(metric_time_series) < 5:
        return {"phase": 1, "name": "discovery", "note": "insufficient data; assuming early phase"}
    recent = metric_time_series[-5:]
    diffs = [recent[i + 1] - recent[i] for i in range(4)]
    slope = statistics.mean(diffs)
    second_diff = [diffs[i + 1] - diffs[i] for i in range(3)]
    accel = statistics.mean(second_diff)

    if slope > 0 and accel > 0:
        phase = 1
    elif slope > 0 and accel < 0:
        # Either adoption (clearly rising) or saturation (flat)
        if abs(slope) > 0.5 * abs(recent[-1]) / 5:    # heuristic rate threshold
            phase = 2
        else:
            phase = 3
    elif slope < 0:
        phase = 4
    else:
        phase = 3
    info = CANONICAL_PHASE_BOUNDARIES[phase - 1]
    return {
        "phase":             phase,
        "name":              info["name"],
        "slope":             slope,
        "acceleration":      accel,
        "recent_values":     recent,
    }


def curve_shape_match(
    series_a: List[float], series_b: List[float]
) -> dict:
    """Correlation of normalized cumulative metrics; >0.85 means same shape."""
    if len(series_a) < 3 or len(series_b) < 3:
        return {"shape_match": False, "reason": "insufficient data"}
    def normalize(s: List[float]) -> List[float]:
        n = len(s)
        if n < 2:
            return list(s)
        lo, hi = min(s), max(s)
        if hi <= lo:
            return [0.0] * n
        return [(x - lo) / (hi - lo) for x in s]
    # Resample to common length using linear interpolation
    na, nb = normalize(series_a), normalize(series_b)
    L = min(len(na), len(nb))
    sa = [na[int(i * (len(na) - 1) / (L - 1))] for i in range(L)]
    sb = [nb[int(i * (len(nb) - 1) / (L - 1))] for i in range(L)]
    mean_a, mean_b = sum(sa) / L, sum(sb) / L
    num = sum((sa[i] - mean_a) * (sb[i] - mean_b) for i in range(L))
    den_a = math.sqrt(sum((sa[i] - mean_a) ** 2 for i in range(L)))
    den_b = math.sqrt(sum((sb[i] - mean_b) ** 2 for i in range(L)))
    if den_a == 0 or den_b == 0:
        return {"shape_match": False, "reason": "flat series"}
    corr = num / (den_a * den_b)
    return {
        "correlation":   corr,
        "shape_match":   corr > 0.85,
    }


def c071_verdict(metric_time_series: List[float] | None = None) -> dict:
    """C071: concern registers when the metric is in phase 2-4 (saturation or later)."""
    series = metric_time_series or [
        1, 3, 8, 18, 35, 60, 95, 130, 158, 175, 182, 182, 180]
    phase = classify_phase(series)
    return {
        "claim_id":              "C071",
        "phase_classification":  phase,
        "historical_examples":   HISTORICAL_CURVE_EXAMPLES,
        "canonical_phases":      CANONICAL_PHASE_BOUNDARIES,
        "threshold_met":         phase["phase"] >= 2,
        "falsifier":
            "adoption-metric time series across 3+ domains at different "
            "timescales whose normalized curves do NOT match the canonical "
            "discovery -> adoption -> saturation -> collapse shape "
            "(curve_shape_match correlation < 0.85)",
    }


# ---------------------------------------------------------------------------
# C072  Institutional cycle blindness
# ---------------------------------------------------------------------------

# Each row: decision-maker class, typical tenure in years.
DEFAULT_TENURE_TABLE: Dict[str, float] = {
    "fortune_500_ceo":             7.0,
    "venture_capital_partner":    10.0,
    "academic_tenure_track":      35.0,
    "policy_administrator":        4.0,
    "board_director":              8.0,
    "consulting_partner":         15.0,
    "elected_official":            6.0,
    "founder_operator":           12.0,
}


def cycle_visibility_score(
    decision_maker_tenure_years: float,
    cycle_timescale_years: float,
) -> dict:
    """Fraction of the cycle visible during the decision-maker's tenure."""
    if cycle_timescale_years <= 0:
        return {"visibility": 1.0, "blind": False}
    visibility = min(1.0, decision_maker_tenure_years / cycle_timescale_years)
    return {
        "decision_maker_tenure_years": decision_maker_tenure_years,
        "cycle_timescale_years":       cycle_timescale_years,
        "visibility":                  visibility,
        "blind":                       visibility < 0.50,
    }


def c072_verdict(
    decision_maker_class: str = "fortune_500_ceo",
    cycle_timescale_years: float = 30.0,
    tenure_table: Dict[str, float] | None = None,
) -> dict:
    """C072: concern registers when decision-maker sees < 50% of cycle."""
    table = {**DEFAULT_TENURE_TABLE, **(tenure_table or {})}
    tenure = table.get(decision_maker_class, 10.0)
    res = cycle_visibility_score(tenure, cycle_timescale_years)
    return {
        "claim_id":      "C072",
        "decision_maker_class": decision_maker_class,
        **res,
        "tenure_table":  table,
        "threshold_met": res["blind"],
        "falsifier":
            "decision-maker class with documented track record of "
            "anticipating own institution's cycle collapse AND pivoting "
            "in advance, sustained over multiple cohorts",
    }


if __name__ == "__main__":
    print("C070:", c070_verdict()["threshold_met"])
    print("C071:", c071_verdict()["threshold_met"])
    print("C072 ceo / 30yr cycle:", c072_verdict()["threshold_met"])
    print("C072 academic / 30yr cycle:",
          c072_verdict("academic_tenure_track", 30.0)["threshold_met"])
