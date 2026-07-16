#!/usr/bin/env python3
"""
FALSIFIABLE HVAC GRADIENT EXPERIMENT
=====================================
Given a temperature difference (ΔT) between the conditioned office and the
unconditioned shop floor, this script:

1. Models WASTE (extra HVAC energy due to thermal coupling).
2. Predicts PRODUCTIVITY loss, INJURY risk increase, and TURNOVER cost.
3. Frames each relationship as a disprovable CLAIM.
4. Designs a real-world experiment (A/B with noisy data) to test the claims.
5. Runs a simulated experiment and reports p-values.

All assumptions are parameterised and annotated so any AI auditor can trace
the logic, challenge the claims, and suggest better data.
"""

import argparse
import math
import random
import statistics
from dataclasses import dataclass
from typing import List, Dict

# stdlib-only replacements for numpy.random + scipy.stats primitives.
# Works both when this file is run as `python3 accounting/HVAC_gradient.py`
# (sys.path[0] == accounting/) and when imported as `accounting.HVAC_gradient`.
try:
    from ._stdlib_stats import poisson, welch_t_greater
except ImportError:
    from _stdlib_stats import poisson, welch_t_greater

# ----------------------------------------------------------------------
# 1. FALSIFIABLE CLAIMS (each can be disproven with data)
# ----------------------------------------------------------------------

@dataclass
class Claims:
    """
    These coefficients are hypotheses.  Change them to match your facility,
    then collect data and test.  If the observed effects are statistically
    indistinguishable from zero, the claim is falsified.
    """
    # ENERGY WASTE: each 1°F of ΔT adds this many kWh/day to office HVAC load
    # (heat transfer through walls/ceiling from hot shop floor)
    extra_kwh_per_degF_per_day: float = 2.0      # Claim 1

    # PRODUCTIVITY: output loss per °F above 75°F (or below 60°F) on floor
    # Source hypothesis: every 1°F beyond comfort band costs 1.5% of output.
    productivity_loss_pct_per_degF: float = 1.5   # Claim 2

    # INJURY RATE: multiplier increase per °F above 85°F (heat stress)
    # Claim: injury rate = base * (1 + 0.02 * max(0, floor_temp_F - 85))
    injury_rate_rise_per_degF_above_85: float = 0.02   # Claim 3

    # TURNOVER: annual voluntary turnover % increase per °F above 80°F
    # Claim: turnover_% = base_turnover% + 0.5 * max(0, floor_temp_F - 80)
    turnover_increase_pct_per_degF_above_80: float = 0.5   # Claim 4

    # Comfort band for office (setpoint)
    office_temp_F: float = 72.0

    # Baseline costs / rates
    electricity_cost_per_kwh: float = 0.12
    annual_work_days: int = 250
    base_daily_productivity_value: float = 500.0  # $ value of output per floor worker/day
    base_annual_injury_rate: float = 0.03         # 3% of workers per year
    base_annual_turnover_rate: float = 0.15       # 15%
    cost_per_turnover: float = 5000.0              # hiring + training cost
    num_floor_workers: int = 20

# ----------------------------------------------------------------------
# 2. GRADIENT MODEL
# ----------------------------------------------------------------------

