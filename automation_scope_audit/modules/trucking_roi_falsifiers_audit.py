"""
trucking_roi_falsifiers_audit.py  —  C084-C089

Six falsifiable claims targeting load-bearing assumptions in the
marketed autonomous-trucking ROI calculation. Each claim is a
structural assertion about what would need to be true for the payback
arithmetic to hold; each falsifier is a single sentence whose
satisfaction would retire the claim.

C084 Pilot ROI is conditional on pilot geometry. Numbers measured on
     fixed depot-to-pad corridors do not transfer to general deployment
     without re-measurement per geometry class; the marketing pitch
     extrapolates without re-measurement.
C085 Reported payback uses point-estimate input prices (diesel,
     electricity, fully-loaded labor, rare-earth, HD-map subscription)
     held static over the depreciation window. Historical coefficient
     of variation for those inputs is large enough that the implicit
     uncertainty band exceeds the reported payback margin.
C086 Claimed insurance premium reduction requires an underwriting
     actuarial table that does not yet exist; under <3 years of
     audited continuous-fleet operational data the underwriter must
     price an uncertainty premium structurally higher than the
     human-baseline rate.
C087 Depreciation schedule books a residual resale value for the
     autonomous-specific capex stack (sensor pack + on-board
     compute + software license + HD-map subscription + cab
     integration). No secondary market exists for that stack as a
     unit, and a buyer would also need access to the same fixed
     geometry; residual is effectively zero on that portion.
C088 Published pilot-program success rates aggregate only deployments
     still operational at reporting time. Failed pilots are dropped
     from the numerator, so the reported success rate overstates the
     base rate; survivorship-adjusted pilot success is far below the
     unadjusted figure.
C089 Reported payback periods (typically 5-7 years) exceed the
     autonomous-stack technological-obsolescence period. Sensor
     packages, ML model architectures, and HD-map standards refresh
     on a 2-3 year cycle; the ROI claim implicitly assumes the
     deployed stack remains state-of-the-art and competitive across
     the entire payback window.

License: CC0-1.0
"""

from typing import Dict, List
from statistics import pstdev, mean


# ---------------------------------------------------------------------------
# C084  Pilot-geometry extrapolation
# ---------------------------------------------------------------------------

# Geometry-class signatures used by the pilot vs deployment match check.
# Variance values are placeholders calibrated against the geometry
# tiers in scope_geometry.py (fixed / hybrid_viable / variable / chaotic).
DEFAULT_PILOT_GEOMETRY: Dict[str, float] = {
    "route_variance":            0.05,    # fixed depot-to-pad
    "destination_set_size":      4.0,
    "weather_envelope_span":     0.2,
    "surface_type_diversity":    0.1,
    "interface_partner_count":   3.0,
}

DEFAULT_DEPLOYMENT_GEOMETRY: Dict[str, float] = {
    "route_variance":            0.45,    # dispersed wellsite
    "destination_set_size":      80.0,
    "weather_envelope_span":     0.75,
    "surface_type_diversity":    0.7,
    "interface_partner_count":   40.0,
}


def pilot_deployment_mismatch(
    pilot: Dict[str, float] | None = None,
    deployment: Dict[str, float] | None = None,
) -> dict:
    """Per-dimension and aggregate mismatch between pilot and deployment geometry."""
    p = {**DEFAULT_PILOT_GEOMETRY, **(pilot or {})}
    d = {**DEFAULT_DEPLOYMENT_GEOMETRY, **(deployment or {})}
    per_dim = {}
    ratios = []
    for k in p:
        if k not in d:
            continue
        denom = max(abs(p[k]), 1e-9)
        ratio = abs(d[k] - p[k]) / denom
        per_dim[k] = ratio
        ratios.append(ratio)
    return {
        "per_dimension_mismatch": per_dim,
        "mean_mismatch":          mean(ratios) if ratios else 0.0,
        "max_mismatch":           max(ratios) if ratios else 0.0,
    }


def c084_verdict(pilot: Dict[str, float] | None = None,
                 deployment: Dict[str, float] | None = None) -> dict:
    """C084: concern registers when mean mismatch > 1.0 (deployment doubles pilot variance)."""
    res = pilot_deployment_mismatch(pilot, deployment)
    return {
        "claim_id":      "C084",
        **res,
        "threshold_met": res["mean_mismatch"] > 1.0,
        "falsifier":
            "audited per-geometry-class ROI measurements covering at least "
            "three distinct geometry classes spanning the deployment envelope, "
            "with payback numbers re-measured rather than extrapolated from "
            "the pilot corridor",
    }


