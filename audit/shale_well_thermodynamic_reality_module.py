"""
shale_well_thermodynamic_reality_module.py

Recalculates EROI for unconventional shale wells using realistic
decline curves and actual economic productive lifespan.

Core metrology failure exposed:
Published EROI amortizes capex over 20-year project lifespan.
Actual Bakken / Eagle Ford / Permian wells follow steeper decline.
Economic cutoff hits around year 5-8. Wells are abandoned with
much of original oil-in-place still in the formation.

This module uses representative decline curves and adds the
capital-system overhead that published EROI omits. Results are
order-of-magnitude, not precise. The point is to show direction
of error, not to publish authoritative figures.

CC0. Standard library only.

See also (substrate-aware-accounting corpus):
  - substrate_damage_audit.py - population-level institutional damage
  - oil_extraction_thermodynamic_cascade_audit.py - ten cost vectors omitted from EROI
  - refinery_stress_cascade_module.py - 2025-2026 refinery incident data; cascade-failure cost vectors
  - shale_well_thermodynamic_reality_module.py - Arps decline curves; per-well EROI recalculation  (this module)
  - eroi_real_time_audit.py - re-run published EROI against current-period prices and supply flags
  - banking_thermodynamic_audit.py - capital-layer overhead; growth-constraint check
  - energy_cascade_audit.py - May 2026 cross-layer cascade detection (price, EROI, refining, demand, trust)
Corpus index: substrate_accounting/README.md  |  claims: substrate_accounting/CLAIMS_UNIFIED.json
"""

from dataclasses import dataclass
from typing import Dict, List
import math


# -----------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------

# Energy per barrel of crude (HHV).
BBL_ENERGY_KJ = 6_117_863.0   # ~5.8 MMBTU / bbl

# Embedded energy in unconventional well construction and operation
# over productive lifespan: steel casing, drilling fuel, frac fluid
# (water, sand, chemicals), sand transport, water hauling, artificial
# lift electricity, ongoing maintenance.
# Industry studies put it at 400 to 700 billion BTU equivalent over
# the well lifecycle. Using mid value.
WELL_LIFECYCLE_ENERGY_KJ = 5.5e11    # ~520 billion BTU


# -----------------------------------------------------------------
# DECLINE CURVE
# -----------------------------------------------------------------

def arps_hyperbolic_monthly_rates(
    q_initial_bpd: float,
    decline_initial_annual: float,
    b: float,
    months: int,
) -> List[float]:
    """
    Arps hyperbolic decline. Converted to monthly time step.
    Decline_initial is the nominal first-year decline (annual basis).
    """
    rates = []
    decline_monthly = decline_initial_annual / 12.0
    for t in range(months):
        denom = (1.0 + b * decline_monthly * t) ** (1.0 / b)
        rates.append(q_initial_bpd / denom)
    return rates


# -----------------------------------------------------------------
# WELL ARCHETYPES
# -----------------------------------------------------------------

@dataclass
class WellArchetype:
    play: str
    initial_production_bpd: float
    decline_initial_annual: float
    b_factor: float
    economic_cutoff_bpd: float
    capex_usd: float


# Decline parameters tuned to published 2024-2026 well behavior.
# Modern shale wells lose 60-75 percent of initial rate in year 1.
ARCHETYPES = [

    WellArchetype(
        play="Bakken (typical 2024-2026)",
        initial_production_bpd=750.0,
        decline_initial_annual=2.4,   # steep first-year decline
        b_factor=0.9,
        economic_cutoff_bpd=40.0,
        capex_usd=9_500_000.0,
    ),

    WellArchetype(
        play="Eagle Ford (post-peak)",
        initial_production_bpd=550.0,
        decline_initial_annual=2.2,
        b_factor=1.0,
        economic_cutoff_bpd=35.0,
        capex_usd=7_500_000.0,
    ),

    WellArchetype(
        play="Permian Midland (core)",
        initial_production_bpd=1100.0,
        decline_initial_annual=2.5,
        b_factor=0.85,
        economic_cutoff_bpd=45.0,
        capex_usd=11_000_000.0,
    ),

    WellArchetype(
        play="Permian Delaware (tier 2)",
        initial_production_bpd=850.0,
        decline_initial_annual=2.3,
        b_factor=0.95,
        economic_cutoff_bpd=45.0,
        capex_usd=10_500_000.0,
    ),

]


