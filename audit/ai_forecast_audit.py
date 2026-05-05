# ai_forecast_audit.py
#
# AI_FORECAST_AUDIT_2026
#
# Two-part audit framework for institutional AI economic forecasts.
#
# Part 1: Forecast accuracy comparison against independent public ground truth
# (BLS, Census, court bankruptcy data, Federal Reserve raw data).
# Avoids institutional cross-referencing where bias compounds.
#
# Part 2: Computational burden quantification — translates compute hours,
# labor hours, and infrastructure investment into human-equivalent
# research years. Used to demolish the "AI needs more time" excuse.
#
# Output: forecast accuracy ratio, error direction, systematic bias
# detection, compute-to-accuracy ratio, equivalent research years
# invested per percentage point of forecast accuracy.
#
# License: CC0 1.0 Universal

from dataclasses import dataclass
from typing import Dict, List, Optional


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ForecastRecord:
    source_institution: str            # e.g., "McKinsey", "Federal Reserve"
    forecast_title: str                # short label
    forecast_date: str                 # ISO date when published
    horizon_years: float               # forecast horizon in years
    target_variable: str               # e.g., "automation_displacement_pct"
    predicted_value: float
    predicted_confidence_pct: float    # institution's stated confidence
    direction_of_error_if_wrong: Optional[str] = None
    citation_url: Optional[str] = None


@dataclass
class GroundTruthRecord:
    source: str                        # e.g., "BLS public release"
    target_variable: str
    actual_value: float
    measurement_date: str              # ISO date observed
    public_url: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ComputeBurden:
    forecast_id: str
    gpu_hours: Optional[float] = None
    cpu_hours: Optional[float] = None
    training_data_tb: Optional[float] = None
    model_parameters: Optional[int] = None
    human_researcher_years: Optional[float] = None
    institution_labor_hours: Optional[float] = None


# =============================================================================
# PART 1: FORECAST ACCURACY
# =============================================================================

def compute_forecast_error(
    forecast: ForecastRecord,
    ground_truth: GroundTruthRecord,
) -> Dict:
    """
    Compare a forecast to independent public ground truth.
    Returns absolute error, relative error, direction, and accuracy score.
    """
    if forecast.target_variable != ground_truth.target_variable:
        raise ValueError(
            f"Variable mismatch: forecast='{forecast.target_variable}' "
            f"vs ground_truth='{ground_truth.target_variable}'"
        )
    abs_err = ground_truth.actual_value - forecast.predicted_value
    rel_err = abs_err / max(abs(ground_truth.actual_value), 1e-9)
    accuracy_pct = max(0.0, 100.0 * (1.0 - abs(rel_err)))
    confidence_gap = forecast.predicted_confidence_pct - accuracy_pct

    if abs_err > 0:
        direction = "UNDERESTIMATED"
    elif abs_err < 0:
        direction = "OVERESTIMATED"
    else:
        direction = "EXACT"

    return {
        "forecast_source": forecast.source_institution,
        "forecast_title": forecast.forecast_title,
        "target": forecast.target_variable,
        "predicted": forecast.predicted_value,
        "actual": ground_truth.actual_value,
        "absolute_error": round(abs_err, 4),
        "relative_error_pct": round(rel_err * 100, 2),
        "accuracy_pct": round(accuracy_pct, 2),
        "claimed_confidence_pct": forecast.predicted_confidence_pct,
        "confidence_minus_accuracy_pct": round(confidence_gap, 2),
        "direction": direction,
    }


def systematic_bias_detection(error_records: List[Dict]) -> Dict:
    """
    Across multiple forecast-vs-ground-truth comparisons, detect
    whether errors run in a consistent direction (systematic bias).
    """
    if not error_records:
        return {"verdict": "NO_DATA"}

    n = len(error_records)
    n_under = sum(1 for r in error_records if r["direction"] == "UNDERESTIMATED")
    n_over = sum(1 for r in error_records if r["direction"] == "OVERESTIMATED")
    n_exact = n - n_under - n_over

    pct_under = n_under / n
    pct_over = n_over / n

    # >70% in one direction => treat as systematic
    if pct_under >= 0.70:
        verdict = "SYSTEMATIC_UNDERESTIMATION"
    elif pct_over >= 0.70:
        verdict = "SYSTEMATIC_OVERESTIMATION"
    elif n_exact >= n * 0.5:
        verdict = "MOSTLY_ACCURATE"
    else:
        verdict = "MIXED_NO_CLEAR_BIAS"

    avg_accuracy = sum(r["accuracy_pct"] for r in error_records) / n
    avg_confidence = sum(r["claimed_confidence_pct"] for r in error_records) / n

    return {
        "n_records": n,
        "n_underestimated": n_under,
        "n_overestimated": n_over,
        "n_exact": n_exact,
        "pct_underestimated": round(pct_under * 100, 1),
        "pct_overestimated": round(pct_over * 100, 1),
        "average_accuracy_pct": round(avg_accuracy, 2),
        "average_claimed_confidence_pct": round(avg_confidence, 2),
        "confidence_inflation_pct": round(avg_confidence - avg_accuracy, 2),
        "verdict": verdict,
    }