# ---------------------------------------------------------------------------
# C085  Static input-price assumption
# ---------------------------------------------------------------------------

# Historical coefficient of variation (CV) of key inputs over a 7-year
# rolling window. CV figures are conservative 2018-2025 envelopes; each
# input can be overridden by an audited price series.
DEFAULT_INPUT_PRICE_CV: Dict[str, float] = {
    "diesel_per_gal":             0.35,
    "industrial_electricity_kwh": 0.18,
    "fully_loaded_driver_wage":   0.12,
    "rare_earth_index":           0.45,
    "hd_map_subscription":        0.20,
    "insurance_premium":          0.22,
    "rail_intermodal_rate":       0.25,
}


def payback_uncertainty_band(
    input_price_cv: Dict[str, float] | None = None,
    reported_payback_margin: float = 0.15,
) -> dict:
    """Compose per-input CVs into a deployment-level uncertainty band.

    Inputs are treated as independent; the deployment-level CV is the
    root-sum-square of the per-input CVs. If that aggregate CV exceeds
    the reported payback margin the point estimate is structurally
    underdetermined.
    """
    cv = {**DEFAULT_INPUT_PRICE_CV, **(input_price_cv or {})}
    rss = (sum(v * v for v in cv.values())) ** 0.5
    return {
        "per_input_cv":           cv,
        "aggregate_cv_rss":       rss,
        "reported_payback_margin": reported_payback_margin,
        "uncertainty_dominates":  rss > reported_payback_margin,
    }


def c085_verdict(input_price_cv: Dict[str, float] | None = None,
                 reported_payback_margin: float = 0.15) -> dict:
    """C085: concern registers when aggregate input CV exceeds the reported margin."""
    res = payback_uncertainty_band(input_price_cv, reported_payback_margin)
    return {
        "claim_id":      "C085",
        **res,
        "threshold_met": res["uncertainty_dominates"],
        "falsifier":
            "published ROI pro-forma carrying a documented Monte-Carlo or "
            "scenario band over the depreciation window for diesel, "
            "electricity, fully-loaded labor, rare-earth, HD-map "
            "subscription, and insurance, with the resulting payback band "
            "narrower than the reported margin",
    }


# ---------------------------------------------------------------------------
# C086  Insurance actuarial gap
# ---------------------------------------------------------------------------


def actuarial_table_maturity(
    years_of_continuous_fleet_data: float,
    audited_fleet_size: int,
    min_years_required: float = 3.0,
    min_fleet_required: int = 100,
) -> dict:
    """Estimate the underwriter uncertainty premium given current data."""
    years_gap = max(0.0, min_years_required - years_of_continuous_fleet_data)
    fleet_gap = max(0, min_fleet_required - audited_fleet_size)
    # Each missing year contributes ~20% uncertainty load; each missing
    # 100 trucks of pooled data contributes ~10%. Both compound.
    years_load = 0.20 * years_gap
    fleet_load = 0.10 * (fleet_gap / 100.0)
    uncertainty_premium = years_load + fleet_load
    return {
        "years_of_continuous_fleet_data":  years_of_continuous_fleet_data,
        "audited_fleet_size":              audited_fleet_size,
        "years_gap":                       years_gap,
        "fleet_gap":                       fleet_gap,
        "uncertainty_premium_fraction":    uncertainty_premium,
    }


def c086_verdict(years_of_continuous_fleet_data: float = 0.75,
                 audited_fleet_size: int = 30,
                 claimed_premium_reduction: float = 0.20) -> dict:
    """C086: concern registers when uncertainty load exceeds the claimed reduction."""
    res = actuarial_table_maturity(
        years_of_continuous_fleet_data, audited_fleet_size)
    return {
        "claim_id":      "C086",
        **res,
        "claimed_premium_reduction":    claimed_premium_reduction,
        "threshold_met":                res["uncertainty_premium_fraction"]
                                         > claimed_premium_reduction,
        "falsifier":
            "published audited actuarial table for autonomous freight, "
            "drawn from >= 3 years of continuous operational data across "
            ">= 100 trucks, supporting the claimed premium reduction at a "
            "regulated underwriter's confidence level",
    }


# ---------------------------------------------------------------------------
# C087  No autonomous-stack secondary market
# ---------------------------------------------------------------------------

