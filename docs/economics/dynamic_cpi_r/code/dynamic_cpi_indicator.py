"""Dynamic CPI-R estimator for the bottom 60% income cohort.

This module converts the transferred prototype into working code that can be
run as a script, imported as a library, and tested without additional project
infrastructure. The implementation keeps the original design intent:

- dynamic expenditure weights estimated with a diagonal Kalman filter
- shock-sensitive measurement updates
- constraint-pressure adjustment based on co-movement of prices and spending
- lagged Consumer Expenditure (CE) correction
- drift detection, error tracking, and revision logging
- optional API payload generation for downstream services

The code uses only `numpy` from the scientific stack so that it fits the
repository's lightweight simulation style.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


CATEGORY_NAMES = ["food", "energy", "rent", "core_goods", "core_services"]
RENT_INDEX = 2


@dataclass
class DynamicCPIRConfig:
    """Configuration for the dynamic CPI-R estimator."""

    n_categories: int = 5
    sigma_w: float = 0.005
    r_base: float = 0.01
    lambda_c: float = 0.25
    phi: float = 0.5
    tau_shock: float = 0.03
    delta_max: float = 0.2
    gamma_rent: float = 0.9
    shock_gain_factor: float = 0.3
    drift_window: int = 12
    drift_threshold: float = 0.05
    correction_reset_factor: float = 0.5
    random_seed: int = 42


@dataclass
class BacktestResult:
    """Structured output from a CPI-R backtest run."""

    category_names: List[str]
    estimated_weights: np.ndarray
    true_weights: np.ndarray
    rms_per_category: np.ndarray
    overall_rms: float
    final_estimated_weights: np.ndarray
    final_true_weights: np.ndarray
    drift_flag: bool
    revision_count: int
    validation_correlation: Dict[str, float] = field(default_factory=dict)

    def to_serializable_dict(self) -> Dict[str, object]:
        """Convert numpy-heavy output into JSON-friendly primitives."""

        return {
            "category_names": self.category_names,
            "rms_per_category": {
                name: float(value)
                for name, value in zip(self.category_names, self.rms_per_category)
            },
            "overall_rms": float(self.overall_rms),
            "final_estimated_weights": {
                name: float(value)
                for name, value in zip(self.category_names, self.final_estimated_weights)
            },
            "final_true_weights": {
                name: float(value)
                for name, value in zip(self.category_names, self.final_true_weights)
            },
            "drift_flag": bool(self.drift_flag),
            "revision_count": int(self.revision_count),
            "validation_correlation": {
                key: float(value) for key, value in self.validation_correlation.items()
            },
        }


def renormalize(weights: Sequence[float]) -> np.ndarray:
    """Project a vector to the positive simplex."""

    w = np.asarray(weights, dtype=float)
    w = np.clip(w, 1e-9, None)
    total = float(np.sum(w))
    if total <= 0:
        return np.ones_like(w) / len(w)
    return w / total


def compute_cumulative_inflation(price_indices: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Compute cumulative CPI-style inflation from price levels and weights."""

    price_indices = np.asarray(price_indices, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if price_indices.shape != weights.shape:
        raise ValueError("price_indices and weights must have the same shape")

    base_prices = price_indices[0]
    weighted_index = np.sum(weights * (price_indices / base_prices), axis=1)
    return (weighted_index - 1.0) * 100.0


def annualized_latest_inflation(cumulative_series: Sequence[float], periods_per_year: int = 12) -> float:
    """Approximate annualized inflation from the latest monthly change."""

    series = np.asarray(cumulative_series, dtype=float)
    if len(series) < 2:
        return 0.0

    prev_level = 1.0 + series[-2] / 100.0
    curr_level = 1.0 + series[-1] / 100.0
    if prev_level <= 0:
        return 0.0
    monthly_growth = curr_level / prev_level
    return float((monthly_growth**periods_per_year - 1.0) * 100.0)


def generate_true_weights(n_months: int = 60, n_categories: int = 5, random_seed: int = 42) -> np.ndarray:
    """Generate synthetic bottom-60% expenditure weights."""

    if n_categories != 5:
        raise ValueError("This synthetic generator currently supports exactly 5 categories.")

    rng = np.random.default_rng(random_seed)
    t = np.arange(n_months)

    rent = 0.32 + 0.0004 * t + 0.02 * np.exp(-((t - 30) / 10) ** 2)
    energy = 0.072 + 0.0001 * t + 0.025 * np.exp(-((t - 28) / 6) ** 2)
    food = 0.145 - 0.0001 * t + 0.005 * np.sin(t / 12)
    core_goods = 0.213 - 0.0003 * t - 0.01 * (t > 24) * (1 - np.exp(-(t - 24) / 12))
    core_services = 1 - (rent + energy + food + core_goods)

    noise = rng.normal(0, 0.002, (n_months, n_categories))
    weights = np.column_stack([food, energy, rent, core_goods, core_services]) + noise
    return np.apply_along_axis(renormalize, 1, np.maximum(weights, 0.01))


def generate_price_indices(n_months: int = 60) -> np.ndarray:
    """Generate synthetic price indices for the five categories."""

    t = np.arange(n_months)
    food = 100 + 0.15 * t + 0.01 * t**1.1
    energy = 100 + 0.1 * t + 15 * np.exp(-((t - 28) / 8) ** 2)
    rent = 100 + 0.25 * t + 0.002 * t**1.2
    core_goods = 100 + 0.1 * t + 0.005 * t**1.1
    core_services = 100 + 0.2 * t + 0.001 * t**1.3
    return np.column_stack([food, energy, rent, core_goods, core_services])


def generate_credit_income_ratio(n_months: int = 60, random_seed: int = 43) -> np.ndarray:
    """Generate synthetic credit-to-income ratios with mid-period stress."""

    rng = np.random.default_rng(random_seed)
    t = np.arange(n_months)
    base = 0.18
    spike = 0.08 * np.exp(-((t - 30) / 10) ** 2)
    noise = rng.normal(0, 0.01, n_months)
    return np.clip(base + spike + noise, 0.1, 0.35)


def generate_external_rent_anchor(n_months: int = 60) -> np.ndarray:
    """Generate a smooth external rent anchor series."""

    t = np.arange(n_months)
    return 0.32 + 0.0003 * t + 0.01 * np.sin(t / 12)


class DynamicCPIR:
    """Dynamic CPI-R estimator with Kalman updates and audit hooks."""

    def __init__(self, config: Optional[DynamicCPIRConfig] = None) -> None:
        self.config = config or DynamicCPIRConfig()
        self.n = self.config.n_categories
        self.rng = np.random.default_rng(self.config.random_seed)

        self.w = np.ones(self.n) / self.n
        self.p = np.ones(self.n) * (self.config.sigma_w**2)
        self.history_w: List[np.ndarray] = []
        self.error_history: List[Tuple[int, np.ndarray]] = []
        self.bias = np.zeros(self.n)
        self.error_variance = np.zeros(self.n)
        self.error_autocorr = 0.0
        self.pred_error_memory: List[float] = []
        self.volatility_memory: List[float] = []
        self.validation_correlation: Dict[str, float] = {}
        self.revision_log: List[Dict[str, object]] = []
        self.weight_history_drift: List[np.ndarray] = []
        self.drift_flag = False
        self.cpi_r_history: List[float] = []

    def observation_model(
        self,
        true_weights: np.ndarray,
        credit_ratio: float,
        noise_std: Optional[float] = None,
    ) -> np.ndarray:
        """Simulate noisy observable expenditure shares."""

        std = self.config.r_base if noise_std is None else noise_std
        z = np.asarray(true_weights, dtype=float) + self.rng.normal(0, std, self.n)
        bias = np.array([0.005, 0.01, -0.02, 0.0, 0.0], dtype=float)
        z_income = z + bias
        z_adjusted = z_income * (1 - self.config.phi * float(credit_ratio))
        return np.maximum(z_adjusted, 1e-9)

    def shock_detected(self, w_prev: np.ndarray, z_curr: np.ndarray) -> bool:
        """Detect whether the measurement implies a meaningful regime shift."""

        return bool(np.sum(np.abs(z_curr - w_prev)) > self.config.tau_shock)

    def constraint_pressure(
        self,
        weights: np.ndarray,
        price_changes: np.ndarray,
        spend_changes: np.ndarray,
        sigma_p: np.ndarray,
        sigma_e: np.ndarray,
    ) -> np.ndarray:
        """Apply multiplicative reweighting based on standardized co-movement."""

        delta_p = np.asarray(price_changes) / (np.asarray(sigma_p) + 1e-6)
        delta_e = np.asarray(spend_changes) / (np.asarray(sigma_e) + 1e-6)
        pressure = np.clip(delta_e * delta_p, -3, 3)
        w_new = np.asarray(weights) * np.exp(self.config.lambda_c * pressure)
        return renormalize(w_new)

    def kalman_update(
        self,
        w_pred: np.ndarray,
        p_pred: np.ndarray,
        z: np.ndarray,
        r_eff: float,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Perform a diagonal Kalman update."""

        innovation = z - w_pred
        gain = p_pred / (p_pred + r_eff + 1e-8)
        w_new = w_pred + gain * innovation
        p_new = (1 - gain) * p_pred
        return w_new, p_new, gain

    def ce_correction(
        self,
        w_est: np.ndarray,
        w_ce: np.ndarray,
        sigma_drift: np.ndarray,
        sigma_ce_hist: np.ndarray,
    ) -> np.ndarray:
        """Blend the current estimate with lagged CE weights."""

        ratio = np.asarray(sigma_drift) / (np.asarray(sigma_ce_hist) + 1e-8)
        delta = np.minimum(self.config.delta_max, ratio)
        corrected = (1 - delta) * np.asarray(w_est) + delta * np.asarray(w_ce)
        return renormalize(corrected)

    def update_error_tracking(self, t: int, w_est: np.ndarray, w_ce_lagged: np.ndarray) -> None:
        """Update bias, variance, and autocorrelation of revision error."""

        error = np.asarray(w_est) - np.asarray(w_ce_lagged)
        self.error_history.append((t, error))

        alpha = 0.1
        self.bias = (1 - alpha) * self.bias + alpha * error

        recent_errors = np.array([entry[1] for entry in self.error_history[-12:]])
        if len(recent_errors) > 1:
            self.error_variance = np.var(recent_errors, axis=0)
        if len(recent_errors) >= 3:
            correlations: List[float] = []
            for idx in range(self.n):
                series = recent_errors[:, idx]
                if np.std(series) > 1e-9:
                    corr = np.corrcoef(series[:-1], series[1:])[0, 1]
                    if not np.isnan(corr):
                        correlations.append(float(corr))
            self.error_autocorr = float(np.mean(correlations)) if correlations else 0.0
        else:
            self.error_autocorr = 0.0

    def compute_adaptive_gain(self, prediction_error: float, current_volatility: float) -> float:
        """Adjust responsiveness based on recent forecast error and volatility."""

        self.pred_error_memory.append(float(prediction_error))
        self.volatility_memory.append(float(current_volatility))
        self.pred_error_memory = self.pred_error_memory[-12:]
        self.volatility_memory = self.volatility_memory[-12:]

        if len(self.pred_error_memory) < 6:
            return 1.0

        mean_error = float(np.mean(self.pred_error_memory))
        mean_vol = float(np.mean(self.volatility_memory))

        if mean_error > 0.02 and mean_vol < 0.01:
            gain_mult = 1.5
        elif mean_vol > 0.03:
            gain_mult = 0.5
        else:
            gain_mult = 1.0

        if self.error_autocorr > 0.5:
            gain_mult = min(gain_mult * 1.2, 2.0)

        return float(np.clip(gain_mult, 0.3, 2.0))

    def external_validation(
        self,
        metric_name: str,
        real_world_stress_series: Sequence[float],
        model_series: Sequence[float],
        threshold: float = 0.3,
    ) -> Tuple[float, bool]:
        """Compare the model series with an external stress signal."""

        x = np.asarray(real_world_stress_series, dtype=float)
        y = np.asarray(model_series, dtype=float)
        n = min(len(x), len(y))
        if n < 3:
            return 0.0, False

        corr = float(np.corrcoef(x[:n], y[:n])[0, 1])
        if np.isnan(corr):
            corr = 0.0
        self.validation_correlation[metric_name] = corr
        return corr, bool(corr > threshold)

    def detect_drift(self, w_current: np.ndarray) -> bool:
        """Track persistent change over the configured window."""

        self.weight_history_drift.append(np.asarray(w_current).copy())
        self.weight_history_drift = self.weight_history_drift[-self.config.drift_window :]

        if len(self.weight_history_drift) == self.config.drift_window:
            w_old = self.weight_history_drift[0]
            w_new = self.weight_history_drift[-1]
            total_drift = float(np.sum(np.abs(w_new - w_old)))
            self.drift_flag = total_drift > self.config.drift_threshold
        return self.drift_flag

    def log_revision(self, t: int, pre_weights: np.ndarray, post_weights: np.ndarray, ce_weights: np.ndarray) -> None:
        """Record a CE-driven revision event."""

        delta = float(np.linalg.norm(np.asarray(post_weights) - np.asarray(pre_weights)))
        self.revision_log.append(
            {
                "time": t,
                "pre": np.asarray(pre_weights).copy(),
                "post": np.asarray(post_weights).copy(),
                "ce": np.asarray(ce_weights).copy(),
                "delta": delta,
            }
        )

    def compute_cpi_r_history(self) -> np.ndarray:
        """Return the stored CPI-R history as a numpy array."""

        return np.asarray(self.cpi_r_history, dtype=float)

    def step(
        self,
        t: int,
        true_weights_t: np.ndarray,
        price_indices: np.ndarray,
        spend_shares_truth: np.ndarray,
        sigma_p: np.ndarray,
        sigma_e: np.ndarray,
        external_rent_anchor_t: float,
        credit_ratio_t: float,
        ce_weights: Optional[np.ndarray] = None,
        ce_release: bool = False,
        external_stress_series: Optional[Sequence[float]] = None,
    ) -> np.ndarray:
        """Perform one estimator update step."""

        w_pred = self.w.copy()
        p_pred = self.p + self.config.sigma_w**2

        z = self.observation_model(true_weights_t, credit_ratio_t)
        innovation = z - w_pred
        pred_error_norm = float(np.linalg.norm(innovation))

        if t > 0:
            window_start = max(0, t - 3)
            recent_price_changes = np.diff(price_indices[window_start : t + 1], axis=0)
            current_volatility = float(np.std(recent_price_changes)) if len(recent_price_changes) else 0.01
        else:
            current_volatility = 0.01

        gain_mult = self.compute_adaptive_gain(pred_error_norm, current_volatility)
        if self.shock_detected(self.w, z):
            r_eff = self.config.r_base * self.config.shock_gain_factor / gain_mult
        else:
            r_eff = self.config.r_base / gain_mult

        w_updated, p_updated, _ = self.kalman_update(w_pred, p_pred, z, r_eff)

        if t > 0:
            delta_p = price_indices[t] - price_indices[t - 1]
            delta_e = spend_shares_truth[t] - spend_shares_truth[t - 1]
        else:
            delta_p = np.zeros(self.n)
            delta_e = np.zeros(self.n)

        w_constrained = self.constraint_pressure(w_updated, delta_p, delta_e, sigma_p, sigma_e)
        w_constrained[RENT_INDEX] = (
            self.config.gamma_rent * float(external_rent_anchor_t)
            + (1 - self.config.gamma_rent) * w_constrained[RENT_INDEX]
        )
        w_final = renormalize(w_constrained)

        self.detect_drift(w_final)

        pre_correction = w_final.copy()
        self.w = w_final
        self.p = p_updated
        self.history_w.append(self.w.copy())

        if ce_release and ce_weights is not None:
            self.update_error_tracking(t, self.w, ce_weights)
            if len(self.history_w) >= 12:
                recent_weights = np.array(self.history_w[-12:])
                sigma_drift = np.std(recent_weights, axis=0)
            else:
                sigma_drift = np.zeros(self.n)
            sigma_ce_hist = 0.01 * np.ones(self.n)
            self.w = self.ce_correction(self.w, ce_weights, sigma_drift, sigma_ce_hist)
            self.p = self.p * self.config.correction_reset_factor
            self.log_revision(t, pre_correction, self.w, ce_weights)
            self.history_w[-1] = self.w.copy()

        current_cpi = float(np.sum(self.w * (price_indices[t] / price_indices[0]) - self.w) * 100.0)
        self.cpi_r_history.append(current_cpi)

        if external_stress_series is not None and t > 0 and (t + 1) % 12 == 0:
            model_series = self.compute_cpi_r_history()
            self.external_validation("cpi_r", external_stress_series[: len(model_series)], model_series)

        return self.w.copy()


def run_backtest(config: Optional[DynamicCPIRConfig] = None, n_months: int = 60) -> BacktestResult:
    """Run a full synthetic backtest and return structured metrics."""

    cfg = config or DynamicCPIRConfig()
    true_weights = generate_true_weights(n_months=n_months, random_seed=cfg.random_seed)
    price_indices = generate_price_indices(n_months=n_months)
    spend_shares = true_weights.copy()
    external_rent_anchor = generate_external_rent_anchor(n_months=n_months)
    credit_ratio = generate_credit_income_ratio(n_months=n_months, random_seed=cfg.random_seed + 1)

    sigma_p = np.std(np.diff(price_indices, axis=0), axis=0)
    sigma_e = np.std(np.diff(spend_shares, axis=0), axis=0)

    estimator = DynamicCPIR(cfg)
    estimated_weights: List[np.ndarray] = []

    ce_release_months = [month for month in [12, 24, 36, 48] if month < n_months]
    ce_weights_dict = {month: true_weights[month - 12] for month in ce_release_months}

    realized_cpi = compute_cumulative_inflation(price_indices, true_weights)
    external_stress = (realized_cpi - np.mean(realized_cpi)) / (np.std(realized_cpi) + 1e-8)

    for t in range(n_months):
        ce_weights = ce_weights_dict.get(t)
        estimate = estimator.step(
            t=t,
            true_weights_t=true_weights[t],
            price_indices=price_indices,
            spend_shares_truth=spend_shares,
            sigma_p=sigma_p,
            sigma_e=sigma_e,
            external_rent_anchor_t=external_rent_anchor[t],
            credit_ratio_t=credit_ratio[t],
            ce_weights=ce_weights,
            ce_release=ce_weights is not None,
            external_stress_series=external_stress,
        )
        estimated_weights.append(estimate)

    estimated_weights_array = np.asarray(estimated_weights)
    errors = estimated_weights_array - true_weights
    rms_per_category = np.sqrt(np.mean(errors**2, axis=0))
    overall_rms = float(np.sqrt(np.mean(errors**2)))

    return BacktestResult(
        category_names=list(CATEGORY_NAMES),
        estimated_weights=estimated_weights_array,
        true_weights=true_weights,
        rms_per_category=rms_per_category,
        overall_rms=overall_rms,
        final_estimated_weights=estimated_weights_array[-1],
        final_true_weights=true_weights[-1],
        drift_flag=estimator.drift_flag,
        revision_count=len(estimator.revision_log),
        validation_correlation=dict(estimator.validation_correlation),
    )


def create_api_payload(result: BacktestResult, timestamp: str = "2026-04-09") -> Dict[str, object]:
    """Create a JSON-serializable payload from the latest backtest result."""

    price_indices = generate_price_indices(len(result.estimated_weights))
    estimated_cpi_series = compute_cumulative_inflation(price_indices, result.estimated_weights)
    latest_cumulative = float(estimated_cpi_series[-1])
    latest_annualized = annualized_latest_inflation(estimated_cpi_series)
    final_weights = {
        name: float(value)
        for name, value in zip(result.category_names, result.final_estimated_weights)
    }
    constraint_scores = {
        "energy": float(final_weights["energy"] / max(final_weights["core_services"], 1e-6)),
        "rent": float(final_weights["rent"] / max(final_weights["food"], 1e-6)),
        "food": float(final_weights["food"] / max(final_weights["core_goods"], 1e-6)),
    }
    return {
        "timestamp": timestamp,
        "cpi_r_cumulative_since_dec2019": round(latest_cumulative, 2),
        "cpi_r_monthly_annualized": round(latest_annualized, 2),
        "weights": {key: round(value, 3) for key, value in final_weights.items()},
        "constraint_scores": {key: round(value, 3) for key, value in constraint_scores.items()},
    }


def save_api_payload(path: Path, payload: Dict[str, object]) -> None:
    """Write an API payload to disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def format_backtest_summary(result: BacktestResult) -> str:
    """Render a readable terminal summary."""

    lines = ["===== Dynamic CPI-R Backtest Results =====", ""]
    lines.append("| Category | RMS Error | Final Estimated | Final True |")
    lines.append("|---|---:|---:|---:|")
    for idx, name in enumerate(result.category_names):
        lines.append(
            f"| {name} | {result.rms_per_category[idx]:.4f} | "
            f"{result.final_estimated_weights[idx]:.4f} | {result.final_true_weights[idx]:.4f} |"
        )
    lines.append("")
    lines.append(f"Overall RMS error: {result.overall_rms:.4f}")
    lines.append(f"Drift detected: {result.drift_flag}")
    lines.append(f"Revision count: {result.revision_count}")
    if result.validation_correlation:
        for metric, corr in result.validation_correlation.items():
            lines.append(f"Validation correlation ({metric}): {corr:.4f}")
    return "\n".join(lines)


def create_flask_app(result: Optional[BacktestResult] = None):
    """Create an optional Flask app without requiring Flask for normal CLI use."""

    from flask import Flask, jsonify

    app = Flask(__name__)
    cached_result = result or run_backtest()
    payload = create_api_payload(cached_result)

    @app.route("/v1/cpi-r/current", methods=["GET"])
    def current_cpi_r():
        return jsonify(payload)

    @app.route("/v1/weights/current", methods=["GET"])
    def current_weights():
        return jsonify(payload["weights"])

    return app


def main() -> None:
    """Run the backtest and refresh the example payload file."""

    result = run_backtest()
    print(format_backtest_summary(result))

    payload = create_api_payload(result)
    output_path = Path(__file__).resolve().parents[1] / "examples" / "api.json"
    save_api_payload(output_path, payload)
    print(f"\nUpdated example payload: {output_path}")


if __name__ == "__main__":
    main()