# -----------------------------------------------------------------
# LIFESPAN
# -----------------------------------------------------------------

@dataclass
class WellLifespanResult:
    play: str
    economic_lifespan_months: int
    cumulative_production_bbl: float
    capex_per_recovered_bbl_usd: float


def simulate_well_lifespan(
    arch: WellArchetype,
    horizon_months: int = 240,
) -> WellLifespanResult:

    rates = arps_hyperbolic_monthly_rates(
        arch.initial_production_bpd,
        arch.decline_initial_annual,
        arch.b_factor,
        horizon_months,
    )

    days_per_month = 30.4
    cumulative = 0.0
    economic_months = 0

    for t, rate in enumerate(rates):
        if rate < arch.economic_cutoff_bpd:
            economic_months = t
            break
        cumulative += rate * days_per_month

    if economic_months == 0:
        economic_months = horizon_months

    capex_per_bbl = (
        arch.capex_usd / cumulative if cumulative > 0 else float("inf")
    )

    return WellLifespanResult(
        play=arch.play,
        economic_lifespan_months=economic_months,
        cumulative_production_bbl=cumulative,
        capex_per_recovered_bbl_usd=capex_per_bbl,
    )


# -----------------------------------------------------------------
# CAPITAL LAYER OVERHEAD
# -----------------------------------------------------------------

@dataclass
class CapitalOverheadEstimate:
    """
    Order-of-magnitude estimate of energy cost embedded in capital
    movement. Banking system runs on data centers, real estate,
    employee energy, compliance infrastructure, currency creation
    overhead. Standard EROI assumes this is zero. It is not.
    """
    energy_kj_per_dollar_per_year: float = 1.8
    compliance_multiplier: float = 1.3
    hedging_multiplier: float = 1.15


def capital_layer_energy_cost(
    capex_usd: float,
    productive_years: float,
    overhead: CapitalOverheadEstimate,
) -> float:
    annual_kj = (
        capex_usd
        * overhead.energy_kj_per_dollar_per_year
        * overhead.compliance_multiplier
        * overhead.hedging_multiplier
    )
    return annual_kj * productive_years


# -----------------------------------------------------------------
# EROI CALCULATIONS
# -----------------------------------------------------------------

@dataclass
class EROIResult:
    play: str
    productive_years: float
    cumulative_bbl: float
    gross_energy_kj: float
    construction_energy_kj: float
    capital_layer_kj: float
    eroi_construction_only: float
    eroi_with_capital_layer: float
    capital_layer_share_pct: float


def recalculate_eroi(arch: WellArchetype) -> EROIResult:

    lifespan = simulate_well_lifespan(arch)
    productive_years = lifespan.economic_lifespan_months / 12.0
    gross_kj = lifespan.cumulative_production_bbl * BBL_ENERGY_KJ

    construction_kj = WELL_LIFECYCLE_ENERGY_KJ
    capital_kj = capital_layer_energy_cost(
        arch.capex_usd,
        productive_years,
        CapitalOverheadEstimate(),
    )

    eroi_construction = gross_kj / construction_kj
    eroi_full = gross_kj / (construction_kj + capital_kj)
    capital_share = (
        100.0 * capital_kj / (construction_kj + capital_kj)
    )

    return EROIResult(
        play=arch.play,
        productive_years=productive_years,
        cumulative_bbl=lifespan.cumulative_production_bbl,
        gross_energy_kj=gross_kj,
        construction_energy_kj=construction_kj,
        capital_layer_kj=capital_kj,
        eroi_construction_only=eroi_construction,
        eroi_with_capital_layer=eroi_full,
        capital_layer_share_pct=capital_share,
    )