# Capex split for an autonomous truck. Conventional residual at 7 years
# is well documented; autonomous-specific items have no secondary market.
DEFAULT_CAPEX_SPLIT_USD: Dict[str, float] = {
    "tractor_glider_conventional":      120_000.0,
    "sensor_pack":                       95_000.0,
    "on_board_compute":                  45_000.0,
    "software_license":                  60_000.0,
    "hd_map_subscription_prepaid":       25_000.0,
    "cab_integration_engineering":       35_000.0,
}

# Residual fractions assumed in the ROI model. Conventional tractor
# books ~25% residual; autonomous-specific items typically booked at
# 30-50% in pitches even though no secondary market clears them.
DEFAULT_RESIDUAL_FRACTIONS: Dict[str, float] = {
    "tractor_glider_conventional":      0.25,
    "sensor_pack":                       0.30,
    "on_board_compute":                  0.30,
    "software_license":                  0.40,
    "hd_map_subscription_prepaid":       0.30,
    "cab_integration_engineering":       0.30,
}

AUTONOMOUS_SPECIFIC_KEYS = (
    "sensor_pack",
    "on_board_compute",
    "software_license",
    "hd_map_subscription_prepaid",
    "cab_integration_engineering",
)


def residual_value_overstatement(
    capex: Dict[str, float] | None = None,
    booked_residual_fraction: Dict[str, float] | None = None,
) -> dict:
    """Compare booked residual to a market-tested residual.

    Autonomous-specific stack residual is forced to 0 under the C087
    structural premise: no clearing secondary market exists.
    """
    c = {**DEFAULT_CAPEX_SPLIT_USD, **(capex or {})}
    r = {**DEFAULT_RESIDUAL_FRACTIONS, **(booked_residual_fraction or {})}
    booked = sum(c[k] * r.get(k, 0.0) for k in c)
    market_tested = sum(
        c[k] * (0.0 if k in AUTONOMOUS_SPECIFIC_KEYS else r.get(k, 0.0))
        for k in c
    )
    overstatement_usd = booked - market_tested
    total_capex = sum(c.values())
    return {
        "capex_total_usd":          total_capex,
        "booked_residual_usd":      booked,
        "market_tested_residual_usd": market_tested,
        "residual_overstatement_usd": overstatement_usd,
        "overstatement_fraction_of_capex":
            overstatement_usd / total_capex if total_capex else 0.0,
    }


def c087_verdict(capex: Dict[str, float] | None = None,
                 booked_residual_fraction: Dict[str, float] | None = None) -> dict:
    """C087: concern registers when overstatement > 10% of total capex."""
    res = residual_value_overstatement(capex, booked_residual_fraction)
    return {
        "claim_id":      "C087",
        **res,
        "threshold_met": res["overstatement_fraction_of_capex"] > 0.10,
        "falsifier":
            "audited secondary-market clearing prices for the autonomous "
            "stack as a unit (sensor pack + on-board compute + software "
            "license + HD-map subscription + cab integration) demonstrating "
            "residual values matching those booked in the ROI pro-forma",
    }


# ---------------------------------------------------------------------------
# C088  Pilot survivorship bias
# ---------------------------------------------------------------------------

# Publicly documented autonomous-trucking pilot outcomes. Each row:
# program name, year of pilot, terminal status. Reporting bodies that
# aggregate "industry success" routinely drop the SHUTDOWN rows.
KNOWN_PILOT_OUTCOMES: List[dict] = [
    {"program": "Otto / Uber Freight",   "year": 2016, "status": "shutdown"},
    {"program": "Starsky Robotics",       "year": 2020, "status": "shutdown"},
    {"program": "Embark",                 "year": 2023, "status": "shutdown"},
    {"program": "Argo AI",                "year": 2022, "status": "shutdown"},
    {"program": "TuSimple_US",            "year": 2024, "status": "shutdown"},
    {"program": "Locomation",             "year": 2024, "status": "shutdown"},
    {"program": "Plus_de-SPAC",           "year": 2022, "status": "pivoted_or_scaled_back"},
    {"program": "Waymo Via",              "year": 2023, "status": "pivoted_or_scaled_back"},
    {"program": "Kodiak Robotics",        "year": 2025, "status": "ongoing"},
    {"program": "Aurora Innovation",      "year": 2025, "status": "ongoing"},
    {"program": "Gatik",                  "year": 2025, "status": "ongoing"},
    {"program": "Torc Robotics",          "year": 2025, "status": "ongoing"},
]


