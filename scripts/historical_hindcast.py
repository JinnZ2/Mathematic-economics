#!/usr/bin/env python3
"""
historical_hindcast.py – Run the 13 economic equations over a historical range.
CC0 – No Rights Reserved. Stdlib + optional matplotlib.

Usage examples:
  # 1960–2023, annual, log-speed model, use cached data, plot
  python historical_hindcast.py --start 1960 --end 2023 --freq annual --speed log_1900 --cache --plot

  # Interactive (no arguments)
  python historical_hindcast.py
"""

import argparse
import csv
import math
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ----------------------------------------------------------------------
# 1. Data fetching – tries live FRED/BLS, falls back to cache or simulation
# ----------------------------------------------------------------------
try:
    import requests  # optional, for live API; not required for cached runs
except ImportError:
    requests = None

# In a real deployment, these would be real series IDs; here we use stubs.
FRED_SERIES = {
    "labor_share": "PRS85006173",          # BLS labor share
    "M2": "M2SL",                          # Money supply
    "monetary_base": "BOGMBASE",
    "currency": "CURRCIR",
    "wage": "AHETPI",                      # Average hourly earnings
    "SP500": "SP500",                      # index
    "corp_profits": "CP",
    "compensation": "COE",
    "fed_assets": "WALCL",
    "med_income": "MEHOINUSA672N",
    "top1_share": "WFRBST01134",
    "bottom50_share": "WFRBSB50215",
    "unemp": "UNRATE",
}

CACHE_DIR = "historical_data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_fred_value(series_id: str, year: int, freq: str = "annual") -> Optional[float]:
    """
    Stub – in production, call FRED API. Here we return simulated data based on
    the series and year, so the script runs without a key.
    To use real data, replace this function with API calls and caching.
    """
    # Simulated data loosely matching historical trends (for testing the flow).
    # Not meant to be accurate; used only to demonstrate the computation pipeline.
    if series_id == "PRS85006173":
        # Labor share (percent) declining
        return max(50, 64 - 0.3 * (year - 1950))
    if series_id == "M2SL":
        return 300 * math.exp(0.06 * (year - 1950))
    if series_id == "BOGMBASE":
        return 50 * math.exp(0.05 * (year - 1950))
    if series_id == "WFRBST01134":
        # Top 1% wealth share
        return 30 + 0.3 * (year - 1980) if year > 1980 else 30
    if series_id == "WFRBSB50215":
        # Bottom 50%
        return 3 - 0.05 * (year - 1980) if year > 1980 else 5
    if series_id == "AHETPI":
        return 2 + 0.08 * (year - 1950)
    if series_id == "SP500":
        return 10 * math.exp(0.07 * (year - 1950))
    if series_id == "UNRATE":
        return 5 + (2 if year < 1980 else 4) * math.sin((year - 1950) / 10)
    if series_id == "MEHOINUSA672N":
        return 3000 + 100 * (year - 1950)
    if series_id == "CP":
        return 50 * math.exp(0.06 * (year - 1950))
    if series_id == "COE":
        return 500 * math.exp(0.05 * (year - 1950))
    if series_id == "WALCL":
        return 1000 * math.exp(0.04 * (year - 1950))
    return None

