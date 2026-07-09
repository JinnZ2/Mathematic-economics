#!/usr/bin/env python3
"""
compare_iam.py – Compare this framework's projections with a minimal DICE model.
CC0. Stdlib + optional scipy/matplotlib.

Usage:
  python compare_iam.py --scenario rcp85 --horizon 2100 --plot
"""

import argparse
import math
from typing import Tuple, List

# ----------------------------------------------------------------------
# 1. Minimal DICE (DICE-2023R simplified) – stdlib only
# ----------------------------------------------------------------------
class MinimalDICE:
    """
    A reduced DICE-like carbon cycle and climate dynamics.
    Parameters from DICE-2023R (approximate, for demonstration).
    """
    # Carbon cycle: 3‑box model (atmosphere, upper ocean, deep ocean)
    # transfer coefficients (per 5 years)
    b12 = 0.12   # atmosphere -> upper
    b23 = 0.007  # upper -> deep
    # climate: heat capacity, feedback
    climate_sensitivity = 3.0  # °C per doubling CO2
    forcing_per_doubling = 3.8  # W/m²
    # preindustrial CO2
    co2_preind = 280.0  # ppm
    # initial conditions (2020)
    mat0 = 851.0   # GtC in atmosphere
    mup0 = 460.0   # GtC upper ocean
    mlo0 = 1740.0  # GtC deep ocean
    temp0 = 1.1    # °C above preindustrial
    # economic (simplified): emissions as fraction of output
    sigma0 = 0.35   # carbon intensity
    gsigma = -0.015 # growth rate of sigma
    # damage function coefficient
    a1 = 0.0
    a2 = 0.00236

    def __init__(self, start_year=2015, dt=5):
        self.year = start_year
        self.dt = dt
        self.mat = self.mat0
        self.mup = self.mup0
        self.mlo = self.mlo0
        self.temp = self.temp0

    def step(self, emissions: float) -> float:
        """
        Update carbon cycle and temperature for one time step (dt years).
        emissions: GtC emitted during the step.
        Returns global mean temperature change from preindustrial.
        """
        dt = self.dt
        # Carbon cycle
        self.mat += (emissions - self.b12 * self.mat + self.b12 * self.mup * (self.mat0/self.mup0 if self.mup0>0 else 1)) * dt/5.0
        # Simplified: use linear exchange
        # Actually, implement proper:
        # mat' = emissions - b12*mat + b21*mup  (b21 = b12 * mat0/mup0)
        b21 = self.b12 * (self.mat0 / self.mup0) if self.mup0 > 0 else 0
        mat_new = self.mat + (emissions - self.b12 * self.mat + b21 * self.mup) * (dt/5.0)
        mup_new = self.mup + (self.b12 * self.mat - b21 * self.mup - self.b23 * self.mup) * (dt/5.0)
        mlo_new = self.mlo + (self.b23 * self.mup) * (dt/5.0)
        self.mat, self.mup, self.mlo = mat_new, mup_new, mlo_new

        # Radiative forcing
        co2_ppm = self.mat * 2.123  # GtC to ppm
        forcing = self.forcing_per_doubling * math.log(co2_ppm / self.co2_preind) / math.log(2)

        # Temperature (one-box ocean)
        # equilibrium temp = sensitivity * forcing / forcing_per_doubling
        teq = self.climate_sensitivity * forcing / self.forcing_per_doubling
        # adjustment time ~ 50 years -> decay factor
        decay = math.exp(-dt / 50.0)
        self.temp = teq * (1 - decay) + self.temp * decay
        return self.temp

def dice_emissions(year: float, scenario: str) -> float:
    """
    Placeholder emissions trajectory based on scenario.
    GtC per year.
    """
    if scenario == "rcp85":
        # rising
        return 10.0 + 0.3 * (year - 2015)
    elif scenario == "rcp45":
        return 10.0 + 0.05 * (year - 2015)
    elif scenario == "rcp26":
        return max(0, 10.0 - 0.2 * (year - 2015))
    return 10.0

# ----------------------------------------------------------------------
# 2. Our framework's proxy: OSDI and Energy Cost trend model
# ----------------------------------------------------------------------
def our_model_projection(year: float) -> Tuple[float, float]:
    """
    Simplified placeholder: OSDI and Energy Cost based on historical hindcast trend.
    Replace with actual call to the unified simulation for production use.
    """
    # Very rough trend extrapolation
    osdi = 0.5 + 0.005 * (year - 1950)  # rising collective dependency
    energy_cost = 2.0 + 0.05 * (year - 1950)  # rising thermodynamic cost
    return osdi, energy_cost

# ----------------------------------------------------------------------
# 3. Comparison runner and plot
# ----------------------------------------------------------------------
def run_comparison(scenario: str, horizon: int = 2100):
    dice = MinimalDICE(start_year=2015)
    years = list(range(2015, horizon+1, 5))  # DICE step 5 years
    dice_temps = []
    dice_temps_anomaly = []  # relative to preindustrial
    osdi_vals = []
    energy_cost_vals = []
    for yr in years:
        em = dice_emissions(yr, scenario)
        temp = dice.step(em)
        dice_temps_anomaly.append(temp)
        dice_temps.append(temp + 14.0)  # approx global mean temp
        osdi, ec = our_model_projection(yr)
        osdi_vals.append(osdi)
        energy_cost_vals.append(ec)

    # Output table
    print("Year\tDICE_Temp_anom\tOSDI\tEnergy_Cost")
    for i, yr in enumerate(years):
        print(f"{yr}\t{dice_temps_anomaly[i]:.2f}\t\t{osdi_vals[i]:.3f}\t{energy_cost_vals[i]:.2f}")

    return years, dice_temps_anomaly, osdi_vals, energy_cost_vals

def main():
    parser = argparse.ArgumentParser(description="IAM comparison.")
    parser.add_argument("--scenario", choices=["rcp85", "rcp45", "rcp26"], default="rcp85")
    parser.add_argument("--horizon", type=int, default=2100)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()

    yrs, temp, osdi, ec = run_comparison(args.scenario, args.horizon)
    if args.plot:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed.")
            return
        fig, ax1 = plt.subplots()
        ax1.plot(yrs, temp, 'b-', label="DICE temp anomaly (°C)")
        ax1.set_ylabel("Temp anomaly (°C)", color='b')
        ax2 = ax1.twinx()
        ax2.plot(yrs, osdi, 'r-', label="OSDI")
        ax2.plot(yrs, ec, 'g-', label="Energy Cost")
        ax2.set_ylabel("Index", color='r')
        lines = ax1.get_lines() + ax2.get_lines()
        labels = [l.get_label() for l in lines]
        plt.legend(lines, labels)
        plt.title(f"IAM Comparison ({args.scenario})")
        plt.savefig("iam_comparison.png")
        plt.close()
        print("Plot saved to iam_comparison.png")

if __name__ == "__main__":
    main()
