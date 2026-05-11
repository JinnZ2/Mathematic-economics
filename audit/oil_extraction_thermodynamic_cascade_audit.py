"""
oil_extraction_thermodynamic_cascade_audit.py

Audit module exposing the metrology failures in current oil-extraction
EROI accounting. Standard EROI calculations treat the extraction system
as if it operates in isolation under stable supply chains, stable
geopolitics, and stable workforce. None of those assumptions hold in
the present operating environment.

This module re-runs the EROI accounting with the suppressed cost vectors
included. It does not claim final numbers - it claims that the published
numbers are non-falsifiable until the suppressed vectors are accounted
for, and provides scoring dimensions and a scope-audit gate to flag
any EROI claim that omits them.

Core claim: published oil EROI figures (6:1 to 10:1 for unconventional)
are upper bounds under stable-supply assumptions. Under current operating
conditions, system-level EROI is substantially lower and approaching
the 1:1 threshold faster than the literature reports.

CC0. Standard library only.

See also (substrate-aware-accounting corpus):
  - substrate_damage_audit.py - population-level institutional damage
  - oil_extraction_thermodynamic_cascade_audit.py - ten cost vectors omitted from EROI  (this module)
  - refinery_stress_cascade_module.py - 2025-2026 refinery incident data; cascade-failure cost vectors
  - shale_well_thermodynamic_reality_module.py - Arps decline curves; per-well EROI recalculation
  - eroi_real_time_audit.py - re-run published EROI against current-period prices and supply flags
  - banking_thermodynamic_audit.py - capital-layer overhead; growth-constraint check
Corpus index: substrate_accounting/README.md  |  claims: substrate_accounting/CLAIMS_UNIFIED.json
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# -----------------------------------------------------------------
# REFERENCE DATA  (sourced May 2026; see CITATIONS below)
# -----------------------------------------------------------------

REFERENCE_DATA: Dict[str, str] = {

    "us_production_2025":
        "13.6 million b/d (record).",

    "us_production_forecast_2026":
        "13.5 million b/d (EIA STEO, December 2025 - decline begins).",

    "spr_inventory_dec_2025":
        "411 million bbl, ~125 days of net import protection. "
        "Lowest level since 1982 if full announced release completes.",

    "eroi_conventional_historical":
        "100:1 (1950s baseline for conventional fields).",

    "eroi_norwegian_oil_2010":
        "~40:1 (declined from ~60:1 peak in 1996).",

    "eroi_unconventional_shale":
        "~6:1 finished fuel (published, stable-supply assumption).",

    "eroi_oil_shale_in_situ":
        "~1.5:1 finished fuel (already at energy-sink threshold).",

    "eroi_2050_projection":
        "6.7:1 weighted average for all oil liquids (Delannoy et al.).",

    "net_energy_peak_estimate":
        "2025 at ~400 PJ/day (Delannoy et al.) - may already be past.",

    "shale_recovery_rate":
        "~10% of oil in unconventional shale formations typically "
        "recovered (DOE / U. North Dakota).",

    "eagle_ford_peak":
        "1.6 million b/d in September 2015. Now in retreat.",

    "permian_inventory_quality":
        "Top 5 public operators control ~70% of high-quality net "
        "inventory. Private operators hold ~16% of sub-$50 breakeven "
        "inventory. Sub-$50 inventory is the marginal class.",

    "hormuz_disruption":
        "Production shut-ins of 6.7 million b/d in May 2026 under "
        "conflict assumptions (EIA STEO). Insurance premiums elevated. "
        "Rerouting around Cape of Good Hope is becoming the new normal.",

    "shipping_emissions_increase":
        "Up to 70% rise in greenhouse gas emissions for a "
        "Singapore-Rotterdam round trip due to rerouting and speed "
        "increases (UNCTAD).",

    "rare_earth_china_share":
        "China supplied >95% of global REM production historically; "
        "81% as of 2017. REE demand expected to increase >5x by 2030.",

    "ree_recycling_rate":
        "<1% global recycling rate for REEs (UN).",

    "semiconductor_fab_cost":
        "TSMC 2nm fab capex >$45 billion. Fab annual power cost at "
        "3nm: $100-300 million. Single fab energy use comparable to "
        "a city of hundreds of thousands.",

    "semiconductor_water_use":
        "1,500-2,000 gallons per wafer at 3nm.",

    "oil_gas_workforce_shortage":
        "Up to 40,000 competent worker shortfall by 2025 (Accenture); "
        "85 million unfilled skilled jobs globally projected (Korn "
        "Ferry).",

    "workforce_age_mobility":
        "Aging workforce, falling mobility, pay-rise expectations "
        "softening (67% in 2026 vs 71% in 2025) - GETI.",

    "workforce_culling_pattern":
        "Workforce reductions target higher-cost veteran employees "
        "(Deloitte 2025). Skill-base degradation is structural, not "
        "cyclical.",

}


# -----------------------------------------------------------------
# SUPPRESSED COST VECTORS  (vectors typically omitted from EROI accounting)
# -----------------------------------------------------------------

@dataclass
class CostVector:
    id: str
    name: str
    description: str
    why_omitted: str
    direction: str   # "increases denominator" or "shrinks numerator"


SUPPRESSED_VECTORS: List[CostVector] = [

    CostVector(
        id="V1_supply_chain_energy",
        name="Supply-chain embodied energy",
        description=(
            "Energy embedded in rigs, casing, drill pipe, fracking sand "
            "logistics, cement, valves, pumps, sensors, and the steel, "
            "rare earths, and semiconductors inside them. Most of this "
            "energy is spent outside the extraction site and outside "
            "the operator's books."
        ),
        why_omitted=(
            "Treated as an externality; only direct on-site energy "
            "inputs are typically counted."
        ),
        direction="increases denominator",
    ),

    CostVector(
        id="V2_geopolitical_disruption",
        name="Geopolitical chokepoint and insurance premium",
        description=(
            "Strait of Hormuz risk, Red Sea / Suez disruption, Cape of "
            "Good Hope rerouting, war-risk insurance, vessel speed "
            "increases to maintain schedules. UNCTAD estimates up to "
            "70% GHG emissions increase on a Singapore-Rotterdam round "
            "trip. That is added energy per delivered barrel."
        ),
        why_omitted=(
            "EROI is calculated as a steady-state property of the well "
            "and refinery, not of the global delivery system."
        ),
        direction="increases denominator",
    ),

    CostVector(
        id="V3_strategic_reserve_drawdown",
        name="Strategic reserve liquidation as hidden subsidy",
        description=(
            "Drawing SPR to stabilize prices during disruption is a "
            "transfer of future buffer into present consumption. The "
            "energy cost of the refill - under depleted production "
            "conditions, on shrinking unconventional EROI - is not "
            "amortized into the EROI of current barrels delivered."
        ),
        why_omitted=(
            "SPR accounting is treated as policy, not as a thermodynamic "
            "subsidy to the extraction system."
        ),
        direction="shrinks numerator",
    ),

    CostVector(
        id="V4_workforce_skill_decay",
        name="Workforce skill decay and replacement cost",
        description=(
            "Veteran workforce culling, training-budget compression, "
            "aging skill base, falling mobility, declining wage growth. "
            "Each lost veteran requires a multi-year replacement cost. "
            "Loss is non-linear: institutional knowledge does not "
            "convert into manuals at 1:1."
        ),
        why_omitted=(
            "Labor is treated as a wage line, not as accumulated energy "
            "embedded in human capability. Skill decay is not measured."
        ),
        direction="increases denominator",
    ),

    CostVector(
        id="V5_automation_substrate_dependency",
        name="Automation substrate dependency",
        description=(
            "Automating extraction requires semiconductors (multi-billion "
            "fab capex, city-scale energy use, REE inputs), industrial "
            "control systems, communications infrastructure, and "
            "ongoing software maintenance. Automation does not reduce "
            "energy input; it relocates it upstream into the fab and "
            "the mining supply chain."
        ),
        why_omitted=(
            "Automation is sold as a cost reducer; the upstream "
            "manufacturing energy is on someone else's books."
        ),
        direction="increases denominator",
    ),

    CostVector(
        id="V6_rare_earth_extraction_energy",
        name="Rare earth and critical mineral extraction energy",
        description=(
            "Magnets, sensors, electronics, batteries depend on REEs "
            "with very high energy intensity per kg refined. "
            "China-concentrated supply, <1% recycling rate, >5x demand "
            "increase projected by 2030. Every automation, electrification, "
            "and digital-twin layer added to extraction increases REE "
            "load."
        ),
        why_omitted=(
            "Mining and refining energy is attributed to the mineral "
            "industry, not to the downstream oil sector that consumes "
            "the outputs."
        ),
        direction="increases denominator",
    ),

    CostVector(
        id="V7_water_and_land_restoration",
        name="Water consumption and land restoration",
        description=(
            "Fracking water, produced-water disposal, aquifer "
            "contamination, surface reclamation. Restoration energy is "
            "deferred indefinitely; in unconventional plays it is "
            "rarely fully amortized."
        ),
        why_omitted=(
            "Booked as future liability or transferred to public "
            "sector via abandonment. Not in operator EROI."
        ),
        direction="increases denominator",
    ),

    CostVector(
        id="V8_decline_curve_reality",
        name="Decline curve reality vs. reported EUR",
        description=(
            "Shale wells follow stretched-exponential decline (SEPD + "
            "Arps). Reported EUR (estimated ultimate recovery) is often "
            "based on early-life production; ~10% recovery rate is "
            "typical for unconventional. Treadmill drilling masks the "
            "system-wide decline."
        ),
        why_omitted=(
            "EUR is reported optimistically for investor and "
            "reserve-booking purposes; the decline curve is technical "
            "literature."
        ),
        direction="shrinks numerator",
    ),

    CostVector(
        id="V9_carbon_compliance_overhead",
        name="Carbon compliance and emissions overhead",
        description=(
            "EU-ETS carbon quotas (rising from 40% to 70% of emissions "
            "in 2026), methane regulation, CCS investments, and "
            "increasing reporting overhead. These convert energy "
            "delivered into compliance work."
        ),
        why_omitted=(
            "Treated as regulatory cost, not as energy diverted from "
            "delivery to compliance."
        ),
        direction="shrinks numerator",
    ),

    CostVector(
        id="V10_substrate_damage_to_dependent_populations",
        name="Substrate damage to dependent populations",
        description=(
            "Health and substrate-degradation costs to populations near "
            "extraction zones and along supply corridors (truck routes, "
            "refinery proximity, water contamination). Multi-generational "
            "epigenetic effects. Reduces the human-capacity substrate "
            "that the extraction system itself depends on."
        ),
        why_omitted=(
            "Externalized to public health systems and not measured "
            "against extraction output."
        ),
        direction="increases denominator",
    ),

]


# -----------------------------------------------------------------
# CASCADE PIPELINE  (how the suppressed vectors interact)
# -----------------------------------------------------------------

CASCADE_PIPELINE: List[Dict[str, str]] = [

    {
        "stage": "1. Reservoir geology",
        "stable_supply_assumption":
            "Recoverable reserves estimated from EUR projections; "
            "decline curve assumed gradual.",
        "actual_2026_state":
            "Eagle Ford in retreat. Permian top-tier inventory "
            "consolidating into 5 operators. Shale recovery ~10%. "
            "Net energy peak may already be past.",
    },

    {
        "stage": "2. Extraction equipment",
        "stable_supply_assumption":
            "Steel, valves, pumps, sensors available at flat real cost.",
        "actual_2026_state":
            "Supply chain disrupted; offshore EPC at $54B with 33% "
            "drop in FIDs YoY despite contract value rising 18%. "
            "Supply-chain inflation embedded in every well.",
    },

    {
        "stage": "3. Automation and digital twin",
        "stable_supply_assumption":
            "Automation reduces labor input; net energy benefit assumed.",
        "actual_2026_state":
            "Automation requires fabs at >$10-45B capex, $100-300M "
            "annual power per fab, 1,500-2,000 gal water per wafer, "
            "REE inputs from concentrated Chinese supply. Energy is "
            "relocated upstream, not eliminated.",
    },

    {
        "stage": "4. Workforce",
        "stable_supply_assumption":
            "Skilled labor available at modest training cost.",
        "actual_2026_state":
            "Up to 40,000 competent worker shortfall by 2025. Aging "
            "workforce, falling mobility, training budgets compressed, "
            "veteran culling structural. Skill decay non-linear.",
    },

    {
        "stage": "5. Logistics and shipping",
        "stable_supply_assumption":
            "Maritime routes stable; Suez and Hormuz open; insurance "
            "premiums baseline.",
        "actual_2026_state":
            "Hormuz disruption: 6.7 million b/d shut-in (EIA STEO). "
            "Rerouting around Cape of Good Hope normalizing. Up to 70% "
            "GHG increase per round trip. Insurance premiums elevated.",
    },

    {
        "stage": "6. Strategic reserves",
        "stable_supply_assumption":
            "SPR is a buffer; refill is routine.",
        "actual_2026_state":
            "SPR at lowest level since 1982 if full release completes. "
            "Refill mathematics under current production and EROI "
            "increasingly unfavorable. Buffer is being liquidated, "
            "not used.",
    },

    {
        "stage": "7. Refinery and product delivery",
        "stable_supply_assumption":
            "Refining capacity matches crude slate; product mix "
            "stable.",
        "actual_2026_state":
            "Crude slate shifting toward lighter unconventional that "
            "many refineries are not optimized for. Carbon compliance "
            "overhead rising. Net delivered fuel per barrel input "
            "declining.",
    },

    {
        "stage": "8. Public health / substrate cost",
        "stable_supply_assumption":
            "Externalized; not in calculation.",
        "actual_2026_state":
            "Documented epigenetic, endocrine, and developmental "
            "damage in proximate populations (Cambridge / Amedor & "
            "Giussani 2026 line of work). Substrate the extraction "
            "system depends on is being degraded.",
    },

]


# -----------------------------------------------------------------
# CLAIMS  (falsifiable)
# -----------------------------------------------------------------

class Confidence(Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


@dataclass
class Claim:
    id: str
    statement: str
    falsifier: str
    confirmer: str
    confidence: Confidence


CLAIMS: List[Claim] = [

    Claim(
        id="C1_published_eroi_omits_system_costs",
        statement=(
            "Published EROI figures for unconventional oil omit at least "
            "ten distinct cost vectors. They describe well-site "
            "thermodynamics, not delivered-fuel thermodynamics."
        ),
        falsifier=(
            "Peer-reviewed EROI calculation that explicitly accounts "
            "for V1-V10 yields published-range numbers (~6:1 for shale)."
        ),
        confirmer=(
            "Re-calculation including any subset of V1-V10 yields a "
            "systematically lower number, scaling with vectors included."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C2_automation_relocates_energy_upstream",
        statement=(
            "Automating extraction does not reduce system energy input; "
            "it relocates energy use into semiconductor fabrication, "
            "REE mining, and software infrastructure. Net system EROI "
            "does not improve and may decline."
        ),
        falsifier=(
            "Full life-cycle analysis of automated vs. non-automated "
            "extraction shows net energy savings inclusive of fab and "
            "REE supply chain."
        ),
        confirmer=(
            "Life-cycle analysis shows upstream energy cost equal to "
            "or greater than downstream labor energy saved."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C3_workforce_skill_decay_is_thermodynamic_cost",
        statement=(
            "Veteran workforce culling and training-budget compression "
            "is a thermodynamic cost: replacement is multi-year and "
            "non-linear. Operations under skill-depleted workforce show "
            "higher accident, repair, and rework energy."
        ),
        falsifier=(
            "Equivalent operational energy efficiency demonstrated "
            "across veteran-staffed and replacement-staffed crews."
        ),
        confirmer=(
            "Documented increases in incident rates, rework, and "
            "unplanned downtime correlating with workforce "
            "demographic shifts."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="C4_geopolitical_chokepoints_change_eroi",
        statement=(
            "Strait of Hormuz, Red Sea, Suez, and Panama disruptions "
            "materially change the energy cost per delivered barrel "
            "and are not embedded in current EROI calculations."
        ),
        falsifier=(
            "Demonstrate that shipping energy is small enough that "
            "rerouting does not materially affect EROI even at 70% "
            "round-trip emissions increase."
        ),
        confirmer=(
            "Quantify rerouting energy cost per barrel; show it "
            "materially shifts delivered EROI."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C5_spr_drawdown_is_hidden_subsidy",
        statement=(
            "Drawing strategic reserves to manage price during "
            "disruption is a thermodynamic transfer: future energy "
            "(needed to refill) is being borrowed against present "
            "stability. EROI of present barrels is overstated by "
            "this borrowing."
        ),
        falsifier=(
            "SPR is fully refillable under current production and "
            "future EROI conditions without compromising delivered "
            "supply."
        ),
        confirmer=(
            "Refill mathematics show declining feasibility as "
            "unconventional EROI compresses and production peaks."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C6_decline_curves_understated_in_reserves",
        statement=(
            "Estimated Ultimate Recovery for unconventional wells is "
            "systematically optimistic relative to observed decline "
            "behavior. Published reserve numbers embed this optimism."
        ),
        falsifier=(
            "Long-life (>6 year) well data confirms early-life EUR "
            "projections across the major shale plays."
        ),
        confirmer=(
            "Long-life data shows SEPD-Arps decline pattern with EUR "
            "below early projections."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C7_substrate_damage_reduces_system_capacity",
        statement=(
            "Public-health and ecological substrate damage in extraction "
            "regions reduces the capacity of populations the extraction "
            "system depends on. This is a measurable thermodynamic cost, "
            "not only an ethical concern."
        ),
        falsifier=(
            "Populations in high-extraction-density regions show "
            "equivalent long-term capacity metrics to comparison "
            "regions."
        ),
        confirmer=(
            "Substrate-damage markers (epigenetic, endocrine, "
            "developmental) elevated in proximate populations and "
            "transmitted across generations."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="C8_net_energy_peak_may_be_passed",
        statement=(
            "Net delivered energy from global oil liquids may already "
            "be at or past peak when V1-V10 are included, even though "
            "gross volume continues to grow."
        ),
        falsifier=(
            "Net energy continues to rise with gross volume after "
            "accounting for V1-V10."
        ),
        confirmer=(
            "Net energy plateaus or declines while gross volume rises; "
            "matches Delannoy et al. 2025 estimate."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="C9_extraction_dependency_loop_is_unstable",
        statement=(
            "Modern oil extraction depends on supply chains, "
            "semiconductors, rare earths, and global shipping that "
            "themselves depend on oil-derived inputs. The loop is "
            "self-referential and degrades under any sustained shock."
        ),
        falsifier=(
            "Identify any link in the extraction supply chain that "
            "operates independently of oil-derived energy or "
            "oil-dependent logistics."
        ),
        confirmer=(
            "Demonstrate the cascade: shock to any single layer (REE, "
            "semiconductor, shipping, workforce) propagates measurably "
            "to delivered EROI."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="C10_published_eroi_is_non_falsifiable_until_audited",
        statement=(
            "Until published EROI figures are recalculated with V1-V10 "
            "explicitly included or explicitly bounded, they are not "
            "falsifiable claims about delivered energy, only claims "
            "about a sub-system."
        ),
        falsifier=(
            "Published methodology document showing explicit treatment "
            "of all ten vectors."
        ),
        confirmer=(
            "Survey of cited EROI literature shows none of the ten "
            "vectors treated comprehensively in mainstream figures."
        ),
        confidence=Confidence.HIGH,
    ),

]


# -----------------------------------------------------------------
# SCORING DIMENSIONS  (audit any EROI claim against these)
# -----------------------------------------------------------------

SCORING_DIMENSIONS: Dict[str, str] = {

    "supply_chain_embodied_energy_included":
        "Are steel, REE, semiconductor, and logistics supply chains "
        "energy-accounted, or treated as externality?",

    "geopolitical_disruption_priced_in":
        "Does the calculation include current chokepoint risk, "
        "rerouting energy, and insurance overhead?",

    "spr_subsidy_amortized":
        "Is reserve drawdown counted as a transfer from future to "
        "present, or treated as free buffer?",

    "workforce_skill_decay_counted":
        "Does the calculation account for veteran loss, training "
        "compression, and replacement non-linearity?",

    "automation_upstream_energy_counted":
        "Is the fab + REE + control-system energy embedded in "
        "automated operations counted in the denominator?",

    "rare_earth_supply_risk_counted":
        "Is the energy cost of REE extraction and the "
        "supply-concentration risk priced in?",

    "water_land_restoration_amortized":
        "Are restoration liabilities energy-amortized, or deferred?",

    "decline_curve_realism":
        "Are well decline curves based on long-life data, or "
        "early-life EUR projections?",

    "carbon_compliance_overhead_included":
        "Is the energy diverted to compliance counted in the "
        "numerator reduction?",

    "substrate_damage_to_dependent_populations":
        "Are health and ecological substrate costs to "
        "extraction-region populations counted?",

}


# -----------------------------------------------------------------
# AUDIT GATE
# -----------------------------------------------------------------

@dataclass
class EROIClaim:
    name: str
    reported_eroi: float

    supply_chain_embodied_energy_included: int = 0
    geopolitical_disruption_priced_in: int = 0
    spr_subsidy_amortized: int = 0
    workforce_skill_decay_counted: int = 0
    automation_upstream_energy_counted: int = 0
    rare_earth_supply_risk_counted: int = 0
    water_land_restoration_amortized: int = 0
    decline_curve_realism: int = 0
    carbon_compliance_overhead_included: int = 0
    substrate_damage_to_dependent_populations: int = 0


def audit(claim: EROIClaim) -> Dict[str, object]:
    checks = {
        "supply_chain_embodied_energy_included":
            claim.supply_chain_embodied_energy_included,
        "geopolitical_disruption_priced_in":
            claim.geopolitical_disruption_priced_in,
        "spr_subsidy_amortized":
            claim.spr_subsidy_amortized,
        "workforce_skill_decay_counted":
            claim.workforce_skill_decay_counted,
        "automation_upstream_energy_counted":
            claim.automation_upstream_energy_counted,
        "rare_earth_supply_risk_counted":
            claim.rare_earth_supply_risk_counted,
        "water_land_restoration_amortized":
            claim.water_land_restoration_amortized,
        "decline_curve_realism":
            claim.decline_curve_realism,
        "carbon_compliance_overhead_included":
            claim.carbon_compliance_overhead_included,
        "substrate_damage_to_dependent_populations":
            claim.substrate_damage_to_dependent_populations,
    }

    score = sum(checks.values())
    max_score = len(checks)
    flagged = [k for k, v in checks.items() if v == 0]

    if score >= 8:
        verdict = (
            "ADMISSIBLE: system-level EROI calculation. Reported "
            "figure can be evaluated as a falsifiable claim."
        )
    elif score >= 5:
        verdict = (
            "PARTIAL: well-site or sub-system EROI. Reported figure "
            "is an upper bound on delivered-fuel EROI."
        )
    elif score >= 2:
        verdict = (
            "CONTAMINATED: omits major cost vectors. Reported figure "
            "is non-comparable to historical conventional EROI."
        )
    else:
        verdict = (
            "NON-FALSIFIABLE: omits substantially all system cost "
            "vectors. Reported figure describes only a sub-process, "
            "not delivered energy."
        )

    return {
        "claim": claim.name,
        "reported_eroi": claim.reported_eroi,
        "score": f"{score}/{max_score}",
        "verdict": verdict,
        "passed": [k for k, v in checks.items() if v == 1],
        "flagged": flagged,
    }


# -----------------------------------------------------------------
# WHAT A HONEST SYSTEM EROI ESTIMATE WOULD REQUIRE
# -----------------------------------------------------------------

HONEST_EROI_REQUIREMENTS: List[str] = [

    "Bottom-up energy accounting for every input in the cascade "
    "pipeline (steel, REE, semiconductor, software, workforce "
    "training, shipping, refining, compliance, restoration).",

    "Long-life decline-curve data (6+ years) for the wells being "
    "audited, with SEPD-Arps fitting rather than early-life EUR.",

    "Geopolitical adjustment: route-specific shipping energy under "
    "current chokepoint conditions, not historical baseline.",

    "Strategic reserve amortization: refill energy cost under current "
    "production and EROI conditions, applied to drawdown volume.",

    "Workforce thermodynamic accounting: training energy as "
    "accumulated capability, not as wage expense. Non-linear "
    "replacement penalty for veteran loss.",

    "Automation life-cycle: fab capex amortized, REE supply chain "
    "energy included, software maintenance and update energy "
    "counted.",

    "Substrate cost: documented public-health and ecological damage "
    "in proximate populations, energy-equivalent of capacity loss.",

    "Uncertainty bounds: published as range, not point estimate. "
    "Sensitivity analysis showing which vectors dominate.",

    "Falsifiability statement: explicit list of observations that "
    "would refute the calculation.",

    "Replicability: data and methodology available for independent "
    "audit.",

]


# -----------------------------------------------------------------
# CITATIONS
# -----------------------------------------------------------------

CITATIONS: List[str] = [

    "EIA Short-Term Energy Outlook, December 2025: US crude oil "
    "production 13.6 mb/d 2025, 13.5 mb/d forecast 2026.",

    "EIA / DOE: SPR inventory 411 MMbbl December 2025, ~125 days "
    "import protection.",

    "Delannoy et al.: net energy peak ~2025 at ~400 PJ/d; oil "
    "liquids weighted EROI 44.4 (1950) -> 6.7 (2050 projected).",

    "Engineer Fix synthesis: conventional oil historical EROI "
    ">100:1, unconventional shale ~6:1, oil shale in-situ ~1.5:1.",

    "Bakken/Eagle Ford/Permian decline curve analysis (>30,000 "
    "wells): SEPD + Arps required for accurate EUR; EUR overstated "
    "by early-life Arps alone.",

    "Art Berman: Eagle Ford peak Sept 2015 at 1.6 mb/d; Permian "
    "showing similar pattern of well-performance deterioration.",

    "EIA: forecast US production decline begins 2026; Bakken and "
    "Eagle Ford maturing with reduced productivity per well.",

    "Fortune / EIA: Strait of Hormuz disruption, 6.7 mb/d shut-ins "
    "May 2026 under conflict assumptions.",

    "UNCTAD: up to 70% GHG emissions increase on "
    "Singapore-Rotterdam round trip due to rerouting and speed.",

    "TSMC public capex disclosures: 2nm fab >$45 billion. "
    "Independent fab analyses: $100-300M annual power, 1,500-2,000 "
    "gallons water per wafer at 3nm.",

    "Accenture / IOGP: up to 40,000 competent worker shortfall by "
    "2025. Korn Ferry: 85 million unfilled skilled jobs globally.",

    "GETI 2026: aging workforce, falling mobility, softening pay "
    "expectations (67% vs 71%).",

    "Deloitte 2025 Oil and Gas Outlook: workforce reductions "
    "target higher-cost veterans; structural skill-base degradation.",

    "Rare-earth literature: China >95% historical supply share, "
    "demand >5x by 2030, <1% global recycling rate.",

    "Amedor & Giussani, Trends in Endocrinology & Metabolism, "
    "April 2026: physiological mechanisms of socio-environmental "
    "stress on pregnancy outcomes - substrate damage to dependent "
    "populations.",

]


# -----------------------------------------------------------------
# DEMO / SELF-TEST
# -----------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 64)
    print("OIL EXTRACTION THERMODYNAMIC CASCADE AUDIT")
    print("=" * 64)
    print()
    print(f"  Claims registered:        {len(CLAIMS)}")
    print(f"  Suppressed cost vectors:  {len(SUPPRESSED_VECTORS)}")
    print(f"  Cascade pipeline stages:  {len(CASCADE_PIPELINE)}")
    print(f"  Scoring dimensions:       {len(SCORING_DIMENSIONS)}")
    print(f"  Citations:                {len(CITATIONS)}")
    print()

    # Audit a typical published shale EROI claim
    typical_published = EROIClaim(
        name="Typical published shale oil EROI (~6:1)",
        reported_eroi=6.0,
        supply_chain_embodied_energy_included=0,
        geopolitical_disruption_priced_in=0,
        spr_subsidy_amortized=0,
        workforce_skill_decay_counted=0,
        automation_upstream_energy_counted=0,
        rare_earth_supply_risk_counted=0,
        water_land_restoration_amortized=0,
        decline_curve_realism=0,
        carbon_compliance_overhead_included=0,
        substrate_damage_to_dependent_populations=0,
    )

    partial = EROIClaim(
        name="Better-than-average EROI study",
        reported_eroi=6.0,
        supply_chain_embodied_energy_included=1,
        geopolitical_disruption_priced_in=0,
        spr_subsidy_amortized=0,
        workforce_skill_decay_counted=0,
        automation_upstream_energy_counted=0,
        rare_earth_supply_risk_counted=0,
        water_land_restoration_amortized=1,
        decline_curve_realism=1,
        carbon_compliance_overhead_included=1,
        substrate_damage_to_dependent_populations=0,
    )

    honest = EROIClaim(
        name="System-level EROI (hypothetical, fully audited)",
        reported_eroi=2.5,
        supply_chain_embodied_energy_included=1,
        geopolitical_disruption_priced_in=1,
        spr_subsidy_amortized=1,
        workforce_skill_decay_counted=1,
        automation_upstream_energy_counted=1,
        rare_earth_supply_risk_counted=1,
        water_land_restoration_amortized=1,
        decline_curve_realism=1,
        carbon_compliance_overhead_included=1,
        substrate_damage_to_dependent_populations=1,
    )

    for c in (typical_published, partial, honest):
        result = audit(c)
        print("-" * 64)
        print(f"CLAIM:         {result['claim']}")
        print(f"REPORTED:      {result['reported_eroi']}:1")
        print(f"SCORE:         {result['score']}")
        print(f"VERDICT:       {result['verdict']}")
        if result["flagged"]:
            print(f"FLAGGED:       {', '.join(result['flagged'])}")
        print()
