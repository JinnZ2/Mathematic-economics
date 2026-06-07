"""
ringwoodite_phase.py  -- CC0, stdlib-only

Mineral-physics layer: ringwoodite (gamma-(Mg,Fe)2SiO4) water storage and
the dehydration flux when hydrous transition-zone material crosses the 660 km
boundary into the lower mantle.

This layer is MEASURED/DERIVED. It sets the slow boundary condition only.
It deliberately produces a quantity per UNIT TIME, integrated by the coupler,
because rates are physical and stocks-pretending-to-be-rates are how models lie.

Depth/pressure anchors (PREM-ish):
  410 km  ~ 13.5 GPa   (olivine -> wadsleyite)
  525 km  ~ 17.9 GPa   (wadsleyite -> ringwoodite)
  660 km  ~ 23.4 GPa   (ringwoodite -> bridgmanite + ferropericlase)
"""

import math
from claim_ledger import Quantity, gate

# ---- anchors -----------------------------------------------------------
P_410_GPA = 13.5
P_525_GPA = 17.9
P_660_GPA = 23.4
RHO_TZ = 3700.0          # kg/m^3, transition-zone density (approx)
G = 9.82                 # m/s^2

# 660 Clapeyron slope (negative): boundary deepens as T drops.
CLAPEYRON_660_MPA_PER_K = -2.0     # MPa/K  (RW-supported range -3..-0.5)
T_REF_660_K = 1900.0               # reference TZ temperature at 660


def depth_to_pressure_gpa(depth_km: float) -> float:
    """Lithostatic estimate. DERIVED."""
    P_pa = RHO_TZ * G * (depth_km * 1000.0)
    return gate(Quantity(P_pa / 1e9, "GPa", 0.0, 30.0), "pressure")


def water_capacity_wt_percent(temperature_k: float) -> float:
    """
    Max structural water in ringwoodite as a function of temperature.
    Decreasing with T; bounded to the MEASURED 0-3 wt% window (RW-01).
    Simple monotonic form calibrated to the hot/cold ends of the field.
    """
    t = temperature_k
    # 3.0 wt% near 1300 K, ~0.5 wt% near 2100 K, clamp to range.
    c = 3.0 - (t - 1300.0) * (2.5 / 800.0)
    c = max(0.0, min(3.0, c))
    return gate(Quantity(c, "wt_percent_H2O", 0.0, 3.0), "water_capacity")


def boundary_660_depth_km(temperature_k: float) -> float:
    """
    Thermally perturbed 660 depth via Clapeyron slope.
    Colder slab -> deeper boundary (negative slope). DERIVED.
    """
    dT = temperature_k - T_REF_660_K
    dP_mpa = CLAPEYRON_660_MPA_PER_K * dT          # MPa
    # convert pressure shift to depth shift: dz = dP / (rho g)
    dz_m = (dP_mpa * 1e6) / (RHO_TZ * G)
    depth = 660.0 + dz_m / 1000.0
    return gate(Quantity(depth, "km", 600.0, 720.0), "boundary_660")


def dehydration_flux(downwelling_m_per_yr: float,
                     temperature_k: float,
                     rw_water_wt: float,
                     lm_water_wt: float = 0.1) -> float:
    """
    Water shed at the 660 as hydrous ringwoodite converts to the drier
    lower-mantle assemblage.  RW-02.

      flux [kg_H2O / m^2 / yr]
        = rho * v_down * (C_rw - C_lm)

    C_* are mass fractions (kg H2O / kg rock).  Negative contrast -> 0.
    `temperature_k` enters by capping rw_water at capacity(T).
    """
    cap = water_capacity_wt_percent(temperature_k) / 100.0
    c_rw = min(rw_water_wt / 100.0, cap)
    c_lm = lm_water_wt / 100.0
    contrast = max(0.0, c_rw - c_lm)
    v = downwelling_m_per_yr
    flux = RHO_TZ * v * contrast      # kg/m^2/yr
    return gate(Quantity(flux, "kg_H2O_per_m2_per_yr", 0.0, 50.0),
                "dehydration_flux")


def deep_water_baseline(temperature_k: float,
                        downwelling_m_per_yr: float,
                        rw_water_wt: float) -> float:
    """
    Collapse the mineral-physics state into ONE slow scalar in [0,1] that the
    coupler reads as 'how primed is the deep base'.  Normalized against a
    plausible max flux (~10 kg/m^2/yr regional).  DERIVED, slow (CPL-02).
    """
    flux = dehydration_flux(downwelling_m_per_yr, temperature_k, rw_water_wt)
    primed = min(1.0, flux / 10.0)
    return gate(Quantity(primed, "dimensionless_0_1", 0.0, 1.0),
                "deep_water_baseline")


if __name__ == "__main__":
    T = 1850.0
    print("P(660 km)        =", round(depth_to_pressure_gpa(660), 2), "GPa")
    print("water capacity   =", round(water_capacity_wt_percent(T), 3), "wt%")
    print("660 depth (cold) =", round(boundary_660_depth_km(1600.0), 1), "km")
    print("660 depth (hot)  =", round(boundary_660_depth_km(2100.0), 1), "km")
    print("dehydration flux =",
          round(dehydration_flux(0.01, T, rw_water_wt=1.4), 4),
          "kg/m2/yr")
    print("deep baseline    =",
          round(deep_water_baseline(T, 0.01, 1.4), 4))
