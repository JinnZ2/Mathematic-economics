#!/usr/bin/env python3
"""
UNKNOWN-VARIABLE TESTER FOR HVAC INEQUITY AUDITS
-------------------------------------------------
Problem:  Observed outcomes (waste, productivity, injuries, turnover) vary
between facilities.  Is the temperature gap (ΔT) really the cause, or could
differences in wages, shift patterns, family time, etc. produce the same
patterns?

This script:
1. Defines a set of falsifiable confounders (any number, any effect size).
2. Generates synthetic facilities with random values for ΔT and all confounders.
3. Runs multivariate linear regressions for each outcome, both with and without
   controlling for the confounders.
4. Outputs an audit trail: raw coefficients, p‑values, and partial R² so you
   can see exactly how much “explanatory power” ΔT retains after other
   variables are accounted for.

All assumptions are stated as adjustable parameters.  Change them to match
real-world measurements or to stress‑test alternative hypotheses.
"""

import numpy as np
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import argparse

# =============================================================================
# CONFIGURABLE CONFOUNDERS
# Add any number of alternative explanations here.
# =============================================================================
@dataclass
class Confounder:
    name: str
    # Effect on each outcome per *unit* of the confounder.
    # Positive = increases the outcome; negative = decreases.
    effect_on_productivity_dollar_per_worker_day: float = 0.0   # e.g., +$10/day per $1/hr wage increase
    effect_on_injury_rate_fraction: float = 0.0                 # e.g., -0.002 per additional break minute
    effect_on_turnover_rate_fraction: float = 0.0               # e.g., -0.01 per extra vacation day
    # Realistic range for random generation [min, max]
    range_min: float = 0.0
    range_max: float = 1.0
    # Correlation with ΔT (to simulate omitted variable bias)
    correlation_with_delta_T: float = 0.0

# Pre‑defined example confounders – edit or add freely.
DEFAULT_CONFOUNDERS = [
    Confounder("hourly_wage_premium_$", 
               effect_on_productivity_dollar_per_worker_day=15.0,
               effect_on_injury_rate_fraction=-0.005,
               effect_on_turnover_rate_fraction=-0.02,
               range_min=-2.0, range_max=5.0, correlation_with_delta_T=-0.4),
    Confounder("daily_shift_hours",
               effect_on_productivity_dollar_per_worker_day=-30.0,
               effect_on_injury_rate_fraction=0.01,
               effect_on_turnover_rate_fraction=0.01,
               range_min=6.0, range_max=12.0, correlation_with_delta_T=0.3),
    Confounder("annual_pto_days",
               effect_on_productivity_dollar_per_worker_day=0.0,
               effect_on_injury_rate_fraction=-0.001,
               effect_on_turnover_rate_fraction=-0.005,
               range_min=5.0, range_max=25.0, correlation_with_delta_T=-0.2),
]

# Baseline claims for the ΔT effect (same as previous gradient model)
@dataclass
class Claims:
    extra_kwh_per_degF_per_day: float = 2.0
    productivity_loss_pct_per_degF: float = 1.5
    injury_rate_rise_per_degF_above_85: float = 0.02
    turnover_increase_pct_per_degF_above_80: float = 0.5
    office_temp_F: float = 72.0
    electricity_cost_per_kwh: float = 0.12
    annual_work_days: int = 250
    base_daily_productivity_value: float = 500.0
    base_annual_injury_rate: float = 0.03
    base_annual_turnover_rate: float = 0.15
    cost_per_turnover: float = 5000.0
    num_floor_workers: int = 20

