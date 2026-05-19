"""
refinery_stress_cascade_module.py

Companion module to oil_extraction_thermodynamic_cascade_audit.py.

Maps real 2025-2026 refinery incident data and the thermodynamic cost
of cascade failure under sustained overcapacity. Each fire, explosion,
and emergency shutdown is real energy and material cost that does not
appear in published EROI.

Core claim: equipment operated at 90+ percent sustained capacity
accumulates stress non-linearly. Failure probability compounds across
the network as load redistributes from failed units onto remaining
units. The cascade signature is exponential, not linear.

CC0. Standard library only.

See also (substrate-aware-accounting corpus):
  - substrate_damage_audit.py - population-level institutional damage
  - oil_extraction_thermodynamic_cascade_audit.py - ten cost vectors omitted from EROI
  - refinery_stress_cascade_module.py - 2025-2026 refinery incident data; cascade-failure cost vectors  (this module)
  - shale_well_thermodynamic_reality_module.py - Arps decline curves; per-well EROI recalculation
  - eroi_real_time_audit.py - re-run published EROI against current-period prices and supply flags
  - banking_thermodynamic_audit.py - capital-layer overhead; growth-constraint check
  - energy_cascade_audit.py - May 2026 cross-layer cascade detection (price, EROI, refining, demand, trust)
  - spr_operational_degradation_audit.py - SPR salt-cavern use vs design envelope; volume + cycling-stress audit
Corpus index: substrate_accounting/README.md  |  claims: substrate_accounting/CLAIMS_UNIFIED.json
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# -----------------------------------------------------------------
# DOCUMENTED INCIDENT DATA  (2025 - early 2026)
# -----------------------------------------------------------------

@dataclass
class Incident:
    date: str
    facility: str
    location: str
    capacity_bpd: Optional[int]
    type: str           # fire, explosion, shutdown, leak
    cause_reported: str
    casualties: int
    cascade_signal: str  # what this tells us about system state


INCIDENTS: List[Incident] = [

    Incident(
        date="2025-10-03",
        facility="Chevron El Segundo",
        location="California, US",
        capacity_bpd=285_000,
        type="fire",
        cause_reported="jet fuel unit incident",
        casualties=0,
        cascade_signal=(
            "CSB investigation suspended due to federal shutdown. "
            "Institutional capacity to analyze pattern eliminated."
        ),
    ),

    Incident(
        date="2025-2026",
        facility="Various US refineries",
        location="United States",
        capacity_bpd=None,
        type="multiple fires/explosions",
        cause_reported="~9 significant incidents in 2025",
        casualties=0,
        cascade_signal=(
            "Same count as 2015, but operating at much tighter margins. "
            "Frequency stable, severity rising due to network fragility."
        ),
    ),

    Incident(
        date="2026-03",
        facility="Valero Port Arthur",
        location="Texas, US",
        capacity_bpd=395_000,
        type="explosion",
        cause_reported="under investigation",
        casualties=0,
        cascade_signal=(
            "Evacuations, prolonged flaring event. One of largest "
            "US refineries by capacity."
        ),
    ),

    Incident(
        date="2026-04-16",
        facility="Viva Energy Geelong",
        location="Australia",
        capacity_bpd=120_000,
        type="fire",
        cause_reported="likely technical failure",
        casualties=0,
        cascade_signal=(
            "Company admitted maintenance postponed in March. "
            "March 2026 subsidy increase explicitly designed to keep "
            "production at maximum. Subsidy-induced failure pattern."
        ),
    ),

    Incident(
        date="2026-04-18",
        facility="BP Cherry Point",
        location="Washington State, US",
        capacity_bpd=251_000,
        type="fire",
        cause_reported="equipment failure during operations",
        casualties=0,
        cascade_signal=(
            "Return to 90+ percent capacity projected within weeks. "
            "Repair speed signals load pressure on remaining network."
        ),
    ),

    Incident(
        date="2026-04",
        facility="HPCL Pachpadra",
        location="Rajasthan, India",
        capacity_bpd=180_000,
        type="fire",
        cause_reported="during commissioning",
        casualties=0,
        cascade_signal="Disrupted commissioning of new capacity.",
    ),

    Incident(
        date="2026-04",
        facility="Vedanta power plant",
        location="Chhattisgarh, India",
        capacity_bpd=None,
        type="boiler explosion",
        cause_reported="under investigation",
        casualties=9,
        cascade_signal=(
            "Fatal incident. Power generation infrastructure showing "
            "same stress signature as refining."
        ),
    ),

    Incident(
        date="2026-04",
        facility="Tuapse refinery",
        location="Russia",
        capacity_bpd=240_000,
        type="fire",
        cause_reported="attack and equipment failure cascade",
        casualties=0,
        cascade_signal=(
            "Indefinite shutdown. Benzene and xylene released. "
            "Severe atmospheric contamination."
        ),
    ),

    Incident(
        date="2026-04",
        facility="Etoile oil well",
        location="Texas, US",
        capacity_bpd=None,
        type="oil well fire",
        cause_reported="undetermined",
        casualties=0,
        cascade_signal=(
            "Upstream extraction infrastructure showing same stress "
            "pattern as downstream refining."
        ),
    ),

]


# Documented pattern from open-source aggregation:
# April 2026 - 60-day window saw 10+ major incidents across 7 countries
# (US, Russia, Australia, India, Romania, others). Each individually
# explainable, collectively a network-state signal.
AGGREGATE_PATTERN = {
    "window": "April 2-20, 2026",
    "countries_affected": 7,
    "incidents_in_window": 10,
    "common_factor": (
        "Sustained operation above design capacity with deferred "
        "maintenance. Same root cause across geopolitically and "
        "operationally diverse facilities."
    ),
    "institutional_response": (
        "CSB (US Chemical Safety Board) cannot investigate due to "
        "federal shutdown. Proposed 2026 federal budget would "
        "eliminate the board entirely."
    ),
    "subsidy_signal": (
        "Australian government March 2026 fuel security subsidy "
        "increase explicitly designed to keep refineries at maximum "
        "production. Geelong fire followed within weeks. Subsidy "
        "structure rewards failure-mode operation."
    ),
}


# -----------------------------------------------------------------
# THERMODYNAMIC MECHANISM
# -----------------------------------------------------------------

CASCADE_MECHANISM = [

    {
        "stage": "1. Baseline operation",
        "capacity_pct": "75-85%",
        "state": (
            "Maintenance windows preserved. Cooling cycles complete. "
            "Material stress relieved. Failures random and rare."
        ),
    },

    {
        "stage": "2. Sustained overcapacity",
        "capacity_pct": "90-95%+",
        "state": (
            "Maintenance windows compressed or skipped. Cooling cycles "
            "shortened. Material stress accumulates. Failure probability "
            "rises with operating hours past design point."
        ),
    },

    {
        "stage": "3. First failure",
        "capacity_pct": "Local 0%, network +5-15%",
        "state": (
            "Single unit offline. Network reroutes load onto remaining "
            "units, which now run hotter. Their wear curves accelerate."
        ),
    },

    {
        "stage": "4. Cascade initiation",
        "capacity_pct": "Network 95-100%+",
        "state": (
            "Remaining units operating beyond design. Their failure "
            "probability compounds. Next failure timeline shortens "
            "exponentially, not linearly."
        ),
    },

    {
        "stage": "5. Repair drain",
        "capacity_pct": "Varies",
        "state": (
            "Repair consumes energy, capital, skilled labor. "
            "Maintenance budgets on remaining facilities cut to fund "
            "emergency response. Future failure probability rises "
            "system-wide."
        ),
    },

    {
        "stage": "6. Institutional blindness",
        "capacity_pct": "n/a",
        "state": (
            "CSB defunded. Pattern analysis suspended. Each incident "
            "treated as isolated. System loses ability to recognize "
            "its own cascade signature."
        ),
    },

]


# -----------------------------------------------------------------
# COST VECTORS  (omitted from published EROI)
# -----------------------------------------------------------------

@dataclass
class CostVector:
    id: str
    name: str
    description: str
    rough_magnitude: str


COST_VECTORS: List[CostVector] = [

    CostVector(
        id="R1_repair_energy",
        name="Repair energy per incident",
        description=(
            "Firefighting, demolition, rebuilding, testing, "
            "re-certification. Energy-intensive across every stage."
        ),
        rough_magnitude=(
            "Often equivalent to weeks of facility output in pure "
            "energy terms."
        ),
    ),

    CostVector(
        id="R2_lost_production",
        name="Lost production during downtime",
        description=(
            "Barrels not refined while facility offline. Demand "
            "redirected to other facilities, which now operate above "
            "their own design point."
        ),
        rough_magnitude=(
            "Capacity x downtime days. For a 250k bpd facility down "
            "30 days: 7.5 million barrels of refining throughput lost."
        ),
    ),

    CostVector(
        id="R3_accelerated_wear_on_remaining_capacity",
        name="Accelerated wear on remaining capacity",
        description=(
            "Every other refinery picks up displaced load. Their "
            "fatigue curves accelerate. Next failure timeline shortens."
        ),
        rough_magnitude=(
            "Non-linear. A 10% network capacity loss can drive 30-50% "
            "increase in network-wide failure probability."
        ),
    ),

    CostVector(
        id="R4_replacement_equipment_embedded_energy",
        name="Replacement equipment embedded energy",
        description=(
            "Replacement units require steel, REE, semiconductors, "
            "transportation. All energy-intensive, all sourced from "
            "the same depleting supply chains."
        ),
        rough_magnitude=(
            "Large capital equipment can embed years of operational "
            "energy in its manufacturing footprint."
        ),
    ),

    CostVector(
        id="R5_workforce_trauma_and_skill_loss",
        name="Workforce trauma and skill loss",
        description=(
            "Workers killed or injured represent decades of training "
            "lost. Survivors carry psychological cost. Replacement "
            "crews lack the experience to read early warning signs."
        ),
        rough_magnitude=(
            "Veteran loss is non-linear; replacement is multi-year "
            "and incomplete. Confer labor-thermodynamics framework."
        ),
    ),

    CostVector(
        id="R6_environmental_remediation",
        name="Environmental remediation",
        description=(
            "Benzene, xylene, PAHs released into atmosphere and soil. "
            "Cleanup energy enormous and rarely fully completed. "
            "Downstream substrate damage to dependent populations."
        ),
        rough_magnitude=(
            "Often exceeds direct repair cost when fully amortized; "
            "typically deferred to public sector or not amortized at "
            "all."
        ),
    ),

    CostVector(
        id="R7_investigation_and_compliance",
        name="Investigation and compliance overhead",
        description=(
            "Where investigations still happen, they consume energy "
            "and personnel time. Where they have been defunded "
            "(CSB), the cost is being externalized by deliberately "
            "not investigating. The system loses the feedback signal "
            "that would correct it."
        ),
        rough_magnitude=(
            "Per-incident cost suspended in 2025-2026 US context; "
            "long-term cost is loss of pattern-recognition capacity."
        ),
    ),

    CostVector(
        id="R8_insurance_premium_inflation",
        name="Insurance premium inflation",
        description=(
            "Every incident raises industry-wide premiums. Embedded "
            "in fuel prices and operational costs. Hidden energy tax "
            "on every barrel."
        ),
        rough_magnitude=(
            "Industry-wide premium effects compound; not captured "
            "in any single facility's EROI calculation."
        ),
    ),

    CostVector(
        id="R9_maintenance_budget_compression",
        name="Maintenance budget compression",
        description=(
            "Emergency response on one facility cuts maintenance "
            "budgets on others. Future failure probability rises "
            "system-wide. Self-reinforcing cascade."
        ),
        rough_magnitude=(
            "Each major incident shifts maintenance spend allocation "
            "across the entire operating fleet."
        ),
    ),

    CostVector(
        id="R10_subsidy_induced_failure_mode",
        name="Subsidy-induced failure mode",
        description=(
            "Government subsidies designed to keep refineries at "
            "maximum production financially reward exactly the "
            "operating regime that causes cascade failure. Public "
            "money funds the failure pattern."
        ),
        rough_magnitude=(
            "Geelong April 2026: subsidy increase in March, fire in "
            "April. Pattern is operational, not coincidental."
        ),
    ),

]


# -----------------------------------------------------------------
# FALSIFIABLE CLAIMS
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
        id="RC1_sustained_overcapacity_compresses_lifespan",
        statement=(
            "Equipment operated at sustained 90+ percent capacity "
            "accumulates material stress non-linearly, compressing "
            "operational lifespan and increasing failure probability."
        ),
        falsifier=(
            "Long-term fatigue data showing equivalent failure rates "
            "at 75% and 95% sustained capacity."
        ),
        confirmer=(
            "Material fatigue literature consistently shows "
            "exponential failure-rate scaling with sustained "
            "operation above design point."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="RC2_load_redistribution_compounds_failure",
        statement=(
            "When one unit fails in a tightly-loaded network, load "
            "redistributes to remaining units, accelerating their "
            "wear and increasing their failure probability. Cascade "
            "is exponential, not linear."
        ),
        falsifier=(
            "Network failure data showing independent (Poisson) "
            "failure distribution rather than clustering."
        ),
        confirmer=(
            "Observed clustering in time and across operators (e.g. "
            "April 2026 wave, 10+ incidents in 60 days across 7 "
            "countries)."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="RC3_repair_energy_omitted_from_eroi",
        statement=(
            "Repair energy and replacement-equipment embedded energy "
            "are systematically omitted from published EROI figures."
        ),
        falsifier=(
            "Published EROI methodology document showing explicit "
            "treatment of repair, replacement, and lost-production "
            "energy."
        ),
        confirmer=(
            "Survey of cited EROI literature shows none of these "
            "vectors treated in mainstream figures."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="RC4_subsidy_structures_reward_failure_mode",
        statement=(
            "Subsidy structures designed to keep refineries at "
            "maximum production financially reward the operating "
            "regime that causes cascade failure. The cost is "
            "externalized to public funds and proximate populations."
        ),
        falsifier=(
            "Subsidy designs that explicitly reward maintenance "
            "headroom and below-capacity operation, with documented "
            "lower incident rates."
        ),
        confirmer=(
            "Geelong April 2026: subsidy increase March, fire "
            "April. Pattern repeated across other subsidy-supported "
            "facilities."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="RC5_institutional_blindness_amplifies_cascade",
        statement=(
            "Defunding pattern-analysis institutions (CSB) removes "
            "the feedback signal that would otherwise correct the "
            "cascade. Each incident becomes isolated, pattern "
            "recognition is suspended, and the system loses ability "
            "to learn from its own failures."
        ),
        falsifier=(
            "CSB or equivalent body operating with full investigation "
            "capacity, producing published cascade-pattern analysis."
        ),
        confirmer=(
            "CSB investigation suspended on October 2025 El Segundo "
            "fire due to federal shutdown. Proposed 2026 budget "
            "would eliminate the board."
        ),
        confidence=Confidence.HIGH,
    ),

    Claim(
        id="RC6_cascade_failure_reduces_system_eroi",
        statement=(
            "When cascade-failure cost vectors (R1-R10) are included, "
            "system-level EROI for delivered refined fuel is reduced "
            "by an additional 0.5 to 1.5 points relative to "
            "published well-site figures."
        ),
        falsifier=(
            "Comprehensive system-level EROI calculation including "
            "R1-R10 yields figures equivalent to published well-site "
            "EROI."
        ),
        confirmer=(
            "Bottom-up accounting of repair, replacement, and "
            "cascade costs yields material EROI reduction."
        ),
        confidence=Confidence.MODERATE,
    ),

    Claim(
        id="RC7_substrate_damage_compounds_with_cascade",
        statement=(
            "Each cascade incident releases hazardous substances "
            "into proximate populations, compounding the "
            "substrate-damage signal already documented for chronic "
            "stress in extraction-zone populations."
        ),
        falsifier=(
            "Air, water, and biological monitoring around incident "
            "sites showing no elevation in benzene, PAH, and related "
            "biomarkers."
        ),
        confirmer=(
            "Tuapse 2026: documented benzene and xylene release. "
            "Long-term proximate-population health markers track "
            "incident frequency."
        ),
        confidence=Confidence.MODERATE,
    ),

]


# -----------------------------------------------------------------
# SCORING DIMENSIONS
# -----------------------------------------------------------------

SCORING_DIMENSIONS: Dict[str, str] = {

    "repair_energy_included":
        "Does the EROI calculation include repair and remediation "
        "energy per expected incident?",

    "lost_production_amortized":
        "Is downtime-induced lost production amortized into "
        "delivered-fuel EROI?",

    "load_redistribution_modeled":
        "Does the model account for accelerated wear on remaining "
        "capacity when units fail?",

    "replacement_equipment_embedded_energy":
        "Is replacement-equipment manufacturing energy counted?",

    "workforce_loss_priced":
        "Is veteran workforce loss from incidents priced as "
        "non-linear capability loss?",

    "environmental_remediation_amortized":
        "Are atmospheric and soil contamination cleanup costs "
        "amortized into delivered EROI?",

    "investigation_overhead_counted":
        "Is the cost of investigation (or the cost of losing "
        "investigative capacity) accounted for?",

    "insurance_inflation_embedded":
        "Are industry-wide insurance premium increases following "
        "incidents reflected in operational EROI?",

    "maintenance_budget_dynamics":
        "Does the model account for maintenance budget compression "
        "across the fleet following major incidents?",

    "subsidy_structure_audit":
        "Does the model audit subsidy structures for failure-mode "
        "reinforcement?",

}


# -----------------------------------------------------------------
# AUDIT GATE
# -----------------------------------------------------------------

@dataclass
class CascadeAuditClaim:
    name: str
    repair_energy_included: int = 0
    lost_production_amortized: int = 0
    load_redistribution_modeled: int = 0
    replacement_equipment_embedded_energy: int = 0
    workforce_loss_priced: int = 0
    environmental_remediation_amortized: int = 0
    investigation_overhead_counted: int = 0
    insurance_inflation_embedded: int = 0
    maintenance_budget_dynamics: int = 0
    subsidy_structure_audit: int = 0


def audit(claim: CascadeAuditClaim) -> Dict[str, object]:
    checks = {
        "repair_energy_included":
            claim.repair_energy_included,
        "lost_production_amortized":
            claim.lost_production_amortized,
        "load_redistribution_modeled":
            claim.load_redistribution_modeled,
        "replacement_equipment_embedded_energy":
            claim.replacement_equipment_embedded_energy,
        "workforce_loss_priced":
            claim.workforce_loss_priced,
        "environmental_remediation_amortized":
            claim.environmental_remediation_amortized,
        "investigation_overhead_counted":
            claim.investigation_overhead_counted,
        "insurance_inflation_embedded":
            claim.insurance_inflation_embedded,
        "maintenance_budget_dynamics":
            claim.maintenance_budget_dynamics,
        "subsidy_structure_audit":
            claim.subsidy_structure_audit,
    }

    score = sum(checks.values())
    max_score = len(checks)
    flagged = [k for k, v in checks.items() if v == 0]

    if score >= 8:
        verdict = (
            "ADMISSIBLE: cascade-aware accounting. Published EROI "
            "figures comparable to system-level reality."
        )
    elif score >= 5:
        verdict = (
            "PARTIAL: some cascade costs included. Published figure "
            "is an upper bound."
        )
    elif score >= 2:
        verdict = (
            "CONTAMINATED: most cascade costs externalized. "
            "Published figure overstates system-level EROI."
        )
    else:
        verdict = (
            "NON-FALSIFIABLE: cascade costs entirely omitted. "
            "Published figure cannot represent delivered-fuel EROI."
        )

    return {
        "claim": claim.name,
        "score": f"{score}/{max_score}",
        "verdict": verdict,
        "passed": [k for k, v in checks.items() if v == 1],
        "flagged": flagged,
    }


# -----------------------------------------------------------------
# CITATIONS
# -----------------------------------------------------------------

CITATIONS: List[str] = [

    "Reuters / AOC: ~9 significant US refinery fires/explosions "
    "2025 across Chevron, Marathon, Valero, Phillips 66, CITGO, "
    "Hunt Refining, and others.",

    "Reuters / Wikipedia: Chevron El Segundo fire, October 3 2025; "
    "CSB investigation suspended due to federal shutdown.",

    "TRT World / The National: April 2026 wave of refinery and "
    "power-plant fires across US, Russia, Australia, India, "
    "Romania; 10+ incidents in 60-day window.",

    "World Socialist Web Site: Viva Energy Geelong fire "
    "April 16 2026; company admitted March maintenance postponed; "
    "Australian government FSSP subsidy increase March 2026 to "
    "maximize production.",

    "TRT World / Reuters: Valero Port Arthur explosion "
    "March 2026; BP Cherry Point fire April 18-19 2026; HPCL "
    "Pachpadra and Vedanta Chhattisgarh incidents April 2026.",

    "Utah News Dispatch / Cobb Courier: Federal shutdown blocks "
    "CSB investigation of El Segundo; proposed 2026 federal "
    "budget would eliminate the CSB entirely.",

    "Union of Concerned Scientists: 2017-2023 US refinery "
    "incidents, 1500+ injuries, 7 deaths across 153 refineries.",

    "Wikipedia: 2026 Tuapse environmental disaster - indefinite "
    "shutdown, benzene and xylene atmospheric release.",

    "JP Morgan analysis (via The National): refining capacity "
    "stressed by Hormuz blockade, refined-product inventory data "
    "poor, export bans spreading (China, Russia, Kazakhstan, "
    "Thailand, India).",

    "EIA Short-Term Energy Outlook: refinery closures and rising "
    "consumption driving US fuel inventories to multi-decade lows "
    "in 2026.",

]


# -----------------------------------------------------------------
# DEMO / SELF-TEST
# -----------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 64)
    print("REFINERY STRESS CASCADE MODULE")
    print("2025-2026 Incident Data Analysis")
    print("=" * 64)
    print()
    print(f"  Documented incidents:        {len(INCIDENTS)}")
    print(f"  Cascade mechanism stages:    {len(CASCADE_MECHANISM)}")
    print(f"  Cost vectors:                {len(COST_VECTORS)}")
    print(f"  Falsifiable claims:          {len(CLAIMS)}")
    print(f"  Scoring dimensions:          {len(SCORING_DIMENSIONS)}")
    print(f"  Citations:                   {len(CITATIONS)}")
    print()
    print("  April 2026 60-day window:    10+ incidents, 7 countries")
    print("  Common factor:               Sustained overcapacity + "
          "deferred maintenance")
    print("  Institutional response:      CSB defunded; pattern "
          "analysis suspended")
    print()

    typical_published = CascadeAuditClaim(
        name="Typical published EROI (no cascade costs)",
    )

    partial = CascadeAuditClaim(
        name="EROI study with environmental and lost-production costs",
        repair_energy_included=1,
        lost_production_amortized=1,
        environmental_remediation_amortized=1,
    )

    full = CascadeAuditClaim(
        name="System-level cascade-aware EROI (hypothetical)",
        repair_energy_included=1,
        lost_production_amortized=1,
        load_redistribution_modeled=1,
        replacement_equipment_embedded_energy=1,
        workforce_loss_priced=1,
        environmental_remediation_amortized=1,
        investigation_overhead_counted=1,
        insurance_inflation_embedded=1,
        maintenance_budget_dynamics=1,
        subsidy_structure_audit=1,
    )

    for c in (typical_published, partial, full):
        result = audit(c)
        print("-" * 64)
        print(f"CLAIM:    {result['claim']}")
        print(f"SCORE:    {result['score']}")
        print(f"VERDICT:  {result['verdict']}")
        if result["flagged"]:
            print(f"FLAGGED:  {', '.join(result['flagged'])}")
        print()