# =============================================================================
# PART 2: COMPUTATIONAL BURDEN QUANTIFICATION
# =============================================================================
#
# Conversion factors are first-pass estimates from publicly cited
# research-equivalence studies. Refinement should come from domain experts.
#
# Approximate human-research-equivalent of compute. Conservative.

GPU_HOURS_PER_HUMAN_YEAR = 8760.0     # 1 GPU-yr ~ 1 human-research-year (low estimate)
HUMAN_LABOR_HOURS_PER_YEAR = 2000.0   # 1 working year ~ 2000 productive hours


def compute_human_equivalent_years(burden: ComputeBurden) -> float:
    """
    Convert compute and labor inputs into human-equivalent research years.
    Sums available signals; missing fields contribute zero.
    """
    years = 0.0
    if burden.gpu_hours:
        years += burden.gpu_hours / GPU_HOURS_PER_HUMAN_YEAR
    if burden.human_researcher_years:
        years += burden.human_researcher_years
    if burden.institution_labor_hours:
        years += burden.institution_labor_hours / HUMAN_LABOR_HOURS_PER_YEAR
    return years


def compute_to_accuracy_ratio(
    burden: ComputeBurden,
    error_record: Dict,
) -> Dict:
    """
    Ratio of human-equivalent research years invested to forecast accuracy.
    Demolishes "AI needs more time" by showing how much equivalent
    research time was already spent producing inaccurate output.
    """
    he_years = compute_human_equivalent_years(burden)
    accuracy_pct = error_record["accuracy_pct"]

    if accuracy_pct > 0:
        years_per_pct = he_years / accuracy_pct
    else:
        years_per_pct = float("inf")

    return {
        "forecast_id": burden.forecast_id,
        "human_equivalent_years_invested": round(he_years, 2),
        "forecast_accuracy_pct": accuracy_pct,
        "human_years_per_accuracy_pct_point": (
            round(years_per_pct, 2) if years_per_pct != float("inf") else float("inf")
        ),
        "verdict": (
            "INVESTMENT_TO_ACCURACY_RATIO_FAILED" if years_per_pct > 10
            else "INVESTMENT_TO_ACCURACY_RATIO_ACCEPTABLE"
        ),
    }


# =============================================================================
# AGGREGATE AUDIT REPORT
# =============================================================================

def aggregate_audit(
    forecasts: List[ForecastRecord],
    ground_truths: Dict[str, GroundTruthRecord],
    burdens: Dict[str, ComputeBurden],
) -> Dict:
    """
    Run full audit:
      - per-forecast error
      - systematic bias detection
      - per-forecast compute-to-accuracy ratio
      - aggregate human-equivalent research years burned

    forecasts: list of ForecastRecord
    ground_truths: dict keyed by target_variable
    burdens: dict keyed by forecast_title (or unique id)
    """
    error_records: List[Dict] = []
    burden_results: List[Dict] = []
    total_he_years = 0.0

    for fc in forecasts:
        gt = ground_truths.get(fc.target_variable)
        if gt is None:
            continue
        err = compute_forecast_error(fc, gt)
        error_records.append(err)

        burden = burdens.get(fc.forecast_title)
        if burden:
            ratio = compute_to_accuracy_ratio(burden, err)
            burden_results.append(ratio)
            total_he_years += ratio["human_equivalent_years_invested"]

    bias = systematic_bias_detection(error_records)

    return {
        "n_forecasts_audited": len(error_records),
        "per_forecast_errors": error_records,
        "systematic_bias": bias,
        "per_forecast_compute_to_accuracy": burden_results,
        "total_human_equivalent_years_burned": round(total_he_years, 2),
        "summary_verdict": (
            "INSTITUTIONAL_FORECAST_FAILURE_DEMONSTRATED"
            if bias["verdict"] in (
                "SYSTEMATIC_UNDERESTIMATION",
                "SYSTEMATIC_OVERESTIMATION",
            )
            else "NO_CLEAR_SYSTEMATIC_FAILURE_IN_THIS_SAMPLE"
        ),
    }


