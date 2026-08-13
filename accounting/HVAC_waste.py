#!/usr/bin/env python3
"""
HVAC Waste Audit: Office Conditioning for Imaginary Customers

This script quantifies the waste of running full HVAC in office areas year-round
under the pretext of rare customer visits, while shop floor workers have none.
All assumptions are clearly stated so any auditor (human or AI) can trace the logic.
"""

import sys
from datetime import date

# =============================================================================
# CONFIGURABLE ASSUMPTIONS
# Change these values to match your facility's actual data.
# =============================================================================

# Office area served by the "customer-ready" HVAC
OFFICE_AREA_SQFT = 2_000            # square feet

# Annual HVAC energy cost per square foot (heating + cooling).
# Typical industrial office: $1.00 - $2.00/sqft depending on climate.
ANNUAL_HVAC_COST_PER_SQFT = 1.50   # dollars

# Number of days per year when HVAC must run at full comfort level
# because a customer visit is scheduled.  Includes a buffer for setup/cleanup.
SCHEDULED_VISITOR_DAYS = 5          # actual visit days
BUFFER_DAYS = 2                     # day before + day after each visit (simplified)
FULL_HVAC_DAYS = SCHEDULED_VISITOR_DAYS + BUFFER_DAYS

# Percentage of full energy cost used when the system runs in "setback" mode
# (minimal conditioning to prevent freezing/pipes or extreme heat, no comfort).
SETBACK_COST_FACTOR = 0.30          # 30% of full consumption

# Cost to add a single spot cooling/heating station on the shop floor
# (e.g., a portable evaporative cooler or high-volume fan per worker).
SPOT_COMFORT_COST_PER_WORKER = 350  # dollars per year per worker (capital + energy)

# Number of floor workers who could benefit from redirected savings
FLOOR_WORKERS = 20

# Provenance: where the numeric assumptions came from. Default = hypothesis
# only. Override at call time with e.g. "measured_facility_XYZ_2025" once real
# records back the coefficients.
PROVENANCE = "illustrative_default"

FALSIFIER = (
    "STRUCTURAL CLAIM: full HVAC on non-visitor days is waste that could "
    "instead fund floor spot-comfort stations.\n"
    "FALSIFIED IF, against real visitor logs / energy records / customer feedback:\n"
    "  (a) unannounced visits are more frequent than FULL_HVAC_DAYS "
    "(the buffer is undersized); OR\n"
    "  (b) setback mode causes pipe damage, mold, or startup-overshoot cost "
    "exceeding annual_waste on any real facility; OR\n"
    "  (c) customer perception of a small temperature deviation on transition "
    "days produces measurable revenue loss > annual_waste (test on a real "
    "customer visit).\n"
    "If any of (a),(b),(c) hold, update the assumption (SCHEDULED_VISITOR_DAYS, "
    "SETBACK_COST_FACTOR, or the audit's scope); do not retune the ratio."
)

# =============================================================================
# AUDIT CALCULATION ENGINE
# Every step is commented and uses only elementary arithmetic.
# =============================================================================

def audit_hvac_waste(area_sqft, annual_cost_per_sqft, full_days,
                     setback_factor, spot_cost_per_worker, floor_workers,
                     year=date.today().year,
                     provenance=PROVENANCE):
    """
    Perform the waste audit and return a dictionary of results.
    All monetary values are in dollars. `provenance` tags the inputs so a
    downstream reader knows whether these numbers are illustrative_default or
    measured.
    """
    # --- 1. Total current annual cost (running full HVAC 365 days) ---
    total_annual_cost = area_sqft * annual_cost_per_sqft

    # --- 2. Daily full-HVAC cost ---
    full_daily_cost = total_annual_cost / 365.0

    # --- 3. Daily setback cost (minimal conditioning) ---
    setback_daily_cost = full_daily_cost * setback_factor

    # --- 4. Number of days when full HVAC is NOT required ---
    non_full_days = 365 - full_days

    # --- 5. Annual waste = cost difference on non-full days ---
    waste_per_non_full_day = full_daily_cost - setback_daily_cost
    annual_waste = non_full_days * waste_per_non_full_day

    # --- 6. Proposed new total annual cost ---
    new_annual_cost = (full_days * full_daily_cost) + (non_full_days * setback_daily_cost)

    # --- 7. Savings ---
    annual_savings = total_annual_cost - new_annual_cost

    # --- 8. What those savings could buy on the floor ---
    stations_possible = annual_savings / spot_cost_per_worker
    workers_covered = min(stations_possible, floor_workers)
    floor_investment = workers_covered * spot_cost_per_worker
    remaining_savings = annual_savings - floor_investment

    return {
        "area_sqft": area_sqft,
        "annual_cost_per_sqft": annual_cost_per_sqft,
        "total_annual_cost": total_annual_cost,
        "full_daily_cost": full_daily_cost,
        "setback_daily_cost": setback_daily_cost,
        "full_hvac_days": full_days,
        "non_full_days": non_full_days,
        "waste_per_non_full_day": waste_per_non_full_day,
        "annual_waste": annual_waste,
        "new_annual_cost": new_annual_cost,
        "annual_savings": annual_savings,
        "spot_cost_per_worker": spot_cost_per_worker,
        "stations_possible": stations_possible,
        "floor_workers": floor_workers,
        "workers_covered": int(workers_covered),
        "floor_investment": floor_investment,
        "remaining_savings": remaining_savings,
        "year": year,
        "provenance": provenance,
        "falsifier": FALSIFIER,
    }