# =============================================================================
# SYNTHETIC DATA GENERATION
# =============================================================================
def generate_facilities(n_facilities: int, claims: Claims,
                        confounders: List[Confounder],
                        delta_T_mean: float = 10.0, delta_T_std: float = 5.0,
                        seed: int = 42) -> Dict[str, np.ndarray]:
    """
    Create synthetic facilities with random ΔT and confounder values.
    Confounders may be correlated with ΔT as specified.
    """
    rng = np.random.default_rng(seed)
    # Generate ΔT
    delta_T = rng.normal(delta_T_mean, delta_T_std, n_facilities)
    delta_T = np.clip(delta_T, 0, None)  # no negative gaps

    # Generate confounders, possibly correlated with ΔT
    confounder_data = {}
    for conf in confounders:
        base = rng.uniform(conf.range_min, conf.range_max, n_facilities)
        if conf.correlation_with_delta_T != 0:
            # Mix base with ΔT to create correlation
            # Use a simple linear combination: desired corr = a / sqrt(a² + b²)
            # We'll set a = corr * base_std, b = sqrt(1 - corr²)*base_std
            # Actually, we can just add fraction of ΔT to base: conf = base + corr_factor * (delta_T - mean)
            delta_T_norm = (delta_T - delta_T_mean) / delta_T_std
            base_norm = (base - (conf.range_min + conf.range_max)/2) / ((conf.range_max - conf.range_min)/2)
            # Create linear combination to achieve desired correlation
            a = conf.correlation_with_delta_T
            b = np.sqrt(1 - a**2) if abs(a) < 1 else 0
            combined_norm = a * delta_T_norm + b * base_norm
            # Rescale back to original range
            orig_center = (conf.range_min + conf.range_max) / 2
            orig_scale = (conf.range_max - conf.range_min) / 2
            combined = combined_norm * orig_scale + orig_center
            combined = np.clip(combined, conf.range_min, conf.range_max)
            confounder_data[conf.name] = combined
        else:
            confounder_data[conf.name] = base

    # Compute true outcomes based on ΔT and confounders
    # Productivity loss due to ΔT
    floor_temp = claims.office_temp_F + delta_T
    uncomfortable_deg = np.where(floor_temp > 75, floor_temp - 75,
                                 np.where(floor_temp < 60, 60 - floor_temp, 0))
    prod_loss_pct = uncomfortable_deg * claims.productivity_loss_pct_per_degF
    prod_loss_pct = np.clip(prod_loss_pct, 0, 100)
    prod_from_delta = claims.base_daily_productivity_value * (1 - prod_loss_pct/100)

    # Add confounder effects to productivity (per worker per day)
    prod_confounder_effect = np.zeros(n_facilities)
    for conf in confounders:
        prod_confounder_effect += conf.effect_on_productivity_dollar_per_worker_day * confounder_data[conf.name]
    true_productivity = prod_from_delta + prod_confounder_effect
    true_productivity = np.clip(true_productivity, 0, None)

    # Injury rate due to ΔT (fraction per year)
    base_inj = claims.base_annual_injury_rate
    injury_mult = np.ones(n_facilities)
    high_mask = floor_temp > 85
    injury_mult[high_mask] += claims.injury_rate_rise_per_degF_above_85 * (floor_temp[high_mask] - 85)
    inj_from_delta = base_inj * injury_mult

    # Confounder effects on injury rate (additive)
    inj_conf_effect = np.zeros(n_facilities)
    for conf in confounders:
        inj_conf_effect += conf.effect_on_injury_rate_fraction * confounder_data[conf.name]
    true_injury_rate = inj_from_delta + inj_conf_effect
    true_injury_rate = np.clip(true_injury_rate, 0, 1)

    # Turnover rate
    base_turn = claims.base_annual_turnover_rate
    turn_rate = np.full(n_facilities, base_turn)
    high_mask80 = floor_temp > 80
    turn_rate[high_mask80] += (claims.turnover_increase_pct_per_degF_above_80
                               * (floor_temp[high_mask80] - 80) / 100.0)
    turn_conf_effect = np.zeros(n_facilities)
    for conf in confounders:
        turn_conf_effect += conf.effect_on_turnover_rate_fraction * confounder_data[conf.name]
    true_turnover_rate = turn_rate + turn_conf_effect
    true_turnover_rate = np.clip(true_turnover_rate, 0, 1)

    return {
        "delta_T": delta_T,
        "floor_temp_F": floor_temp,
        "productivity": true_productivity,
        "injury_rate": true_injury_rate,
        "turnover_rate": true_turnover_rate,
        "confounders": confounder_data
    }

# =============================================================================
# REGRESSION ANALYSIS
# =============================================================================
def run_regression(y: np.ndarray, X: np.ndarray, feature_names: List[str]):
    """
    Ordinary Least Squares using numpy.linalg.lstsq.
    Returns coefficient table and partial R² contributions.
    """
    # Add intercept
    X_with_intercept = np.column_stack([np.ones(len(y)), X])
    coeffs, residuals, rank, s = np.linalg.lstsq(X_with_intercept, y, rcond=None)
    # coeffs[0] is intercept, rest are slopes
    # Compute predictions and standard errors
    y_pred = X_with_intercept @ coeffs
    n, p = X_with_intercept.shape
    dof = n - p
    if residuals.size > 0:
        mse = residuals[0] / dof
    else:
        mse = np.sum((y - y_pred)**2) / dof
    # Variance-covariance matrix
    XtX_inv = np.linalg.inv(X_with_intercept.T @ X_with_intercept)
    se = np.sqrt(np.diag(XtX_inv) * mse)
    t_stats = coeffs / se
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), dof))

    # Partial R² via sequential sum of squares? Simpler: compute contribution to variance explained
    # Compute correlation of each X with y after controlling for others:
    partial_corrs = []
    for i in range(1, len(coeffs)):
        # Partial correlation of X[:,i-1]
        x_i = X[:, i-1]
        # residualize y and x_i on all other X
        other_mask = [j for j in range(X.shape[1]) if j != (i-1)]
        X_others = X[:, other_mask]
        # Residualize y
        X_others_int = np.column_stack([np.ones(n), X_others])
        coeff_y_others, _, _, _ = np.linalg.lstsq(X_others_int, y, rcond=None)
        y_resid = y - X_others_int @ coeff_y_others
        # Residualize x_i
        coeff_x_others, _, _, _ = np.linalg.lstsq(X_others_int, x_i, rcond=None)
        x_resid = x_i - X_others_int @ coeff_x_others
        corr = np.corrcoef(y_resid, x_resid)[0,1] if np.std(y_resid)>0 and np.std(x_resid)>0 else 0
        partial_corrs.append(corr)

    # Total R²
    ss_total = np.sum((y - np.mean(y))**2)
    ss_residual = np.sum((y - y_pred)**2)
    r_squared = 1 - ss_residual / ss_total

    return {
        "coefficients": coeffs,
        "std_errors": se,
        "t_stats": t_stats,
        "p_values": p_values,
        "r_squared": r_squared,
        "partial_correlations": partial_corrs,
        "feature_names": ["intercept"] + feature_names
    }