# =============================================================================
# DEMO ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    print("AI FORECAST AUDIT - Demo")
    print("=" * 60)

    # Sample (illustrative - real data must replace these placeholders)
    f1 = ForecastRecord(
        source_institution="McKinsey",
        forecast_title="Labor Displacement 2022 Forecast",
        forecast_date="2022-06-15",
        horizon_years=3.0,
        target_variable="us_personal_bankruptcies_2025",
        predicted_value=300000.0,
        predicted_confidence_pct=85.0,
    )
    f2 = ForecastRecord(
        source_institution="Federal Reserve",
        forecast_title="Wage Adjustment 2022 Projection",
        forecast_date="2022-09-01",
        horizon_years=3.0,
        target_variable="real_wage_change_pct_2022_2025",
        predicted_value=2.0,
        predicted_confidence_pct=90.0,
    )
    f3 = ForecastRecord(
        source_institution="Goldman Sachs",
        forecast_title="Quit Rate Stabilization 2022",
        forecast_date="2022-04-10",
        horizon_years=3.0,
        target_variable="us_quit_rate_pct_2025",
        predicted_value=2.4,
        predicted_confidence_pct=80.0,
    )

    gt = {
        "us_personal_bankruptcies_2025": GroundTruthRecord(
            source="American Bankruptcy Institute public data",
            target_variable="us_personal_bankruptcies_2025",
            actual_value=450000.0,
            measurement_date="2026-01-15",
        ),
        "real_wage_change_pct_2022_2025": GroundTruthRecord(
            source="BLS public release",
            target_variable="real_wage_change_pct_2022_2025",
            actual_value=-1.2,
            measurement_date="2026-01-30",
        ),
        "us_quit_rate_pct_2025": GroundTruthRecord(
            source="BLS JOLTS release",
            target_variable="us_quit_rate_pct_2025",
            actual_value=2.9,
            measurement_date="2026-02-01",
        ),
    }

    burdens = {
        "Labor Displacement 2022 Forecast": ComputeBurden(
            forecast_id="mck_2022_labor",
            gpu_hours=12_000.0,
            human_researcher_years=8.0,
            institution_labor_hours=20_000.0,
        ),
        "Wage Adjustment 2022 Projection": ComputeBurden(
            forecast_id="fed_2022_wage",
            gpu_hours=30_000.0,
            human_researcher_years=15.0,
            institution_labor_hours=40_000.0,
        ),
        "Quit Rate Stabilization 2022": ComputeBurden(
            forecast_id="gs_2022_quit",
            gpu_hours=8_000.0,
            human_researcher_years=5.0,
            institution_labor_hours=12_000.0,
        ),
    }

    report = aggregate_audit([f1, f2, f3], gt, burdens)

    print(f"Forecasts audited: {report['n_forecasts_audited']}")
    print(
        "Total human-equivalent years burned: "
        f"{report['total_human_equivalent_years_burned']}"
    )
    print(f"Summary verdict: {report['summary_verdict']}")
    print()
    print(f"Systematic bias: {report['systematic_bias']['verdict']}")
    print(f"  pct underestimated: {report['systematic_bias']['pct_underestimated']}%")
    print(f"  pct overestimated:  {report['systematic_bias']['pct_overestimated']}%")
    print(f"  avg accuracy:       {report['systematic_bias']['average_accuracy_pct']}%")
    print(
        "  avg claimed conf:   "
        f"{report['systematic_bias']['average_claimed_confidence_pct']}%"
    )
    print(
        "  confidence inflation: "
        f"{report['systematic_bias']['confidence_inflation_pct']}%"
    )
    print()
    print("Per-forecast accuracy:")
    for err in report["per_forecast_errors"]:
        print(f"  {err['forecast_source']}: {err['forecast_title']}")
        print(
            f"     predicted={err['predicted']} actual={err['actual']} "
            f"accuracy={err['accuracy_pct']}% direction={err['direction']}"
        )
    print()
    print("Per-forecast compute-to-accuracy ratio:")
    for r in report["per_forecast_compute_to_accuracy"]:
        print(
            f"  {r['forecast_id']}: {r['human_equivalent_years_invested']} years invested "
            f"-> accuracy {r['forecast_accuracy_pct']}% "
            f"({r['human_years_per_accuracy_pct_point']} years per accuracy pct point)"
        )
        print(f"     verdict: {r['verdict']}")