def compute_impacts(delta_T_F: float, claims: Claims) -> Dict:
    """
    Given a steady-state temperature difference ΔT = T_floor - T_office,
    return estimated annual waste, productivity loss, extra injuries, and
    extra turnover cost.
    """
    # --- Waste: extra HVAC energy due to heat flow ---
    extra_kwh_per_day = claims.extra_kwh_per_degF_per_day * abs(delta_T_F)  # works for both heating & cooling
    annual_extra_kwh = extra_kwh_per_day * claims.annual_work_days
    annual_waste_cost = annual_extra_kwh * claims.electricity_cost_per_kwh

    # Floor temperature (assumed office always at 72°F)
    floor_temp = claims.office_temp_F + delta_T_F

    # --- Productivity loss (symmetrical hot/cold outside 60-75°F band) ---
    if floor_temp > 75:
        uncomfortable_deg = floor_temp - 75
    elif floor_temp < 60:
        uncomfortable_deg = 60 - floor_temp
    else:
        uncomfortable_deg = 0
    productivity_loss_pct = uncomfortable_deg * claims.productivity_loss_pct_per_degF
    # Cap at 100%
    productivity_loss_pct = min(productivity_loss_pct, 100.0)
    daily_loss_per_worker = claims.base_daily_productivity_value * (productivity_loss_pct / 100)
    annual_productivity_loss = (daily_loss_per_worker * claims.annual_work_days
                                * claims.num_floor_workers)

    # --- Injury rate increase (heat only) ---
    injury_multiplier = 1.0
    if floor_temp > 85:
        injury_multiplier += claims.injury_rate_rise_per_degF_above_85 * (floor_temp - 85)
    annual_injuries = claims.base_annual_injury_rate * claims.num_floor_workers * injury_multiplier
    extra_injuries = annual_injuries - (claims.base_annual_injury_rate * claims.num_floor_workers)

    # --- Turnover increase (heat only) ---
    turnover_rate = claims.base_annual_turnover_rate
    if floor_temp > 80:
        turnover_rate += (claims.turnover_increase_pct_per_degF_above_80
                          * (floor_temp - 80) / 100)  # convert to fraction
    annual_turnovers = turnover_rate * claims.num_floor_workers
    extra_turnovers = annual_turnovers - (claims.base_annual_turnover_rate * claims.num_floor_workers)
    extra_turnover_cost = extra_turnovers * claims.cost_per_turnover

    return {
        "delta_T_F": delta_T_F,
        "floor_temp_F": floor_temp,
        "annual_waste_cost": annual_waste_cost,
        "productivity_loss_pct": productivity_loss_pct,
        "annual_productivity_loss": annual_productivity_loss,
        "injury_rate_multiplier": injury_multiplier,
        "extra_annual_injuries": extra_injuries,
        "turnover_rate": turnover_rate,
        "extra_annual_turnovers": extra_turnovers,
        "extra_turnover_cost": extra_turnover_cost,
        "total_extra_annual_cost": (annual_waste_cost + annual_productivity_loss
                                    + extra_turnover_cost)
    }

# ----------------------------------------------------------------------
# 3. EXPERIMENT DESIGN (Falsifiable)
# ----------------------------------------------------------------------

