#!/usr/bin/env python3
"""
GENERIC HVAC INEQUITY AUDIT
----------------------------
Observed pattern: office spaces fully conditioned year-round under the
pretext of rare customer visits, while the shop floor has no climate control.

This script models the cost consequences as a function of the temperature
difference (ΔT) between floor and office. All relationships are stated as
falsifiable claims. An experimental design with synthetic data demonstrates
how real-world measurements can validate or disprove each claim.

Usage:
    python hvac_gradient_audit.py --delta_T 15 --office_temp 72 --workers 20
    python hvac_gradient_audit.py --help

Output:
    - Gradient scan of impacts across a range of ΔT
    - Simulated A/B experiment with statistical tests
"""

import argparse
import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# FALSIFIABLE CLAIMS – change these to match empirical evidence
# ----------------------------------------------------------------------
@dataclass
class Claims:
    """
    Each coefficient is a hypothesis that can be tested.
    Set any to 0.0 to simulate 'no effect' and watch the statistical
    test lose significance — that's the falsifiability in action.
    """
    extra_kwh_per_degF_per_day: float = 2.0       # Heat transfer from floor to office
    productivity_loss_pct_per_degF: float = 1.5    # % output loss per °F outside 60-75°F
    injury_rate_rise_per_degF_above_85: float = 0.02  # Multiplier increase per °F above 85
    turnover_increase_pct_per_degF_above_80: float = 0.5  # Extra turnover % per °F >80
    office_temp_F: float = 72.0
    # Economic defaults
    electricity_cost_per_kwh: float = 0.12
    annual_work_days: int = 250
    base_daily_productivity_value: float = 500.0   # $ output per floor worker/day
    base_annual_injury_rate: float = 0.03          # 3% of workforce injured annually
    base_annual_turnover_rate: float = 0.15        # 15% voluntary turnover
    cost_per_turnover: float = 5000.0              # Recruitment + training
    num_floor_workers: int = 20

# ----------------------------------------------------------------------
# IMPACT COMPUTATION (pure functions, no side effects)
# ----------------------------------------------------------------------
def compute_impacts(delta_T_F: float, claims: Claims) -> Dict:
    """Return annualized costs for a given temperature gap."""
    floor_temp = claims.office_temp_F + delta_T_F

    # 1. Waste: extra HVAC energy to maintain office against heat/cold from floor
    extra_kwh_per_day = claims.extra_kwh_per_degF_per_day * abs(delta_T_F)
    annual_waste_cost = extra_kwh_per_day * claims.annual_work_days * claims.electricity_cost_per_kwh

    # 2. Productivity loss (symmetrical outside comfort band 60-75°F)
    if floor_temp > 75:
        uncomfortable_deg = floor_temp - 75
    elif floor_temp < 60:
        uncomfortable_deg = 60 - floor_temp
    else:
        uncomfortable_deg = 0
    prod_loss_pct = min(uncomfortable_deg * claims.productivity_loss_pct_per_degF, 100.0)
    daily_loss = claims.base_daily_productivity_value * (prod_loss_pct / 100)
    annual_productivity_loss = daily_loss * claims.annual_work_days * claims.num_floor_workers

    # 3. Injury risk (heat stress only, >85°F)
    injury_mult = 1.0
    if floor_temp > 85:
        injury_mult += claims.injury_rate_rise_per_degF_above_85 * (floor_temp - 85)
    base_injuries = claims.base_annual_injury_rate * claims.num_floor_workers
    extra_injuries = base_injuries * (injury_mult - 1)

    # 4. Turnover (heat only, >80°F)
    turnover_rate = claims.base_annual_turnover_rate
    if floor_temp > 80:
        turnover_rate += (claims.turnover_increase_pct_per_degF_above_80
                          * (floor_temp - 80) / 100.0)
    extra_turnovers = (turnover_rate - claims.base_annual_turnover_rate) * claims.num_floor_workers
    extra_turnover_cost = extra_turnovers * claims.cost_per_turnover

    return {
        "delta_T_F": delta_T_F,
        "floor_temp_F": floor_temp,
        "annual_waste_cost": annual_waste_cost,
        "productivity_loss_pct": prod_loss_pct,
        "annual_productivity_loss": annual_productivity_loss,
        "injury_multiplier": injury_mult,
        "extra_annual_injuries": extra_injuries,
        "turnover_rate": turnover_rate,
        "extra_annual_turnovers": extra_turnovers,
        "extra_turnover_cost": extra_turnover_cost,
        "total_extra_annual_cost": annual_waste_cost + annual_productivity_loss + extra_turnover_cost
    }