def survivorship_adjusted_success_rate(
    pilot_outcomes: List[dict] | None = None,
) -> dict:
    """Compute reported (ongoing-only) vs survivorship-adjusted success rate."""
    rows = pilot_outcomes or KNOWN_PILOT_OUTCOMES
    n_total = len(rows)
    n_ongoing = sum(1 for r in rows if r.get("status") == "ongoing")
    n_pivoted = sum(1 for r in rows if r.get("status") == "pivoted_or_scaled_back")
    n_shutdown = sum(1 for r in rows if r.get("status") == "shutdown")
    reported_success_rate = n_ongoing / max(1, n_ongoing)              # = 1.0 by selection
    survivorship_adjusted = n_ongoing / max(1, n_total)
    return {
        "n_total":                  n_total,
        "n_ongoing":                n_ongoing,
        "n_pivoted_or_scaled_back": n_pivoted,
        "n_shutdown":               n_shutdown,
        "reported_success_rate":    reported_success_rate,
        "survivorship_adjusted_success_rate": survivorship_adjusted,
        "selection_bias_delta":     reported_success_rate - survivorship_adjusted,
    }


def c088_verdict(pilot_outcomes: List[dict] | None = None,
                 selection_bias_threshold: float = 0.50) -> dict:
    """C088: concern registers when the selection-bias delta (reported - adjusted)
    exceeds the threshold — i.e. the published success rate overstates the
    base rate by more than the threshold in absolute terms."""
    res = survivorship_adjusted_success_rate(pilot_outcomes)
    return {
        "claim_id":      "C088",
        **res,
        "selection_bias_threshold":  selection_bias_threshold,
        "threshold_met":
            res["selection_bias_delta"] > selection_bias_threshold,
        "falsifier":
            "industry success-rate report that includes every publicly "
            "documented pilot launched in the last decade — shutdowns, "
            "pivots, and ongoing — in the denominator, with audited terminal "
            "status for each",
    }


# ---------------------------------------------------------------------------
# C089  Payback exceeds technological-obsolescence period
# ---------------------------------------------------------------------------

# Refresh / obsolescence cycle for each autonomous-stack component.
# Years are conservative public-disclosure envelopes; each item can be
# overridden by an audited refresh-cycle source.
DEFAULT_STACK_REFRESH_YEARS: Dict[str, float] = {
    "sensor_pack_lidar_camera_radar":  3.0,
    "on_board_compute_silicon":        2.5,
    "ml_model_architecture":           1.5,
    "hd_map_standard":                 2.0,
    "regulatory_software_baseline":    3.0,
}


def payback_vs_obsolescence(
    reported_payback_years: float,
    stack_refresh_years: Dict[str, float] | None = None,
) -> dict:
    """Compare reported payback to the minimum stack refresh cycle."""
    r = {**DEFAULT_STACK_REFRESH_YEARS, **(stack_refresh_years or {})}
    min_refresh = min(r.values()) if r else 0.0
    mean_refresh = mean(r.values()) if r else 0.0
    return {
        "reported_payback_years":          reported_payback_years,
        "per_component_refresh_years":     r,
        "min_refresh_years":               min_refresh,
        "mean_refresh_years":              mean_refresh,
        "payback_exceeds_min_refresh":     reported_payback_years > min_refresh,
        "payback_exceeds_mean_refresh":    reported_payback_years > mean_refresh,
    }


def c089_verdict(reported_payback_years: float = 6.0,
                 stack_refresh_years: Dict[str, float] | None = None) -> dict:
    """C089: concern registers when payback exceeds the mean refresh cycle."""
    res = payback_vs_obsolescence(reported_payback_years, stack_refresh_years)
    return {
        "claim_id":      "C089",
        **res,
        "threshold_met": res["payback_exceeds_mean_refresh"],
        "falsifier":
            "audited deployment that completed reported payback while "
            "running the originally-deployed sensor pack, on-board compute, "
            "ML architecture, and HD-map standard without mid-cycle refresh "
            "subsidized outside the ROI accounting",
    }


# ---------------------------------------------------------------------------
# standalone smoke run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for vf in (c084_verdict, c085_verdict, c086_verdict,
               c087_verdict, c088_verdict, c089_verdict):
        v = vf()
        print(f"{v['claim_id']}: threshold_met={v['threshold_met']}")
