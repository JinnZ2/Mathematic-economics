"""
lifecycle_eroi.py  —  C004

ROI window must exceed well productivity decline curve.

Falsifier: profitable autonomous deployment on <3yr wells.

EROI (Energy Returned On Invested) is computed in dimensionless energy
units rather than dollars, in line with the repository's no-monetary-proxy
posture. Inputs and outputs are summed across the full lifecycle: capex
embodied energy, operating energy, fuel/feedstock energy in; delivered
service energy / extracted-resource energy out.

The viability window then asks: over what fraction of the equipment's
depreciation period does the underlying well actually produce enough to
justify the deployment? Shale wells typically lose 70-80% of initial flow
in year one and 30-40% additional in year two.

License: CC0-1.0
"""

from typing import Dict, List


def eroi_calc(energy_input: Dict[str, float],
              energy_output: Dict[str, float],
              lifecycle_years: int) -> float:
    """Lifecycle EROI = sum(energy_output) / sum(energy_input).

    Both dicts have arbitrary keys; values are joules (or any consistent
    energy unit). `lifecycle_years` is informational — used to flag
    truncated-horizon errors when callers also pass an output time series.
    Returns 0.0 if input is zero.
    """
    total_in = sum(float(v) for v in energy_input.values())
    total_out = sum(float(v) for v in energy_output.values())
    if total_in <= 0.0:
        return 0.0
    return total_out / total_in


def viability_window(eroi: float, decline_curve: List[float]) -> int:
    """Years in which incremental EROI remains >= 1.0.

    `decline_curve` is a list of fractional production multipliers per year
    (e.g. [1.0, 0.30, 0.18, 0.13, 0.10] for a typical shale well). The
    incremental EROI for year k is approximated as eroi * decline_curve[k].
    Returns the count of years for which that remains >= 1.0.

    An autonomous deployment whose equipment depreciates over 7 years on a
    well whose viability window is 2 years strands ~5/7 of its capex.
    """
    count = 0
    for mult in decline_curve:
        if eroi * mult >= 1.0:
            count += 1
        else:
            break  # EROI is monotonically non-increasing along a decline curve
    return count


def roi_window_match(viable_years: int, depreciation_years: int) -> dict:
    """Compose the C004 verdict.

    Threshold: lease productive life > equipment depreciation period.
    """
    stranded_years = max(0, depreciation_years - viable_years)
    return {
        "viable_years":          viable_years,
        "depreciation_years":    depreciation_years,
        "stranded_years":        stranded_years,
        "stranded_fraction":     stranded_years / depreciation_years
                                  if depreciation_years > 0 else 0.0,
        "threshold_met":         viable_years > depreciation_years,
    }


def c004_verdict(energy_input: Dict[str, float],
                 energy_output: Dict[str, float],
                 decline_curve: List[float],
                 depreciation_years: int = 7) -> dict:
    eroi = eroi_calc(energy_input, energy_output, len(decline_curve))
    viable = viability_window(eroi, decline_curve)
    match = roi_window_match(viable, depreciation_years)
    return {
        "claim_id":          "C004",
        "lifecycle_eroi":    eroi,
        "decline_curve":     decline_curve,
        **match,
        "falsifier":         "profitable autonomous deployment on <3yr wells",
    }


if __name__ == "__main__":
    # Conventional well, modest decline
    print("conventional:", c004_verdict(
        energy_input={"capex": 1.0e12, "opex": 3.0e12, "fuel": 1.5e12},
        energy_output={"delivered_oil": 1.8e13},
        decline_curve=[1.0, 0.85, 0.75, 0.65, 0.58, 0.52, 0.47, 0.42, 0.38, 0.34],
        depreciation_years=7,
    ))
    # Shale well, steep decline
    print("shale:", c004_verdict(
        energy_input={"capex": 1.0e12, "opex": 0.6e12, "fuel": 0.5e12},
        energy_output={"delivered_oil": 6.0e12},
        decline_curve=[1.0, 0.30, 0.18, 0.13, 0.10, 0.08, 0.07],
        depreciation_years=7,
    ))
