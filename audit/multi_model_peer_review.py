# multi_model_peer_review.py
#
# MULTI_MODEL_PEER_REVIEW_2026
#
# AI-to-AI peer review framework. Independent models with different
# training data, architectures, or vendors run the same forecast
# question. Compare predictions for convergence/divergence. Test all
# against ground truth. Replaces (or complements) traditional human
# peer review with independent AI cross-validation.
#
# Companion to ai_forecast_audit and validation_timeline_audit.
#
# Outputs:
#   - per-model predictions
#   - convergence score (how closely models agree)
#   - per-model accuracy against ground truth
#   - divergence flags identifying which models drift and in which direction
#   - peer-review verdict: CONSENSUS / SPLIT / FRAGMENTED
#
# License: CC0 1.0 Universal

import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ModelPrediction:
    model_id: str                       # e.g., "model_A_vendor_X"
    training_corpus_label: str          # e.g., "open_web_2020", "financial_2022"
    architecture_class: str             # e.g., "transformer_LLM", "tabular_GBM"
    predicted_value: float
    stated_confidence_pct: float
    prediction_date: str                # ISO


@dataclass
class GroundTruthPoint:
    target_variable: str
    actual_value: float
    measurement_source: str
    measurement_date: str


# =============================================================================
# CONVERGENCE / DIVERGENCE
# =============================================================================

def convergence_metrics(predictions: List[ModelPrediction]) -> Dict:
    """
    Measure how closely independent models agree on a prediction.
    """
    if len(predictions) < 2:
        return {"verdict": "INSUFFICIENT_MODELS", "n_models": len(predictions)}

    values = [p.predicted_value for p in predictions]
    mean_v = statistics.mean(values)
    stdev_v = statistics.stdev(values) if len(values) > 1 else 0.0
    spread = max(values) - min(values)

    # Coefficient of variation as convergence proxy
    cv = stdev_v / max(abs(mean_v), 1e-9)

    if cv < 0.05:
        verdict = "STRONG_CONVERGENCE"
    elif cv < 0.15:
        verdict = "MODERATE_CONVERGENCE"
    elif cv < 0.30:
        verdict = "WEAK_CONVERGENCE"
    else:
        verdict = "DIVERGENT_NO_CONSENSUS"

    return {
        "n_models": len(predictions),
        "mean_prediction": round(mean_v, 4),
        "stdev_prediction": round(stdev_v, 4),
        "spread": round(spread, 4),
        "coefficient_of_variation": round(cv, 4),
        "verdict": verdict,
    }


# =============================================================================
# ACCURACY VS GROUND TRUTH
# =============================================================================

def accuracy_vs_ground_truth(
    predictions: List[ModelPrediction],
    ground_truth: GroundTruthPoint,
) -> List[Dict]:
    """
    For each model, compute accuracy against the same ground truth point.
    Returns ranked list, most accurate first.
    """
    out = []
    for p in predictions:
        abs_err = ground_truth.actual_value - p.predicted_value
        rel_err = abs_err / max(abs(ground_truth.actual_value), 1e-9)
        accuracy_pct = max(0.0, 100.0 * (1.0 - abs(rel_err)))
        out.append({
            "model_id": p.model_id,
            "training_corpus_label": p.training_corpus_label,
            "architecture_class": p.architecture_class,
            "predicted": p.predicted_value,
            "actual": ground_truth.actual_value,
            "accuracy_pct": round(accuracy_pct, 2),
            "stated_confidence_pct": p.stated_confidence_pct,
            "confidence_minus_accuracy_pct":
                round(p.stated_confidence_pct - accuracy_pct, 2),
            "absolute_error": round(abs_err, 4),
        })
    out.sort(key=lambda x: -x["accuracy_pct"])
    return out


# =============================================================================
# DIVERGENCE FLAGS
# =============================================================================