# ----------------------------------------------------------------------
# 2. Equation computations (from the README)
# ----------------------------------------------------------------------
def compute_equations(data: Dict[str, float]) -> Dict[str, float]:
    """
    Compute the 13 structural equations plus OSDI from the data dict.
    Returns a dict of equation outputs.
    """
    # Extract needed values
    labor_share = data.get("labor_share", 60)       # percent
    m2 = data.get("M2", 1000)
    monetary_base = data.get("monetary_base", 100)
    corp_profits = data.get("corp_profits", 100)
    compensation = data.get("compensation", 500)
    top1 = data.get("top1_share", 30)
    bottom50 = data.get("bottom50_share", 3)
    med_income = data.get("med_income", 5000)
    sp500 = data.get("SP500", 100)
    wage = data.get("wage", 5)
    unemp = data.get("unemp", 5)
    fed_assets = data.get("fed_assets", 2000)

    # Convert labor share to fraction
    ls = labor_share / 100.0

    # Equation 1: VE/VL
    ve_vl = (1 - ls) / ls if ls > 0 else float('inf')

    # Equation 2: SID (approximate using ratio of corporate profits to total income)
    # Simplified: SID = C/(C+P) where C = government spending proxy (fed_assets), P = corporate profits
    total_resources = abs(corp_profits) + abs(compensation)
    sid = abs(compensation) / total_resources if total_resources > 0 else 0

    # Equation 3: RI (risk inequality) – worker risk proxy from unemployment, investor risk from SP500 volatility
    worker_risk = unemp / 100.0 + 0.1  # simplistic
    investor_risk = 0.05  # assumed low
    ri = worker_risk / investor_risk if investor_risk > 0 else float('inf')

    # Equation 4: DI – power concentration using top1/bottom50 ratio
    di_ratio = top1 / bottom50 if bottom50 > 0 else float('inf')

    # Equation 5: LWR – median income vs SP500 growth
    wealth_labor = med_income
    wealth_owner = sp500 * 10  # arbitrary scaling
    lwr = wealth_labor / wealth_owner if wealth_owner > 0 else float('inf')

    # Equation 6: MSI – money creation socialist index
    msi = monetary_base / m2 if m2 > 0 else 1

    # Equation 7: BSC – bailout socialism coefficient (rough: Fed assets vs corp profits)
    bsc = fed_assets / abs(corp_profits) if corp_profits != 0 else float('inf')

    # Equation 8: MM – money multiplier (M2/monetary base)
    mm = m2 / monetary_base if monetary_base > 0 else float('inf')

    # Equation 9: ISR – infrastructure subsidy ratio (hard to compute, placeholder)
    isr = 10.0  # assumed constant for demonstration

    # Equation 10: UFR – upward flow rate, change in top1 vs bottom50
    # We'll compute in the loop using previous values; here placeholder
    ufr = (top1 / bottom50)  # static ratio; dynamic handled outside

    # Equation 11: ER – extraction rate
    er = 1 - ls

    # Equation 12: HHI – market concentration (placeholder, from corporate profits concentration)
    hhi = 3500  # illustrative

    # Equation 13: SD – semantic drift not applicable

    # Composite OSDI
    osdi = (sid * 0.3 + msi * 0.2 + (isr/20.0) * 0.2 + min(bsc/5, 1) * 0.15 + min(mm/10, 1) * 0.15)

    return {
        "year": data["year"],
        "VE_VL": round(ve_vl, 4),
        "SID": round(sid, 4),
        "RI": round(ri, 4),
        "DI_ratio": round(di_ratio, 2),
        "LWR": round(lwr, 4),
        "MSI": round(msi, 4),
        "BSC": round(bsc, 4),
        "MM": round(mm, 4),
        "ISR": isr,
        "UFR": round(ufr, 2),
        "ER": round(er, 4),
        "HHI": hhi,
        "OSDI": round(osdi, 4),
    }

# ----------------------------------------------------------------------
# 3. Logarithmic speed factor
# ----------------------------------------------------------------------
def speed_factor(year: int, model: str = "log_1900") -> float:
    """
    A multiplier representing how much faster bureaucratic/transaction processes are
    compared to a baseline. 1.0 = no change.
    """
    if model == "none":
        return 1.0
    elif model == "log_1900":
        base = 1900
        ref = 2026 - base
        if year <= base:
            return 1.0
        return math.log(year - base) / math.log(ref) if ref > 0 else 1.0
    elif model == "step":
        # Step function based on technology eras
        if year < 1960:
            return 1.0
        elif year < 1980:
            return 1.2
        elif year < 1995:
            return 1.5
        elif year < 2010:
            return 2.0
        else:
            return 3.0
    else:
        return 1.0