def analyze_and_report(data: Dict, confounders: List[Confounder], claims: Claims):
    """Run regressions for each outcome and print audit."""
    X = np.column_stack([data["delta_T"]] + [data["confounders"][c.name] for c in confounders])
    feature_names = ["delta_T"] + [c.name for c in confounders]

    outcomes = {
        "productivity $/worker/day": data["productivity"],
        "injury rate (annual fraction)": data["injury_rate"],
        "turnover rate (annual fraction)": data["turnover_rate"]
    }

    print("\n" + "="*80)
    print("MULTIVARIABLE REGRESSION AUDIT — Does ΔT survive confounders?")
    print("="*80)
    for outcome_name, y in outcomes.items():
        print(f"\n--- Outcome: {outcome_name} ---")
        res = run_regression(y, X, feature_names)
        print(f"Overall R² = {res['r_squared']:.4f}")
        # Table
        print(f"{'Feature':<25} {'Coef':>10} {'StdErr':>10} {'t':>8} {'p-value':>10} {'Partial r':>10}")
        print("-"*80)
        for i, name in enumerate(res["feature_names"]):
            coef = res["coefficients"][i]
            se = res["std_errors"][i]
            t = res["t_stats"][i]
            p = res["p_values"][i]
            partial = res["partial_correlations"][i-1] if i>0 else ""
            print(f"{name:<25} {coef:10.4f} {se:10.4f} {t:8.2f} {p:10.4f} {str(partial):>10}")
        # Check if ΔT remains significant
        delta_p = res["p_values"][1]  # index 1 is delta_T after intercept
        if delta_p < 0.05:
            print(f"✅ ΔT effect remains statistically significant (p={delta_p:.4f}) after controlling for confounders.")
        else:
            print(f"❌ ΔT effect is NOT significant (p={delta_p:.4f}) — confounders may explain the variation.")
        # Additional note: compare to simple regression
        simple_res = run_regression(y, X[:,0].reshape(-1,1), ["delta_T"])
        print(f"Simple ΔT-only R² = {simple_res['r_squared']:.4f}; ΔT coefficient = {simple_res['coefficients'][1]:.4f}")
        print(f"After controlling, ΔT coefficient = {res['coefficients'][1]:.4f}")

    # Summary: how much variance ΔT uniquely explains
    print("\n" + "="*80)
    print("PARTIAL VARIANCE EXPLAINED BY ΔT AFTER REMOVING CONFOUNDERS")
    print("="*80)
    for outcome_name, y in outcomes.items():
        # Compute R² of full model vs model without ΔT
        X_no_delta = X[:, 1:]
        full_r2 = run_regression(y, X, feature_names)["r_squared"]
        no_delta_r2 = run_regression(y, X_no_delta, feature_names[1:])["r_squared"]
        delta_unique = full_r2 - no_delta_r2
        print(f"{outcome_name:<35}: Full R² {full_r2:.4f} | Without ΔT {no_delta_r2:.4f} | ΔT unique contribution {delta_unique:.4f}")

# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Unknown-variable tester for HVAC gradient audit.")
    parser.add_argument('--facilities', type=int, default=500, help='Number of simulated facilities')
    parser.add_argument('--delta_T_mean', type=float, default=10.0)
    parser.add_argument('--delta_T_std', type=float, default=5.0)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    claims = Claims()
    confounders = DEFAULT_CONFOUNDERS

    print("Using confounders:")
    for c in confounders:
        print(f"  {c.name}: range [{c.range_min}, {c.range_max}], corr with ΔT = {c.correlation_with_delta_T}")
        print(f"    effect on productivity: {c.effect_on_productivity_dollar_per_worker_day:+} per unit")
        print(f"    effect on injury rate:  {c.effect_on_injury_rate_fraction:+}")
        print(f"    effect on turnover:     {c.effect_on_turnover_rate_fraction:+}")

    data = generate_facilities(args.facilities, claims, confounders,
                               delta_T_mean=args.delta_T_mean,
                               delta_T_std=args.delta_T_std,
                               seed=args.seed)
    analyze_and_report(data, confounders, claims)

    print("\n👉 To test your own alternative explanations, edit the DEFAULT_CONFOUNDERS list.")
    print("   Change effect sizes or correlations to see how they alter the conclusions.")
    print("   If ΔT no longer matters, the original claim is falsified for that scenario.")

if __name__ == "__main__":
    main()