def divergence_flags(predictions: List[ModelPrediction]) -> List[Dict]:
    """
    Identify which models drift far from the median, and in which direction.
    Useful for spotting model-specific bias.
    """
    if len(predictions) < 3:
        return []
    values = [p.predicted_value for p in predictions]
    median_v = statistics.median(values)
    iqr = statistics.quantiles(values, n=4)
    q1, q3 = iqr[0], iqr[2]
    iqr_range = q3 - q1
    flags = []
    for p in predictions:
        if p.predicted_value > q3 + 1.5 * iqr_range:
            flags.append({
                "model_id": p.model_id,
                "drift_direction": "HIGH_OUTLIER",
                "predicted_value": p.predicted_value,
                "median_value": median_v,
            })
        elif p.predicted_value < q1 - 1.5 * iqr_range:
            flags.append({
                "model_id": p.model_id,
                "drift_direction": "LOW_OUTLIER",
                "predicted_value": p.predicted_value,
                "median_value": median_v,
            })
    return flags


# =============================================================================
# AGGREGATE PEER REVIEW
# =============================================================================

def peer_review(
    predictions: List[ModelPrediction],
    ground_truth: Optional[GroundTruthPoint] = None,
) -> Dict:
    """
    Full multi-model peer review report.
    """
    convergence = convergence_metrics(predictions)
    drift = divergence_flags(predictions)
    accuracy = (
        accuracy_vs_ground_truth(predictions, ground_truth)
        if ground_truth else None
    )

    # Overall peer-review verdict
    if convergence["verdict"] == "STRONG_CONVERGENCE":
        if accuracy and accuracy[0]["accuracy_pct"] >= 70:
            review_verdict = "CONSENSUS_AND_VALIDATED"
        elif accuracy:
            review_verdict = "CONSENSUS_BUT_FALSIFIED_BY_GROUND_TRUTH"
        else:
            review_verdict = "CONSENSUS_AWAITING_GROUND_TRUTH"
    elif convergence["verdict"] in ("MODERATE_CONVERGENCE", "WEAK_CONVERGENCE"):
        review_verdict = "PARTIAL_CONSENSUS_REQUIRES_MORE_MODELS"
    else:
        review_verdict = "FRAGMENTED_NO_CONSENSUS"

    return {
        "n_models": len(predictions),
        "convergence": convergence,
        "drift_flags": drift,
        "per_model_accuracy": accuracy,
        "peer_review_verdict": review_verdict,
    }


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("MULTI-MODEL PEER REVIEW - Demo")
    print("=" * 60)

    # Three independent models predict the same target variable
    p1 = ModelPrediction(
        model_id="model_A_vendor_X",
        training_corpus_label="open_web_2020",
        architecture_class="transformer_LLM",
        predicted_value=300000.0,
        stated_confidence_pct=85.0,
        prediction_date="2022-06-01",
    )
    p2 = ModelPrediction(
        model_id="model_B_vendor_Y",
        training_corpus_label="financial_news_2021",
        architecture_class="tabular_GBM",
        predicted_value=320000.0,
        stated_confidence_pct=78.0,
        prediction_date="2022-06-15",
    )
    p3 = ModelPrediction(
        model_id="model_C_vendor_Z",
        training_corpus_label="bls_microdata_2020",
        architecture_class="ensemble_with_linear_baseline",
        predicted_value=380000.0,
        stated_confidence_pct=72.0,
        prediction_date="2022-07-10",
    )
    predictions = [p1, p2, p3]

    gt = GroundTruthPoint(
        target_variable="us_personal_bankruptcies_2025",
        actual_value=450000.0,
        measurement_source="American Bankruptcy Institute public release",
        measurement_date="2026-01-15",
    )

    report = peer_review(predictions, gt)

    print(f"Models reviewed: {report['n_models']}")
    print(f"Peer-review verdict: {report['peer_review_verdict']}")
    print()
    print("Convergence:")
    for k, v in report["convergence"].items():
        print(f"  {k}: {v}")
    print()
    print("Drift flags:")
    for f in report["drift_flags"]:
        print(f"  {f}")
    print()
    print("Per-model accuracy (sorted):")
    for a in report["per_model_accuracy"]:
        print(
            f"  {a['model_id']:25s} pred={a['predicted']:>8.0f} "
            f"actual={a['actual']:>8.0f} accuracy={a['accuracy_pct']}% "
            f"(claimed conf={a['stated_confidence_pct']}%, "
            f"inflation={a['confidence_minus_accuracy_pct']}%)"
        )