def apply_speed_effect(eq_output: Dict[str, float], speed: float) -> Dict[str, float]:
    """
    Adjust certain equations that involve time or friction.
    For example, UFR might increase with speed (wealth flows faster),
    and institutional friction terms (BSC, ISR) might decrease.
    """
    # Simple heuristic: UFR scales with speed, friction measures scale inversely.
    adjusted = eq_output.copy()
    adjusted["UFR"] = eq_output["UFR"] * speed
    adjusted["BSC"] = eq_output["BSC"] / math.sqrt(speed) if speed > 0 else eq_output["BSC"]
    adjusted["ISR"] = eq_output["ISR"] / speed if speed > 0 else eq_output["ISR"]
    # Recompute OSDI with adjusted components? We'll keep OSDI as originally computed,
    # but could recalc. For simplicity, we leave OSDI untouched; the output includes both raw and adjusted metrics.
    adjusted["speed_factor"] = speed
    return adjusted

# ----------------------------------------------------------------------
# 4. Main loop and output
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Historical hindcast of the 13 equations.")
    parser.add_argument("--start", type=int, default=1947)
    parser.add_argument("--end", type=int, default=2026)
    parser.add_argument("--freq", choices=["annual", "quarterly"], default="annual")
    parser.add_argument("--speed", choices=["log_1900", "step", "none"], default="log_1900")
    parser.add_argument("--cache", action="store_true", help="Use cached data")
    parser.add_argument("--plot", action="store_true", help="Generate plot (requires matplotlib)")
    args = parser.parse_args()

    years = range(args.start, args.end + 1)
    if args.freq == "quarterly":
        # Quick implementation: treat quarters as fractional years (not fully fleshed out)
        years = [y + q/4.0 for y in years for q in range(4)]  # float years

    results = []
    prev_top1 = prev_bottom50 = None

    for yr in years:
        year_int = int(yr) if isinstance(yr, float) else yr
        # Fetch data for this year
        data = {"year": yr}
        for name, sid in FRED_SERIES.items():
            val = fetch_fred_value(sid, year_int, args.freq)
            if val is not None:
                data[name] = val

        # Compute UFR dynamically using previous values
        if prev_top1 is not None and prev_bottom50 is not None:
            d_top = data.get("top1_share", prev_top1) - prev_top1
            d_bot = data.get("bottom50_share", prev_bottom50) - prev_bottom50
            if d_bot != 0:
                data["UFR_dynamic"] = d_top / d_bot
            else:
                data["UFR_dynamic"] = float('inf')
        else:
            data["UFR_dynamic"] = 0.0
        prev_top1 = data.get("top1_share", 0)
        prev_bottom50 = data.get("bottom50_share", 0)

        eq = compute_equations(data)
        # Overwrite UFR with dynamic value if available
        if "UFR_dynamic" in data:
            eq["UFR"] = data["UFR_dynamic"]

        sp = speed_factor(year_int, args.speed)
        adjusted = apply_speed_effect(eq, sp)
        results.append(adjusted)

    # Output CSV
    csv_path = "historical_hindcast_output.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Results written to {csv_path}")

    # Optional plot
    if args.plot:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not installed; skipping plot.")
            return
        yrs = [r["year"] for r in results]
        osdi_vals = [r["OSDI"] for r in results]
        ufr_vals = [r["UFR"] for r in results]
        plt.figure()
        plt.plot(yrs, osdi_vals, label="OSDI")
        plt.plot(yrs, ufr_vals, label="UFR (speed-adjusted)")
        plt.legend()
        plt.title("Historical Hindcast")
        plt.savefig("historical_hindcast.png")
        plt.close()
        print("Plot saved to historical_hindcast.png")

if __name__ == "__main__":
    main()