# ----------------------------------------------------------------------
# FALSIFIABLE EXPERIMENT SIMULATION
# ----------------------------------------------------------------------
def run_simulated_experiment(claims: Claims,
                             control_delta_T: float,
                             treatment_delta_T: float,
                             sample_days: int = 30,
                             seed: int = 42) -> Tuple[Dict, Dict, Dict]:
    """
    Generate synthetic daily data using the claims, then test whether
    a 30-day intervention (reducing ΔT) produces statistically significant
    improvements. Returns test results and the underlying impact dicts.
    """
    rng = np.random.default_rng(seed)
    ctrl = compute_impacts(control_delta_T, claims)
    trt = compute_impacts(treatment_delta_T, claims)

    # True daily effects (before noise)
    true_kwh_ctrl = claims.extra_kwh_per_degF_per_day * abs(control_delta_T)
    true_kwh_trt  = claims.extra_kwh_per_degF_per_day * abs(treatment_delta_T)
    true_prod_loss_ctrl = ctrl["productivity_loss_pct"] / 100.0
    true_prod_loss_trt  = trt["productivity_loss_pct"] / 100.0
    daily_inj_rate_ctrl = (ctrl["injury_multiplier"] * claims.base_annual_injury_rate
                           / claims.annual_work_days)
    daily_inj_rate_trt  = (trt["injury_multiplier"] * claims.base_annual_injury_rate
                           / claims.annual_work_days)

    # Generate noisy daily measurements
    noise_kwh = 5.0
    noise_prod = claims.base_daily_productivity_value * 0.02
    control_kwh = rng.normal(true_kwh_ctrl, noise_kwh, sample_days)
    treatment_kwh = rng.normal(true_kwh_trt, noise_kwh, sample_days)
    control_prod = rng.normal(claims.base_daily_productivity_value * (1 - true_prod_loss_ctrl),
                              noise_prod, sample_days)
    treatment_prod = rng.normal(claims.base_daily_productivity_value * (1 - true_prod_loss_trt),
                                noise_prod, sample_days)
    control_inj = rng.poisson(daily_inj_rate_ctrl * claims.num_floor_workers, sample_days)
    treatment_inj = rng.poisson(daily_inj_rate_trt * claims.num_floor_workers, sample_days)

    # Statistical tests (one-sided where direction is predicted)
    _, p_waste = stats.ttest_ind(control_kwh, treatment_kwh, alternative='greater')
    _, p_prod = stats.ttest_ind(treatment_prod, control_prod, alternative='greater')
    _, p_inj = stats.ttest_ind(control_inj, treatment_inj, alternative='greater')

    results = {
        'waste_p': p_waste, 'prod_p': p_prod, 'inj_p': p_inj,
        'waste_ctrl_mean': np.mean(control_kwh), 'waste_trt_mean': np.mean(treatment_kwh),
        'prod_ctrl_mean': np.mean(control_prod), 'prod_trt_mean': np.mean(treatment_prod),
        'inj_ctrl_mean': np.mean(control_inj), 'inj_trt_mean': np.mean(treatment_inj),
        'turnover_annual_diff': ctrl['extra_turnover_cost'] - trt['extra_turnover_cost']
    }
    return results, ctrl, trt

