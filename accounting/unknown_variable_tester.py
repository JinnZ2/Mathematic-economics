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
4. Outputs an audit trail: raw coefficients, p-values, and partial correlations
   so you can see exactly how much "explanatory power" ΔT retains after other
   variables are accounted for.

All assumptions are stated as adjustable parameters.  Change them to match
real-world measurements or to stress-test alternative hypotheses.
"""

import argparse
import math
import random
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# stdlib-only replacements for numpy + scipy primitives.
try:
    from ._stdlib_stats import ols, correlation
except ImportError:
    from _stdlib_stats import ols, correlation


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
# SYNTHETIC DATA GENERATION  (stdlib lists)
# =============================================================================
def generate_facilities(n_facilities: int, claims: Claims,
                        confounders: List[Confounder],
                        delta_T_mean: float = 10.0, delta_T_std: float = 5.0,
                        seed: int = 42) -> Dict:
    """
    Create synthetic facilities with random ΔT and confounder values.
    Confounders may be correlated with ΔT as specified. Returns lists keyed
    by outcome / driver name so downstream code is dtype-agnostic.
    """
    rng = random.Random(seed)

    # ΔT truncated at zero (no negative gaps)
    delta_T = [max(0.0, rng.gauss(delta_T_mean, delta_T_std))
               for _ in range(n_facilities)]

    # Confounders, possibly correlated with ΔT via linear combination of
    # normalized ΔT and normalized independent baseline.
    confounder_data: Dict[str, List[float]] = {}
    for conf in confounders:
        base = [rng.uniform(conf.range_min, conf.range_max) for _ in range(n_facilities)]
        if conf.correlation_with_delta_T != 0.0 and delta_T_std > 0.0:
            b_center = (conf.range_min + conf.range_max) / 2.0
            b_scale = (conf.range_max - conf.range_min) / 2.0
            if b_scale <= 0.0:
                confounder_data[conf.name] = base
                continue
            a = conf.correlation_with_delta_T
            bcoef = math.sqrt(1.0 - a * a) if abs(a) < 1.0 else 0.0
            combined = []
            for k in range(n_facilities):
                dT_norm = (delta_T[k] - delta_T_mean) / delta_T_std
                b_norm = (base[k] - b_center) / b_scale
                c_norm = a * dT_norm + bcoef * b_norm
                v = c_norm * b_scale + b_center
                combined.append(max(conf.range_min, min(conf.range_max, v)))
            confounder_data[conf.name] = combined
        else:
            confounder_data[conf.name] = base

    floor_temp = [claims.office_temp_F + dt for dt in delta_T]

    # Productivity from ΔT (piecewise; comfort band [60, 75])
    uncomfortable_deg = []
    for ft in floor_temp:
        if ft > 75:
            uncomfortable_deg.append(ft - 75)
        elif ft < 60:
            uncomfortable_deg.append(60 - ft)
        else:
            uncomfortable_deg.append(0.0)
    prod_loss_pct = [min(100.0, u * claims.productivity_loss_pct_per_degF)
                     for u in uncomfortable_deg]
    prod_from_delta = [claims.base_daily_productivity_value * (1.0 - p / 100.0)
                       for p in prod_loss_pct]

    # Confounder contributions to productivity
    prod_conf_effect = [0.0] * n_facilities
    for conf in confounders:
        eff = conf.effect_on_productivity_dollar_per_worker_day
        vals = confounder_data[conf.name]
        for k in range(n_facilities):
            prod_conf_effect[k] += eff * vals[k]
    true_productivity = [max(0.0, prod_from_delta[k] + prod_conf_effect[k])
                         for k in range(n_facilities)]

    # Injury rate from ΔT (heat stress above 85F only)
    base_inj = claims.base_annual_injury_rate
    injury_mult = [1.0 + (claims.injury_rate_rise_per_degF_above_85 * (ft - 85.0)
                          if ft > 85.0 else 0.0)
                   for ft in floor_temp]
    inj_from_delta = [base_inj * m for m in injury_mult]
    inj_conf_effect = [0.0] * n_facilities
    for conf in confounders:
        eff = conf.effect_on_injury_rate_fraction
        vals = confounder_data[conf.name]
        for k in range(n_facilities):
            inj_conf_effect[k] += eff * vals[k]
    true_injury_rate = [max(0.0, min(1.0, inj_from_delta[k] + inj_conf_effect[k]))
                        for k in range(n_facilities)]

    # Turnover rate from ΔT (only above 80F)
    base_turn = claims.base_annual_turnover_rate
    turn_from_delta = [base_turn + (claims.turnover_increase_pct_per_degF_above_80
                                    * (ft - 80.0) / 100.0
                                    if ft > 80.0 else 0.0)
                       for ft in floor_temp]
    turn_conf_effect = [0.0] * n_facilities
    for conf in confounders:
        eff = conf.effect_on_turnover_rate_fraction
        vals = confounder_data[conf.name]
        for k in range(n_facilities):
            turn_conf_effect[k] += eff * vals[k]
    true_turnover_rate = [max(0.0, min(1.0, turn_from_delta[k] + turn_conf_effect[k]))
                          for k in range(n_facilities)]

    return {
        "delta_T": delta_T,
        "floor_temp_F": floor_temp,
        "productivity": true_productivity,
        "injury_rate": true_injury_rate,
        "turnover_rate": true_turnover_rate,
        "confounders": confounder_data,
    }


# =============================================================================
# REGRESSION ANALYSIS  (delegates to _stdlib_stats.ols)
# =============================================================================
def run_regression(y: List[float], X: List[List[float]],
                   feature_names: List[str]) -> Dict:
    """
    Ordinary Least Squares via _stdlib_stats.ols.
    Returns coefficient table (with intercept prepended to feature_names)
    and partial-correlation contributions for the non-intercept features.
    """
    r = ols(X, y)
    return {
        "coefficients": r["coefficients"],
        "std_errors": r["std_errors"],
        "t_stats": r["t_stats"],
        "p_values": r["p_values"],
        "r_squared": r["r_squared"],
        "partial_correlations": r["partial_correlations"],
        "feature_names": ["intercept"] + list(feature_names),
    }


def _build_X(data: Dict, confounders: List[Confounder]) -> List[List[float]]:
    """Assemble the design matrix as list-of-rows [delta_T, conf1, conf2, ...]"""
    n = len(data["delta_T"])
    return [[data["delta_T"][k]] + [data["confounders"][c.name][k] for c in confounders]
            for k in range(n)]


def analyze_and_report(data: Dict, confounders: List[Confounder], claims: Claims) -> None:
    """Run regressions for each outcome and print audit."""
    X = _build_X(data, confounders)
    feature_names = ["delta_T"] + [c.name for c in confounders]

    outcomes = [
        ("productivity $/worker/day",       data["productivity"]),
        ("injury rate (annual fraction)",   data["injury_rate"]),
        ("turnover rate (annual fraction)", data["turnover_rate"]),
    ]

    print("\n" + "=" * 80)
    print("MULTIVARIABLE REGRESSION AUDIT — Does ΔT survive confounders?")
    print("=" * 80)
    for outcome_name, y in outcomes:
        print(f"\n--- Outcome: {outcome_name} ---")
        res = run_regression(y, X, feature_names)
        print(f"Overall R² = {res['r_squared']:.4f}")
        print(f"{'Feature':<25} {'Coef':>10} {'StdErr':>10} {'t':>8} {'p-value':>10} {'Partial r':>10}")
        print("-" * 80)
        for i, name in enumerate(res["feature_names"]):
            coef = res["coefficients"][i]
            se = res["std_errors"][i]
            t = res["t_stats"][i]
            p = res["p_values"][i]
            partial = f"{res['partial_correlations'][i-1]:.4f}" if i > 0 else ""
            print(f"{name:<25} {coef:10.4f} {se:10.4f} {t:8.2f} {p:10.4f} {partial:>10}")

        delta_p = res["p_values"][1]  # index 1 = delta_T (after intercept)
        if delta_p < 0.05:
            print(f"✅ ΔT effect remains statistically significant (p={delta_p:.4f}) after controlling for confounders.")
        else:
            print(f"❌ ΔT effect is NOT significant (p={delta_p:.4f}) — confounders may explain the variation.")

        # Compare against simple ΔT-only model
        X_single = [[row[0]] for row in X]
        simple_res = run_regression(y, X_single, ["delta_T"])
        print(f"Simple ΔT-only R² = {simple_res['r_squared']:.4f}; ΔT coefficient = {simple_res['coefficients'][1]:.4f}")
        print(f"After controlling, ΔT coefficient = {res['coefficients'][1]:.4f}")

    # Partial variance ΔT uniquely explains: R² of full model minus R² without ΔT
    print("\n" + "=" * 80)
    print("PARTIAL VARIANCE EXPLAINED BY ΔT AFTER REMOVING CONFOUNDERS")
    print("=" * 80)
    X_no_delta = [row[1:] for row in X]
    for outcome_name, y in outcomes:
        full = run_regression(y, X, feature_names)
        no_delta = run_regression(y, X_no_delta, feature_names[1:])
        delta_unique = full["r_squared"] - no_delta["r_squared"]
        print(f"{outcome_name:<35}: Full R² {full['r_squared']:.4f} | "
              f"Without ΔT {no_delta['r_squared']:.4f} | "
              f"ΔT unique contribution {delta_unique:.4f}")


# =============================================================================
# MAIN
# =============================================================================
def main() -> None:
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