def run_simulated_experiment(claims: Claims,
                             treatment_delta_T: float = 3.0,   # reduced gap
                             control_delta_T: float = 15.0,    # status quo
                             sample_days: int = 30,
                             noise_std_kwh: float = 5.0,
                             noise_std_productivity: float = 0.02,
                             noise_std_injury: float = 0.005,
                             rng_seed: int = 42):
    """
    Simulate an A/B experiment:
    - Control period: office HVAC full, big ΔT.
    - Treatment period: office setback + floor spot cooling, small ΔT.

    We generate noisy daily data, then test whether the observed differences
    match the claims above (at 95% confidence).  If the test fails to reject
    the null (p > 0.05), the claim is falsified *with this sample size*.
    """
    rng = random.Random(rng_seed)

    # ---- True effects according to claims ----
    control = compute_impacts(control_delta_T, claims)
    treatment = compute_impacts(treatment_delta_T, claims)

    # Waste: extra HVAC kWh per day
    true_waste_control = claims.extra_kwh_per_degF_per_day * abs(control_delta_T)
    true_waste_treatment = claims.extra_kwh_per_degF_per_day * abs(treatment_delta_T)

    # Productivity loss fraction per worker per day
    # We'll measure output value (dollars/day/worker) – no noise in floor temp, noise in output
    true_prod_loss_control = control["productivity_loss_pct"] / 100.0
    true_prod_loss_treatment = treatment["productivity_loss_pct"] / 100.0

    # Injury rate per worker per day (annualized fraction / 250 days)
    daily_injury_rate_control = (control["injury_rate_multiplier"] *
                                 claims.base_annual_injury_rate / claims.annual_work_days)
    daily_injury_rate_treatment = (treatment["injury_rate_multiplier"] *
                                   claims.base_annual_injury_rate / claims.annual_work_days)

    # Generate noisy daily data
    # kWh
    control_kwh = [rng.gauss(true_waste_control, noise_std_kwh) for _ in range(sample_days)]
    treatment_kwh = [rng.gauss(true_waste_treatment, noise_std_kwh) for _ in range(sample_days)]
    # Productivity (dollars per worker per day) – base minus loss + noise
    base_val = claims.base_daily_productivity_value
    control_prod = [rng.gauss(base_val * (1 - true_prod_loss_control),
                              base_val * noise_std_productivity)
                    for _ in range(sample_days)]
    treatment_prod = [rng.gauss(base_val * (1 - true_prod_loss_treatment),
                                base_val * noise_std_productivity)
                      for _ in range(sample_days)]
    # Injuries per day (Poisson on lam = daily_rate * n_workers)
    control_injuries = [poisson(rng, daily_injury_rate_control * claims.num_floor_workers)
                        for _ in range(sample_days)]
    treatment_injuries = [poisson(rng, daily_injury_rate_treatment * claims.num_floor_workers)
                          for _ in range(sample_days)]

    # ---- Statistical tests (Welch two-sample t-test, one-sided) ----
    results = {}
    # 1. Waste difference (control > treatment)
    t_waste, p_waste = welch_t_greater(control_kwh, treatment_kwh)
    results['waste'] = {
        'mean_control': statistics.mean(control_kwh),
        'mean_treatment': statistics.mean(treatment_kwh),
        'diff_observed': statistics.mean(control_kwh) - statistics.mean(treatment_kwh),
        'p_value': p_waste, 'reject_null': p_waste < 0.05,
    }

    # 2. Productivity (treatment > control)
    t_prod, p_prod = welch_t_greater(treatment_prod, control_prod)
    results['productivity'] = {
        'mean_control': statistics.mean(control_prod),
        'mean_treatment': statistics.mean(treatment_prod),
        'diff_observed': statistics.mean(treatment_prod) - statistics.mean(control_prod),
        'p_value': p_prod, 'reject_null': p_prod < 0.05,
    }

    # 3. Injuries (control > treatment)
    t_inj, p_inj = welch_t_greater(control_injuries, treatment_injuries)
    results['injuries'] = {
        'mean_control': statistics.mean(control_injuries),
        'mean_treatment': statistics.mean(treatment_injuries),
        'diff_observed': statistics.mean(control_injuries) - statistics.mean(treatment_injuries),
        'p_value': p_inj, 'reject_null': p_inj < 0.05,
    }

    # Turnover: simulated as total over the period? We'll do a 30-day rate test using Poisson
    # but for simplicity we'll just note the expected annual difference (not enough data to test).
    results['turnover_note'] = (
        "Turnover requires longer observation (months/year). "
        "Expected annual extra turnover cost difference: "
        f"${control['extra_turnover_cost'] - treatment['extra_turnover_cost']:,.2f}"
    )

    return results, control, treatment

