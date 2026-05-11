"""
eroi_real_time_audit.py

Recalculates Energy Return on Investment for an oil play using
current-period input prices and supply-availability flags, rather
than the frozen assumptions baked into most published EROI studies.

Default inputs are placeholder 2026 estimates. The module is
designed to be updated periodically with real spot data, contract
rates, and current supply-chain constraints. Every assumption is
exposed and overrideable.

The point is not to publish authoritative numbers. The point is to
provide a falsifiable, updateable harness so anyone running an EROI
claim can be asked: which version of these inputs did you use?

CC0. Standard library only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# -----------------------------------------------------------------
# CURRENT-PERIOD PRICE VECTOR
# -----------------------------------------------------------------

@dataclass
class PriceVector:
    """
    All prices are nominal current-period (May 2026 placeholder).
    Each comes with a source field that should be a citation. Real
    deployment would pull from spot markets, contract data, and
    insurance industry reports.
    """
    label: str
    as_of: str

    # Energy commodity prices
    wti_oil_usd_per_bbl: float = 78.0
    brent_oil_usd_per_bbl: float = 82.0
    natgas_usd_per_mmbtu: float = 4.2
    electricity_usd_per_kwh_industrial: float = 0.085

    # Transport
    shipping_rate_usd_per_bbl_normal: float = 2.5
    shipping_rate_usd_per_bbl_current: float = 5.8
    # Current reflects Hormuz/Red Sea rerouting around Cape.

    # Materials and equipment
    steel_usd_per_tonne: float = 1100.0
    frac_sand_usd_per_tonne: float = 65.0
    rig_day_rate_usd: float = 28000.0
    rare_earth_cost_index: float = 1.45
    # 1.0 = 2020 baseline. 1.45 reflects China export restrictions
    # and demand surge.

    # Labor
    skilled_field_wage_usd_per_hour: float = 52.0
    skilled_labor_shortage_premium_pct: float = 25.0
    # Percentage uplift over published-study labor rate.

    # Financial
    project_finance_rate_pct: float = 9.5
    # Current corporate borrowing for unconventional oil projects.
    insurance_premium_uplift_pct: float = 42.0
    # Increase over 2020 baseline after refinery incident wave.

    # Compliance and regulation
    carbon_compliance_usd_per_bbl: float = 4.5
    methane_capture_capex_uplift_pct: float = 8.0

    # Tariffs
    equipment_tariff_pct: float = 18.0
    # Average uplift on imported drilling and processing equipment.

    notes: str = ""


# Default current-period placeholder. Update fields with real data.
CURRENT_2026 = PriceVector(
    label="Placeholder May 2026 conditions",
    as_of="2026-05",
    notes=(
        "Numbers are placeholder estimates calibrated to public "
        "reporting on the Hormuz disruption, refinery cascade wave, "
        "labor shortage, and rare earth supply constraints. Replace "
        "with sourced spot data before publishing any conclusions."
    ),
)


# Historical baseline used in most cited EROI studies.
PUBLISHED_BASELINE_2020 = PriceVector(
    label="2018-2020 baseline (cited EROI study era)",
    as_of="2018-2020",
    wti_oil_usd_per_bbl=55.0,
    brent_oil_usd_per_bbl=60.0,
    natgas_usd_per_mmbtu=2.6,
    electricity_usd_per_kwh_industrial=0.065,
    shipping_rate_usd_per_bbl_normal=2.5,
    shipping_rate_usd_per_bbl_current=2.7,
    steel_usd_per_tonne=720.0,
    frac_sand_usd_per_tonne=42.0,
    rig_day_rate_usd=19500.0,
    rare_earth_cost_index=1.0,
    skilled_field_wage_usd_per_hour=38.0,
    skilled_labor_shortage_premium_pct=0.0,
    project_finance_rate_pct=5.5,
    insurance_premium_uplift_pct=0.0,
    carbon_compliance_usd_per_bbl=1.2,
    methane_capture_capex_uplift_pct=2.0,
    equipment_tariff_pct=0.0,
    notes=(
        "Approximate baseline reflecting conditions when most "
        "currently-cited shale EROI studies were calibrated."
    ),
)


# -----------------------------------------------------------------
# SUPPLY AVAILABILITY FLAGS
# -----------------------------------------------------------------

@dataclass
class SupplyConstraint:
    item: str
    available: bool
    lead_time_weeks: int
    sourcing_risk: str   # low / moderate / high / critical
    notes: str = ""


CURRENT_SUPPLY_FLAGS_2026: List[SupplyConstraint] = [

    SupplyConstraint(
        item="High-grade frac sand",
        available=True,
        lead_time_weeks=2,
        sourcing_risk="moderate",
        notes="Domestic supply adequate. Transport logistics strained.",
    ),

    SupplyConstraint(
        item="Specialty drilling steel (high-pressure)",
        available=True,
        lead_time_weeks=12,
        sourcing_risk="high",
        notes=(
            "Tariff-affected. Domestic mills running near capacity. "
            "Replacement timeline doubled."
        ),
    ),

    SupplyConstraint(
        item="Rare earth permanent magnets (motors, sensors)",
        available=False,
        lead_time_weeks=24,
        sourcing_risk="critical",
        notes=(
            "China export restrictions tightening. Western refining "
            "capacity insufficient. Some grades unavailable at any "
            "price."
        ),
    ),

    SupplyConstraint(
        item="Industrial-grade semiconductors (control systems)",
        available=True,
        lead_time_weeks=18,
        sourcing_risk="high",
        notes=(
            "Fab capacity allocated. Replacement parts for legacy "
            "control systems particularly constrained."
        ),
    ),

    SupplyConstraint(
        item="Refinery catalyst (FCC, hydrotreating)",
        available=True,
        lead_time_weeks=8,
        sourcing_risk="moderate",
        notes=(
            "Some specialty catalysts back-ordered. Increased "
            "regeneration cycles compensating short-term."
        ),
    ),

    SupplyConstraint(
        item="Skilled welders and pipefitters (Class 1)",
        available=False,
        lead_time_weeks=999,
        sourcing_risk="critical",
        notes=(
            "Net shortage; cannot be ordered. Wage inflation 25 pct "
            "and rising. Veteran workforce retiring faster than "
            "replacement."
        ),
    ),

    SupplyConstraint(
        item="Replacement pipeline sections (large diameter)",
        available=True,
        lead_time_weeks=16,
        sourcing_risk="high",
        notes="Tariff and mill capacity constraints.",
    ),

    SupplyConstraint(
        item="Drilling rigs (high-spec horizontal)",
        available=True,
        lead_time_weeks=8,
        sourcing_risk="moderate",
        notes=(
            "Day rates up 45 pct vs 2020 baseline. Crew availability "
            "the real constraint."
        ),
    ),

]


# -----------------------------------------------------------------
# COST RECALCULATION
# -----------------------------------------------------------------

@dataclass
class EROIStudyReference:
    """
    A published EROI study to be re-audited against current inputs.
    """
    citation: str
    publication_year: int
    play: str
    published_eroi: float
    capex_basis_usd: float
    labor_share_of_cost_pct: float
    materials_share_of_cost_pct: float
    transport_share_of_cost_pct: float
    finance_share_of_cost_pct: float
    other_share_of_cost_pct: float
    assumed_well_lifespan_years: float


def cost_inflation_factor(
    baseline: PriceVector,
    current: PriceVector,
) -> Dict[str, float]:
    """
    Component-by-component inflation factors. 1.00 = unchanged.
    """
    def ratio(now, then):
        return now / then if then > 0 else float("inf")

    return {
        "steel": ratio(current.steel_usd_per_tonne,
                       baseline.steel_usd_per_tonne),
        "frac_sand": ratio(current.frac_sand_usd_per_tonne,
                           baseline.frac_sand_usd_per_tonne),
        "rig_day_rate": ratio(current.rig_day_rate_usd,
                              baseline.rig_day_rate_usd),
        "rare_earth": ratio(current.rare_earth_cost_index,
                            baseline.rare_earth_cost_index),
        "labor": ratio(
            current.skilled_field_wage_usd_per_hour
            * (1.0 + current.skilled_labor_shortage_premium_pct / 100.0),
            baseline.skilled_field_wage_usd_per_hour
            * (1.0 + baseline.skilled_labor_shortage_premium_pct / 100.0),
        ),
        "shipping": ratio(current.shipping_rate_usd_per_bbl_current,
                          baseline.shipping_rate_usd_per_bbl_current),
        "finance": ratio(current.project_finance_rate_pct,
                         baseline.project_finance_rate_pct),
        "insurance_uplift": (
            (100.0 + current.insurance_premium_uplift_pct)
            / (100.0 + baseline.insurance_premium_uplift_pct)
        ),
        "carbon_compliance": ratio(
            current.carbon_compliance_usd_per_bbl,
            baseline.carbon_compliance_usd_per_bbl,
        ),
        "equipment_tariff": (
            (100.0 + current.equipment_tariff_pct)
            / (100.0 + baseline.equipment_tariff_pct)
        ),
    }


def weighted_inflation(
    study: EROIStudyReference,
    inflation: Dict[str, float],
) -> float:
    """
    Apply component inflation factors weighted by their share of
    the study's original cost structure.
    """
    # Map cost categories to component inflation factors.
    labor_inflation = inflation["labor"]
    materials_inflation = (
        0.45 * inflation["steel"]
        + 0.25 * inflation["frac_sand"]
        + 0.15 * inflation["rare_earth"]
        + 0.15 * inflation["equipment_tariff"]
    )
    transport_inflation = inflation["shipping"]
    finance_inflation = (
        0.6 * inflation["finance"] + 0.4 * inflation["insurance_uplift"]
    )
    other_inflation = inflation["carbon_compliance"]

    total = (
        study.labor_share_of_cost_pct / 100.0 * labor_inflation
        + study.materials_share_of_cost_pct / 100.0 * materials_inflation
        + study.transport_share_of_cost_pct / 100.0 * transport_inflation
        + study.finance_share_of_cost_pct / 100.0 * finance_inflation
        + study.other_share_of_cost_pct / 100.0 * other_inflation
    )
    return total


def recalculate_eroi(
    study: EROIStudyReference,
    baseline: PriceVector,
    current: PriceVector,
) -> Dict[str, float]:
    """
    Take a published EROI and adjust it for current-period cost
    inflation. EROI new = EROI published / inflation factor.

    This is a first-order approximation. It assumes energy output
    is unchanged and only input costs have inflated, mapped through
    energy intensity.
    """
    inflation = cost_inflation_factor(baseline, current)
    weighted = weighted_inflation(study, inflation)

    eroi_adjusted = study.published_eroi / weighted

    return {
        "study": study.citation,
        "play": study.play,
        "published_eroi": study.published_eroi,
        "inflation_factor": weighted,
        "eroi_adjusted_current_period": eroi_adjusted,
        "component_inflation": inflation,
    }


# -----------------------------------------------------------------
# EXAMPLE STUDIES
# -----------------------------------------------------------------

EXAMPLE_STUDIES: List[EROIStudyReference] = [

    EROIStudyReference(
        citation="Hall et al. 2014 (US conventional, mature)",
        publication_year=2014,
        play="US conventional, mature",
        published_eroi=11.0,
        capex_basis_usd=8_000_000.0,
        labor_share_of_cost_pct=22.0,
        materials_share_of_cost_pct=38.0,
        transport_share_of_cost_pct=12.0,
        finance_share_of_cost_pct=18.0,
        other_share_of_cost_pct=10.0,
        assumed_well_lifespan_years=20.0,
    ),

    EROIStudyReference(
        citation="Brandt et al. 2015 (Bakken / Eagle Ford composite)",
        publication_year=2015,
        play="Unconventional shale composite",
        published_eroi=6.5,
        capex_basis_usd=8_500_000.0,
        labor_share_of_cost_pct=20.0,
        materials_share_of_cost_pct=42.0,
        transport_share_of_cost_pct=10.0,
        finance_share_of_cost_pct=20.0,
        other_share_of_cost_pct=8.0,
        assumed_well_lifespan_years=15.0,
    ),

    EROIStudyReference(
        citation="Murphy et al. 2018 (Permian, peak era)",
        publication_year=2018,
        play="Permian Basin",
        published_eroi=8.0,
        capex_basis_usd=10_000_000.0,
        labor_share_of_cost_pct=18.0,
        materials_share_of_cost_pct=44.0,
        transport_share_of_cost_pct=11.0,
        finance_share_of_cost_pct=19.0,
        other_share_of_cost_pct=8.0,
        assumed_well_lifespan_years=20.0,
    ),

]


# -----------------------------------------------------------------
# TEMPORAL DECAY FLAGGING
# -----------------------------------------------------------------

def temporal_decay_flag(
    study: EROIStudyReference,
    current_year: int = 2026,
) -> str:
    age = current_year - study.publication_year
    if age <= 2:
        return "current"
    elif age <= 4:
        return "aging - verify inputs"
    elif age <= 8:
        return "stale - major regime shifts since publication"
    else:
        return "obsolete - structurally different operating environment"


# -----------------------------------------------------------------
# REPORT
# -----------------------------------------------------------------

def report():
    print("=" * 74)
    print("EROI REAL-TIME AUDIT")
    print("=" * 74)
    print()
    print(f"  Baseline:  {PUBLISHED_BASELINE_2020.label}")
    print(f"  Current:   {CURRENT_2026.label}")
    print()
    print(f"  Note: {CURRENT_2026.notes}")
    print()

    print("=" * 74)
    print("COMPONENT INFLATION FACTORS  (baseline -> current)")
    print("=" * 74)
    inflation = cost_inflation_factor(
        PUBLISHED_BASELINE_2020, CURRENT_2026
    )
    for k, v in inflation.items():
        print(f"  {k:25s}  x {v:6.2f}")
    print()

    print("=" * 74)
    print("SUPPLY AVAILABILITY FLAGS")
    print("=" * 74)
    for sc in CURRENT_SUPPLY_FLAGS_2026:
        avail = "yes" if sc.available else "NO"
        lead = (
            f"{sc.lead_time_weeks} wk"
            if sc.lead_time_weeks < 999
            else "n/a"
        )
        print(f"  {sc.item}")
        print(f"    available: {avail}   lead: {lead}   "
              f"risk: {sc.sourcing_risk}")
        if sc.notes:
            print(f"    notes: {sc.notes}")
        print()

    print("=" * 74)
    print("EROI RECALCULATION  (published studies -> current period)")
    print("=" * 74)

    for study in EXAMPLE_STUDIES:
        result = recalculate_eroi(
            study, PUBLISHED_BASELINE_2020, CURRENT_2026
        )
        decay = temporal_decay_flag(study)

        print("-" * 74)
        print(f"STUDY:   {study.citation}")
        print(f"PLAY:    {study.play}")
        print(f"PUBLISHED EROI:           "
              f"{study.published_eroi:6.2f} : 1")
        print(f"INFLATION FACTOR:         "
              f"x {result['inflation_factor']:5.2f}")
        print(f"ADJUSTED (current period):"
              f"{result['eroi_adjusted_current_period']:6.2f} : 1")
        print(f"TEMPORAL DECAY:           {decay}")
        print()


if __name__ == "__main__":
    report()