def format_report(results):
    """Generate a human- and AI-readable audit report."""
    r = results
    provenance_banner = ""
    if r.get('provenance') == "illustrative_default":
        provenance_banner = (
            f" PROVENANCE: {r.get('provenance', 'unstated')}\n"
            f"   ⚠ Values below are derived from ILLUSTRATIVE DEFAULT inputs.\n"
            f"     Substitute measured facility data to make figures real.\n"
        )
    else:
        provenance_banner = f" PROVENANCE: {r.get('provenance', 'unstated')}\n"

    report = f"""
================================================================================
 HVAC CUSTOMER-READY OFFICE WASTE AUDIT – {r['year']}
================================================================================
{provenance_banner} ASSUMPTIONS
   Office area:                          {r['area_sqft']:>8,} sq ft
   Annual HVAC cost per sq ft:           ${r['annual_cost_per_sqft']:>8.2f}
   Days requiring full HVAC (visits+buffer): {r['full_hvac_days']:>3} days
   Setback energy factor:                {r['waste_per_non_full_day'] / (r['full_daily_cost'] - r['setback_daily_cost']) if r['full_daily_cost'] != r['setback_daily_cost'] else 0:.0%} (so setback uses {r['setback_daily_cost']/r['full_daily_cost']:.0%} of full)
   Floor spot comfort cost per worker:   ${r['spot_cost_per_worker']:>8,.2f}/year

 CURRENT STATE (full HVAC year-round)
   Total annual office HVAC cost:        ${r['total_annual_cost']:>8,.2f}
   Daily full conditioning cost:         ${r['full_daily_cost']:>8,.2f}

 WASTE IDENTIFIED
   On {r['non_full_days']} non-visitor days, full comfort is wasted.
   Cost difference per day (full - setback): ${r['waste_per_non_full_day']:>8,.2f}
   Annual waste = {r['non_full_days']} × ${r['waste_per_non_full_day']:,.2f} = ${r['annual_waste']:>8,.2f}

 PROPOSED JIT HVAC MODEL
   Full HVAC only on {r['full_hvac_days']} visitor days.
   Setback mode on the remaining {r['non_full_days']} days.
   New annual office HVAC cost:          ${r['new_annual_cost']:>8,.2f}
   ANNUAL SAVINGS:                       ${r['annual_savings']:>8,.2f}

 REINVESTMENT POTENTIAL (example)
   Savings could fund spot cooling/heating for up to {r['stations_possible']:.1f} workers.
   Covering all {r['floor_workers']} floor workers would cost: ${r['floor_investment']:>8,.2f}
   Remaining savings after floor investment: ${r['remaining_savings']:>8,.2f}

 BOTTOM LINE
   “Paying to condition empty air for 360 imaginary customer days wastes
    ${r['annual_waste']:,.2f} every year.  With just-in-time HVAC, we keep the
    customer experience perfect on the 5 days that matter, slash overhead,
    and improve productivity & safety on the floor for free.”
================================================================================

 FALSIFICATION CONTRACT
{r['falsifier']}
================================================================================
"""
    return report


def main():
    # Optional: override assumptions via command line (kept simple)
    if len(sys.argv) > 1:
        print("Usage: python hvac_waste_audit.py   (edit script for facility data)")
        print("Current defaults are shown below.")
        print("You can also import and call audit_hvac_waste() with custom parameters.")
        sys.exit(1)

    results = audit_hvac_waste(
        area_sqft=OFFICE_AREA_SQFT,
        annual_cost_per_sqft=ANNUAL_HVAC_COST_PER_SQFT,
        full_days=FULL_HVAC_DAYS,
        setback_factor=SETBACK_COST_FACTOR,
        spot_cost_per_worker=SPOT_COMFORT_COST_PER_WORKER,
        floor_workers=FLOOR_WORKERS,
    )
    print(format_report(results))


if __name__ == "__main__":
    main()