# ----------------------------------------------------------------------
# REPORT GENERATION
# ----------------------------------------------------------------------
def print_gradient_scan(claims: Claims):
    """Show how costs scale with ΔT from 0 to 25°F."""
    print("\n" + "="*80)
    print("GRADIENT SCAN — Annual impacts as floor‑office temperature gap widens")
    print("="*80)
    header = f"{'ΔT°F':>6} {'Floor°F':>8} {'Waste $':>10} {'ProdLoss%':>10} {'InjMult':>8} {'Turn%':>8} {'Total $':>12}"
    print(header)
    print("-"*80)
    for dt in range(0, 26, 5):
        r = compute_impacts(dt, claims)
        print(f"{dt:6.1f} {r['floor_temp_F']:8.1f} {r['annual_waste_cost']:10.0f} "
              f"{r['productivity_loss_pct']:9.1f} {r['injury_multiplier']:8.2f} "
              f"{r['turnover_rate']:8.2%} {r['total_extra_annual_cost']:12.0f}")

def print_experiment(claims: Claims, control_dT: float, treatment_dT: float):
    """Run experiment and display falsifiable test results."""
    res, ctrl, trt = run_simulated_experiment(claims, control_dT, treatment_dT)
    print("\n" + "="*80)
    print("FALSIFIABLE EXPERIMENT (30-day A/B simulation)")
    print("="*80)
    print(f"Control ΔT:   {control_dT}°F  (floor {ctrl['floor_temp_F']}°F)")
    print(f"Treatment ΔT: {treatment_dT}°F  (floor {trt['floor_temp_F']}°F)")
    print(f"\nDaily extra HVAC kWh — Control: {res['waste_ctrl_mean']:.1f}  Treatment: {res['waste_trt_mean']:.1f}")
    print(f"Productivity $/worker   — Control: {res['prod_ctrl_mean']:.2f}  Treatment: {res['prod_trt_mean']:.2f}")
    print(f"Injuries/day (total)    — Control: {res['inj_ctrl_mean']:.3f}  Treatment: {res['inj_trt_mean']:.3f}")
    print(f"\nOne‑sided t‑test p‑values (smaller = stronger evidence of improvement):")
    print(f"  Waste reduction:      p = {res['waste_p']:.4f} {'✅' if res['waste_p']<0.05 else '❌'}")
    print(f"  Productivity increase: p = {res['prod_p']:.4f} {'✅' if res['prod_p']<0.05 else '❌'}")
    print(f"  Injury reduction:      p = {res['inj_p']:.4f} {'✅' if res['inj_p']<0.05 else '❌'}")
    print(f"  Expected annual turnover cost difference: ${res['turnover_annual_diff']:,.2f}")
    print("\n👉 If a p‑value > 0.05, the corresponding claim is NOT supported by this data.")
    print("   Change Claims coefficients or increase sample size to explore sensitivity.")

# ----------------------------------------------------------------------
# CLI ENTRY POINT
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Universal HVAC inequity audit – gradient model with falsifiable experiment."
    )
    parser.add_argument('--delta_T', type=float, default=15.0,
                        help='Temperature gap (°F) for the experiment control scenario (default: 15)')
    parser.add_argument('--office_temp', type=float, default=72.0,
                        help='Office thermostat setpoint °F (default: 72)')
    parser.add_argument('--workers', type=int, default=20,
                        help='Number of floor workers (default: 20)')
    parser.add_argument('--electricity_rate', type=float, default=0.12,
                        help='Cost per kWh (default: 0.12)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    args = parser.parse_args()

    # Configure claims from CLI
    claims = Claims(
        office_temp_F=args.office_temp,
        num_floor_workers=args.workers,
        electricity_cost_per_kwh=args.electricity_rate
    )
    treatment_dT = 3.0   # ideal reduced gap (e.g., using spot cooling)

    print_gradient_scan(claims)
    print_experiment(claims, control_dT=args.delta_T, treatment_dT=treatment_dT)

    print("\n" + "="*80)
    print("This tool models the *observed pattern*, not any single facility.")
    print("All relationships are adjustable hypotheses. Gather real data to validate or refute.")
    print("="*80)

if __name__ == "__main__":
    main()
