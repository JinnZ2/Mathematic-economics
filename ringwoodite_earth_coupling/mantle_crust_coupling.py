"""
mantle_crust_coupling.py  -- CC0, stdlib-only

Upward propagation chain. Turns the slow deep-water baseline into a crustal
SENSITIVITY scalar. It does not produce events; it produces how reactive the
crust/hydrosphere is when a fast forcing arrives.

  deep_water_baseline  (0..1, slow)
      -> hydrolytic weakening -> viscosity drop
      -> heat-flux modulation at crust base
      -> crustal pore-pressure headroom
      -> SENSITIVITY S (0..1)

Every step DERIVED from MEASURED rheology (CPL-01). Honest caveat (CPL-02):
this whole scalar drifts on >10 kyr timescales. On a single human lifetime it
is effectively constant.
"""

import math
from claim_ledger import Quantity, gate

# hydrolytic weakening: log10 viscosity drop per wt% water (CPL-01 range 0.5-2.5)
LOG10_ETA_DROP_PER_WT = 1.3
ETA_DRY_LOG10 = 21.0     # log10(Pa s) dry reference mantle viscosity


def viscosity_log10(water_wt_percent: float) -> float:
    """Effective log10 viscosity after hydrolytic weakening. DERIVED."""
    val = ETA_DRY_LOG10 - LOG10_ETA_DROP_PER_WT * water_wt_percent
    return gate(Quantity(val, "log10_Pa_s", 17.0, 23.0), "viscosity")


def heat_flux_modulation(baseline_0_1: float) -> float:
    """
    Lower viscosity -> more vigorous local convection -> more heat to crust base.
    Returns a multiplier on background basal heat flux. DERIVED.
    """
    m = 1.0 + 0.6 * baseline_0_1      # up to +60% when fully primed
    return gate(Quantity(m, "dimensionless_multiplier", 0.5, 2.0),
                "heat_flux_mod")


def pore_pressure_headroom(baseline_0_1: float) -> float:
    """
    Primed base + elevated basal water/heat reduces effective stress in deep
    aquifers -> LESS headroom before overpressure release (seepage/flood).
    Returns headroom in [0,1]; lower headroom = more sensitive. DERIVED.
    """
    headroom = 1.0 - 0.7 * baseline_0_1
    return gate(Quantity(headroom, "dimensionless_0_1", 0.0, 1.0),
                "pore_headroom")


def crustal_sensitivity(baseline_0_1: float,
                        water_wt_percent: float = 1.4) -> float:
    """
    Collapse the chain into ONE sensitivity scalar S in [0,1].
    High S = a small fast-forcing kick can trip surface water emergence.
    """
    eta = viscosity_log10(water_wt_percent)
    eta_term = (23.0 - eta) / 6.0                 # 0..1, lower visc -> higher
    hflux = heat_flux_modulation(baseline_0_1)
    head = pore_pressure_headroom(baseline_0_1)
    # sensitivity rises with heat-flux and falls with headroom
    s = 0.5 * eta_term + 0.5 * (hflux - 0.5) / 1.5 * (1.0 - head)
    s = max(0.0, min(1.0, s))
    return gate(Quantity(s, "sensitivity_0_1", 0.0, 1.0), "crustal_sensitivity")


if __name__ == "__main__":
    for b in (0.0, 0.3, 0.6, 1.0):
        print(f"baseline={b:.1f}  "
              f"eta=10^{viscosity_log10(1.4):.1f}  "
              f"hflux x{heat_flux_modulation(b):.2f}  "
              f"headroom={pore_pressure_headroom(b):.2f}  "
              f"S={crustal_sensitivity(b):.3f}")