# -----------------------------------------------------------------
# REPLACEMENT TREADMILL
# -----------------------------------------------------------------

def replacement_treadmill(
    arch: WellArchetype,
    years: int = 20,
) -> Dict[str, float]:

    lifespan = simulate_well_lifespan(arch)
    productive_years = lifespan.economic_lifespan_months / 12.0
    wells_needed = max(1, math.ceil(years / productive_years))

    total_capex = arch.capex_usd * wells_needed
    total_construction_kj = WELL_LIFECYCLE_ENERGY_KJ * wells_needed
    total_capital_kj = capital_layer_energy_cost(
        total_capex, years, CapitalOverheadEstimate(),
    )

    total_bbl = lifespan.cumulative_production_bbl * wells_needed
    gross_kj = total_bbl * BBL_ENERGY_KJ
    total_input_kj = total_construction_kj + total_capital_kj

    return {
        "play": arch.play,
        "productive_years_per_well": productive_years,
        "wells_needed": wells_needed,
        "total_capex_usd": total_capex,
        "total_production_bbl": total_bbl,
        "treadmill_eroi": gross_kj / total_input_kj,
    }


# -----------------------------------------------------------------
# REPORT
# -----------------------------------------------------------------

def report():
    print("=" * 74)
    print("SHALE WELL THERMODYNAMIC REALITY MODULE")
    print("=" * 74)
    print()
    print("  Decline curves: Arps hyperbolic, 2024-2026 representative.")
    print("  Energy per barrel: 5.8 MMBTU (HHV).")
    print("  Well lifecycle embedded energy: ~520 billion BTU.")
    print("  Capital layer: order-of-magnitude estimate.")
    print()

    print("=" * 74)
    print("PER-WELL LIFESPAN AND EROI")
    print("=" * 74)

    for arch in ARCHETYPES:
        lifespan = simulate_well_lifespan(arch)
        eroi = recalculate_eroi(arch)

        print("-" * 74)
        print(f"PLAY: {arch.play}")
        print(f"  Initial production:       "
              f"{arch.initial_production_bpd:7.0f} bbl/day")
        print(f"  Economic cutoff:          "
              f"{arch.economic_cutoff_bpd:7.0f} bbl/day")
        print(f"  Capex:                    "
              f"${arch.capex_usd:>12,.0f}")
        print()
        print(f"  Economic lifespan:        "
              f"{eroi.productive_years:6.1f} years")
        print(f"  Cumulative production:    "
              f"{lifespan.cumulative_production_bbl:>12,.0f} bbl")
        print(f"  Capex per bbl:            "
              f"${lifespan.capex_per_recovered_bbl_usd:>9,.2f}")
        print()
        print(f"  EROI construction only:   "
              f"{eroi.eroi_construction_only:6.2f} : 1")
        print(f"  EROI with capital layer:  "
              f"{eroi.eroi_with_capital_layer:6.2f} : 1")
        print(f"  Capital share of inputs:  "
              f"{eroi.capital_layer_share_pct:6.2f} %")
        print()

    print("=" * 74)
    print("REPLACEMENT TREADMILL (20-year production maintenance)")
    print("=" * 74)
    print()

    for arch in ARCHETYPES:
        td = replacement_treadmill(arch, years=20)
        print("-" * 74)
        print(f"PLAY: {arch.play}")
        print(f"  Productive years per well:    "
              f"{td['productive_years_per_well']:6.1f}")
        print(f"  Wells needed over 20 years:   "
              f"{td['wells_needed']:6.0f}")
        print(f"  Total capex over horizon:     "
              f"${td['total_capex_usd']:>14,.0f}")
        print(f"  Total production:             "
              f"{td['total_production_bbl']:>12,.0f} bbl")
        print(f"  Treadmill EROI:               "
              f"{td['treadmill_eroi']:6.2f} : 1")
        print()


if __name__ == "__main__":
    report()
