"""
aquifer_pressure_head.py  -- CC0, stdlib-only

The MECHANISM module. Turns a seismic event into forced groundwater emergence
('water coming out of the ground'), not rainfall flooding.

Two coupled paths, both MEASURED-grounded (Wang & Manga 2010):

  STATIC poroelastic   coseismic strain -> dp = B * d_sigma_mean -> head rise
  DYNAMIC / energy      seismic energy density e(M,r) -> liquefaction / springs

The SLOW mantle state enters as a threshold modulator (AQ-03): a primed,
pre-overpressured base needs less shaking to erupt.

HONESTY: triggering is LOCAL/regional (near-to-intermediate field). This module
does NOT claim a mantle pulse causes simultaneous global quakes. Cross-continent
synchrony is a separate, skeptical test (SYN-02) handled downstream.
"""

import math
from claim_ledger import Quantity, gate

RHO_W = 1000.0     # kg/m^3
G = 9.81           # m/s^2

# Skempton coefficient for saturated soft sediment (AQ-01)
SKEMPTON_B = 0.7                    # 0.4-0.9
# energy-density thresholds (AQ-02), J/m^3
E_LIQUEFACTION = 0.1               # forced upwelling / sand boils
E_SUSTAINED = 1.0e-2              # sustained spring / artesian discharge
E_WATERLEVEL = 1.0e-3            # measurable water-level change only


def seismic_energy_density(magnitude: float, r_km: float) -> float:
    """
    Wang (2007) seismic energy density at distance r from an Mw event.
      log r = 0.48 M - 0.33 log e - 1.4   (r in km, e in J/m^3)
    solved for e. MEASURED/empirical (AQ-02).
    """
    r = max(1.0, r_km)
    log_e = (0.48 * magnitude - 1.4 - math.log10(r)) / 0.33
    e = 10.0 ** log_e
    return gate(Quantity(e, "J_per_m3_energy_density", 1.0e-6, 1.0e5),
                "energy_density")


def coseismic_volumetric_strain(magnitude: float, r_km: float) -> float:
    """
    Schematic near/intermediate-field static volumetric strain.
    Anchored: ~1e-4 near a great quake, falling ~1/r^2. DERIVED (schematic).
    """
    r = max(1.0, r_km)
    eps0 = 10.0 ** (0.5 * magnitude - 7.0)     # ~1e-3.5 at M7 reference
    eps = eps0 / (r ** 1.5)
    eps = min(1.0e-3, eps)
    return gate(Quantity(eps, "volumetric_strain", 0.0, 1.0e-3),
                "coseismic_strain")


def pore_pressure_change(magnitude: float, r_km: float,
                         bulk_mod_pa: float = 2.0e9,
                         B: float = SKEMPTON_B) -> float:
    """
    Undrained poroelastic pore-pressure change (AQ-01).
      d_sigma_mean ~ K * eps_vol ;  dp = B * d_sigma_mean
    """
    eps = coseismic_volumetric_strain(magnitude, r_km)
    d_sigma = bulk_mod_pa * eps
    dp = B * d_sigma
    return gate(Quantity(dp, "Pa_pore_pressure_change", 0.0, 5.0e6),
                "pore_pressure_change")


def head_change_m(magnitude: float, r_km: float) -> float:
    """Pore-pressure change expressed as hydraulic head (m of water)."""
    dp = pore_pressure_change(magnitude, r_km)
    h = dp / (RHO_W * G)
    return gate(Quantity(h, "m_head", 0.0, 500.0), "head_change")


def emergence_response(magnitude: float, r_km: float,
                       s_base: float = 0.0) -> dict:
    """
    Classify forced groundwater emergence at a site.

    s_base (0..1) from the mantle/crust chain lowers the energy thresholds
    (AQ-03): a primed base erupts at lower shaking.

    Returns class, energy density, head change, and an emergence-flux proxy.
    """
    e = seismic_energy_density(magnitude, r_km)
    # threshold scale: primed base -> thresholds drop up to 50%
    scale = 1.0 - 0.5 * max(0.0, min(1.0, s_base))
    e_liq = E_LIQUEFACTION * scale
    e_sus = E_SUSTAINED * scale
    e_lvl = E_WATERLEVEL * scale

    if e >= e_liq:
        cls, flux = "LIQUEFACTION_UPWELLING", 1.0
    elif e >= e_sus:
        cls, flux = "SUSTAINED_SPRING_ARTESIAN", 0.6
    elif e >= e_lvl:
        cls, flux = "WATER_LEVEL_RISE", 0.25
    else:
        cls, flux = "NONE", 0.0

    return {
        "class": cls,
        "energy_density_J_m3": round(e, 5),
        "head_change_m": round(head_change_m(magnitude, r_km), 4),
        "emergence_flux_0_1": flux,
        "thresholds_scaled_by": round(scale, 3),
    }


def liquefaction_limit_km(magnitude: float, s_base: float = 0.0) -> float:
    """
    Max distance at which forced upwelling is plausible (e = E_LIQUEFACTION*scale).
    Invert Wang relation for r.
    """
    scale = 1.0 - 0.5 * max(0.0, min(1.0, s_base))
    e = E_LIQUEFACTION * scale
    log_r = 0.48 * magnitude - 1.4 - 0.33 * math.log10(e)
    r = 10.0 ** log_r
    return gate(Quantity(r, "km", 0.0, 5000.0), "liquefaction_limit")


if __name__ == "__main__":
    print("Wang energy density (dry base, s_base=0):")
    for M, r in ((7.0, 10), (7.0, 100), (8.5, 300), (9.0, 800)):
        print(f"  M{M} @ {r:4d} km -> {emergence_response(M, r)}")
    print("\nSame sites over a PRIMED base (s_base=1.0):")
    for M, r in ((7.0, 100), (8.5, 300), (9.0, 800)):
        print(f"  M{M} @ {r:4d} km -> {emergence_response(M, r, s_base=1.0)}")
    print("\nLiquefaction limit distance:")
    for M in (6.5, 7.5, 8.5, 9.2):
        print(f"  M{M}: dry={liquefaction_limit_km(M):.0f} km  "
              f"primed={liquefaction_limit_km(M, 1.0):.0f} km")