# ----------------------------------------------------------------------
# 4. MAIN: gradient scan + experiment
# ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Falsifiable HVAC gradient audit -- gradient scan + A/B experiment simulation."
    )
    parser.add_argument('--delta_T', type=float, default=15.0,
                        help='Control-scenario ΔT °F for the A/B experiment (default: 15)')
    parser.add_argument('--treatment_delta_T', type=float, default=3.0,
                        help='Treatment-scenario ΔT °F after intervention (default: 3)')
    parser.add_argument('--office_temp', type=float, default=72.0,
                        help='Office thermostat setpoint °F (default: 72)')
    parser.add_argument('--workers', type=int, default=20,
                        help='Number of floor workers (default: 20)')
    parser.add_argument('--electricity_rate', type=float, default=0.12,
                        help='Cost per kWh (default: 0.12)')
    parser.add_argument('--sample_days', type=int, default=30,
                        help='Sample days for the A/B simulation (default: 30)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility (default: 42)')
    args = parser.parse_args()

    claims = Claims(
        office_temp_F=args.office_temp,
        num_floor_workers=args.workers,
        electricity_cost_per_kwh=args.electricity_rate,
    )

    print("=" * 70)
    print("GRADIENT ANALYSIS: impacts as ΔT (floor − office) varies from 0 to 25°F")
    print("=" * 70)
    print(f"{'ΔT°F':>6} {'Floor°F':>8} {'Waste $':>10} {'ProdLoss%':>10} "
          f"{'InjMult':>8} {'Turn%':>8} {'Total $':>12}")
    print("-" * 70)
    for dt in range(0, 26, 5):
        r = compute_impacts(dt, claims)
        print(f"{dt:6.1f} {r['floor_temp_F']:8.1f} {r['annual_waste_cost']:10.0f} "
              f"{r['productivity_loss_pct']:9.1f} {r['injury_rate_multiplier']:8.2f} "
              f"{r['turnover_rate']:8.2%} {r['total_extra_annual_cost']:12.0f}")

    print("\n" + "=" * 70)
    print(f"EXPERIMENT SIMULATION ({args.sample_days}-day A/B test, "
          f"control ΔT={args.delta_T}°F vs. treatment ΔT={args.treatment_delta_T}°F)")
    print("=" * 70)
    exp_results, ctrl, trt = run_simulated_experiment(
        claims,
        treatment_delta_T=args.treatment_delta_T,
        control_delta_T=args.delta_T,
        sample_days=args.sample_days,
        noise_std_kwh=5.0,
        noise_std_productivity=0.02,
        noise_std_injury=0.005,
        rng_seed=args.seed,
    )

    print(f"\nControl period (ΔT={ctrl['delta_T_F']}°F, floor={ctrl['floor_temp_F']}°F):")
    print(f"  Avg extra HVAC kWh/day: {exp_results['waste']['mean_control']:.1f}")
    print(f"  Avg productivity $/worker/day: {exp_results['productivity']['mean_control']:.2f}")
    print(f"  Avg injuries/day: {exp_results['injuries']['mean_control']:.3f}")

    print(f"\nTreatment period (ΔT={trt['delta_T_F']}°F, floor={trt['floor_temp_F']}°F):")
    print(f"  Avg extra HVAC kWh/day: {exp_results['waste']['mean_treatment']:.1f}")
    print(f"  Avg productivity $/worker/day: {exp_results['productivity']['mean_treatment']:.2f}")
    print(f"  Avg injuries/day: {exp_results['injuries']['mean_treatment']:.3f}")

    print("\nHypothesis tests (one-sided t-test):")
    print(f"  Waste reduction:      p = {exp_results['waste']['p_value']:.4f}  "
          f"{'✅ Reject null' if exp_results['waste']['reject_null'] else '❌ Not significant'}")
    print(f"  Productivity increase: p = {exp_results['productivity']['p_value']:.4f}  "
          f"{'✅ Reject null' if exp_results['productivity']['reject_null'] else '❌ Not significant'}")
    print(f"  Injury reduction:      p = {exp_results['injuries']['p_value']:.4f}  "
          f"{'✅ Reject null' if exp_results['injuries']['reject_null'] else '❌ Not significant'}")
    print(exp_results['turnover_note'])

    print("\n👉 To falsify a claim, increase noise, reduce sample size, or change coefficients "
          "until p > 0.05. That shows the minimum detectable effect for your facility.\n"
          "Replace the dummy data with real measurements from a real intervention to audit the truth.")

if __name__ == "__main__":
    main()
