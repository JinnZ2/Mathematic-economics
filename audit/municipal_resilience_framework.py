"""
municipal_resilience_framework.py

Restructures municipal/township incentive systems so they
reward businesses that build community substrate and filter
out extraction-model businesses that degrade it.

Three coupled layers:

  1. Actuarial pricing layer (insurance reframed for systemic resilience)
  2. Municipal scoring layer (business reputation tied to substrate health)
  3. Tax/zoning incentive layer (cost to operate scales with extraction ratio)

The three together flip the incentive: extraction becomes
expensive, contribution becomes cheap.

Coupled to monolith_brittleness: a list of BusinessProfile aggregates
into a municipality-level SystemNode whose resilience and shock survival
can be measured directly. This closes the loop between micro (per-business
incentive pricing) and macro (whole-town fragility under shock).

License: CC0 1.0 Universal
"""

from dataclasses import dataclass
from typing import Dict, List

from monolith_brittleness import (
    SystemNode,
    monolith_synchrony_failure,
    resilience_score,
    simulate_shock,
)


# -----------------------------------------------------------------------------
# BUSINESS PROFILE
# -----------------------------------------------------------------------------

@dataclass
class BusinessProfile:
    name: str

    # workforce signals
    avg_tenure_years: float            # higher = more committed substrate
    pension_or_equivalent: bool        # binary: real long-term commitment
    discretionary_effort_index: float  # 0..1 from worker surveys / safety reports
    accident_rate_per_1000: float      # actuarial input
    turnover_rate_pct: float           # actuarial input

    # community signals
    local_supplier_pct: float              # 0..1 fraction of inputs from local economy
    profit_recirculated_local_pct: float   # 0..1 fraction kept in local loop
    community_lifespan_years: int          # years operating in this community
    externalized_costs: float              # 0..1 fraction of costs pushed onto community

    # extraction signals
    profit_extracted_to_holding_pct: float  # 0..1
    debt_loaded_for_extraction: bool
    subsidiary_liability_shuffling: bool

    # cascade signals
    sole_employer_dependency: float       # 0..1 -- community dependence on this firm
    substrate_knowledge_retained: float   # 0..1 -- how much knowledge stays vs leaves


# -----------------------------------------------------------------------------
# LAYER 1: ACTUARIAL RESILIENCE PRICING
# -----------------------------------------------------------------------------

def actuarial_resilience_score(b: BusinessProfile) -> dict:
    """
    Reframes insurance pricing from short-term extraction risk
    to long-term cascade-failure risk.

    LOWER score = lower premium (better risk).
    HIGHER score = higher premium (worse risk).
    """

    # short-term risk (current actuary view)
    short_term = (
        b.accident_rate_per_1000 / 100.0 +
        b.turnover_rate_pct / 100.0
    )

    # systemic risk (the missing layer)
    instability_penalty = 0.0
    if b.avg_tenure_years < 3.0:
        instability_penalty += 0.30
    if not b.pension_or_equivalent:
        instability_penalty += 0.20
    if b.discretionary_effort_index < 0.4:
        instability_penalty += 0.25
    if b.substrate_knowledge_retained < 0.3:
        instability_penalty += 0.20

    cascade_penalty = (
        b.sole_employer_dependency * 0.4 +
        b.externalized_costs * 0.5 +
        b.profit_extracted_to_holding_pct * 0.3
    )

    # commitment discount
    discount = 0.0
    if b.avg_tenure_years > 7:
        discount += 0.15
    if b.pension_or_equivalent:
        discount += 0.20
    if b.discretionary_effort_index > 0.7:
        discount += 0.15
    if b.local_supplier_pct > 0.5:
        discount += 0.10

    total = short_term + instability_penalty + cascade_penalty - discount
    return {
        "premium_index": round(max(0.05, total), 3),
        "short_term_risk": round(short_term, 3),
        "systemic_risk": round(instability_penalty + cascade_penalty, 3),
        "commitment_discount": round(discount, 3),
    }


# -----------------------------------------------------------------------------
# LAYER 2: MUNICIPAL REPUTATION SCORE
# -----------------------------------------------------------------------------

def municipal_reputation_score(b: BusinessProfile) -> dict:
    """
    Score the business as a community member.
    Used by municipality for zoning, permits, contract eligibility.

    Range: -1.0 (extraction predator) to +1.0 (substrate contributor)
    """
    contribution = (
        b.local_supplier_pct * 0.20 +
        b.profit_recirculated_local_pct * 0.25 +
        b.discretionary_effort_index * 0.10 +
        b.substrate_knowledge_retained * 0.15 +
        min(b.community_lifespan_years / 50.0, 1.0) * 0.20 +
        (0.10 if b.pension_or_equivalent else 0.0)
    )

    extraction = (
        b.profit_extracted_to_holding_pct * 0.30 +
        b.externalized_costs * 0.30 +
        (0.20 if b.debt_loaded_for_extraction else 0.0) +
        (0.20 if b.subsidiary_liability_shuffling else 0.0)
    )

    score = round(contribution - extraction, 3)
    classification = (
        "substrate_contributor"  if score > 0.4  else
        "neutral"                if score > -0.1 else
        "extraction_predator"
    )
    return {
        "score": score,
        "contribution": round(contribution, 3),
        "extraction": round(extraction, 3),
        "classification": classification,
    }


# -----------------------------------------------------------------------------
# LAYER 3: TAX / ZONING INCENTIVE
# -----------------------------------------------------------------------------

def tax_and_zoning_treatment(b: BusinessProfile, base_rate: float = 0.05) -> dict:
    """
    Tax rate scales with extraction ratio.
    Substrate contributors get reduced rates and zoning priority.
    Extraction predators pay more and face zoning friction.
    """
    rep = municipal_reputation_score(b)
    score = rep["score"]

    if score > 0.4:
        rate_multiplier = 0.5
        zoning = "priority"
        permit_speed = "expedited"
    elif score > 0.1:
        rate_multiplier = 0.75
        zoning = "favorable"
        permit_speed = "standard"
    elif score > -0.1:
        rate_multiplier = 1.0
        zoning = "standard"
        permit_speed = "standard"
    elif score > -0.4:
        rate_multiplier = 1.5
        zoning = "restricted"
        permit_speed = "extended_review"
    else:
        rate_multiplier = 2.5
        zoning = "blocked"
        permit_speed = "denied_pending_review"

    return {
        "effective_tax_rate": round(base_rate * rate_multiplier, 4),
        "zoning_status": zoning,
        "permit_speed": permit_speed,
        "rate_multiplier": rate_multiplier,
    }


# -----------------------------------------------------------------------------
# COUPLED FRAMEWORK (per-business)
# -----------------------------------------------------------------------------

def evaluate_business(b: BusinessProfile) -> dict:
    return {
        "name": b.name,
        "actuarial": actuarial_resilience_score(b),
        "reputation": municipal_reputation_score(b),
        "tax_zoning": tax_and_zoning_treatment(b),
    }


# -----------------------------------------------------------------------------
# COUPLING TO monolith_brittleness (municipality-level SystemNode)
# -----------------------------------------------------------------------------

def _stdev(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5


def municipality_to_system_node(
    name: str,
    businesses: List[BusinessProfile],
    energy_dependency: float = 0.6,
) -> SystemNode:
    """
    Aggregate a list of BusinessProfile into a SystemNode that represents
    the municipality as a whole. The aggregate can then be fed directly
    into resilience_score / simulate_shock / monolith_synchrony_failure
    from monolith_brittleness, closing the loop between per-business
    incentive pricing and town-level fragility.

    Aggregation logic:
      - cognitive_diversity   from variance of extraction / substrate /
                              local-sourcing across the business mix
                              (homogeneous mix -> low diversity)
      - substrate_knowledge   mean of substrate_knowledge_retained
      - extraction_ratio      mean of profit_extracted_to_holding_pct
      - feedback_loop_strength  1 - mean(externalized_costs)
      - redundancy            1 - max(sole_employer_dependency)
                              (one dominant employer collapses redundancy)
      - local_adaptation      mean(local_supplier_pct)
      - energy_dependency     parameter (not derivable from BusinessProfile)
    """
    if not businesses:
        raise ValueError("municipality_to_system_node requires at least one business")

    extractions = [b.profit_extracted_to_holding_pct for b in businesses]
    substrates = [b.substrate_knowledge_retained for b in businesses]
    locals_ = [b.local_supplier_pct for b in businesses]
    externals = [b.externalized_costs for b in businesses]
    deps = [b.sole_employer_dependency for b in businesses]

    profile_variance = (_stdev(extractions) + _stdev(substrates) + _stdev(locals_)) / 3.0
    cognitive_diversity = min(1.0, profile_variance * 2.0)

    n = len(businesses)
    return SystemNode(
        name=name,
        cognitive_diversity=cognitive_diversity,
        substrate_knowledge=sum(substrates) / n,
        extraction_ratio=sum(extractions) / n,
        feedback_loop_strength=1.0 - sum(externals) / n,
        redundancy=1.0 - max(deps),
        local_adaptation=sum(locals_) / n,
        energy_dependency=energy_dependency,
    )


def municipal_resilience_report(
    name: str,
    businesses: List[BusinessProfile],
    energy_dependency: float = 0.6,
    shock_magnitude: float = 0.5,
) -> dict:
    """
    Full coupled report:
      - per-business actuarial / reputation / tax-zoning treatment
      - aggregate SystemNode for the municipality
      - resilience_score and shock survival across all four shock types
      - monolith synchrony test on the aggregate
    """
    per_business = [evaluate_business(b) for b in businesses]
    node = municipality_to_system_node(name, businesses, energy_dependency)

    shocks = {
        shock: simulate_shock(node, shock_magnitude, shock)
        for shock in ("supply", "energy", "knowledge", "extraction_revolt")
    }
    synchrony = monolith_synchrony_failure({name: node}, shock_magnitude, "energy")[name]

    return {
        "name": name,
        "per_business": per_business,
        "aggregate_node": node,
        "resilience_score": resilience_score(node),
        "shock_survival": shocks,
        "synchrony_test": synchrony,
    }


# -----------------------------------------------------------------------------
# REFERENCE PROFILES
# -----------------------------------------------------------------------------

def reference_profiles() -> List[BusinessProfile]:
    return [
        BusinessProfile(
            name="Long-tenure regional manufacturer (Costco-like)",
            avg_tenure_years=9.0, pension_or_equivalent=True,
            discretionary_effort_index=0.78,
            accident_rate_per_1000=2.1, turnover_rate_pct=12.0,
            local_supplier_pct=0.45, profit_recirculated_local_pct=0.55,
            community_lifespan_years=40, externalized_costs=0.10,
            profit_extracted_to_holding_pct=0.20,
            debt_loaded_for_extraction=False,
            subsidiary_liability_shuffling=False,
            sole_employer_dependency=0.30,
            substrate_knowledge_retained=0.80,
        ),
        BusinessProfile(
            name="Big-box extraction model (Walmart-like)",
            avg_tenure_years=1.8, pension_or_equivalent=False,
            discretionary_effort_index=0.30,
            accident_rate_per_1000=4.5, turnover_rate_pct=68.0,
            local_supplier_pct=0.05, profit_recirculated_local_pct=0.10,
            community_lifespan_years=15, externalized_costs=0.55,
            profit_extracted_to_holding_pct=0.85,
            debt_loaded_for_extraction=True,
            subsidiary_liability_shuffling=True,
            sole_employer_dependency=0.65,
            substrate_knowledge_retained=0.15,
        ),
        BusinessProfile(
            name="Small local farm cooperative",
            avg_tenure_years=15.0, pension_or_equivalent=False,
            discretionary_effort_index=0.85,
            accident_rate_per_1000=3.0, turnover_rate_pct=8.0,
            local_supplier_pct=0.85, profit_recirculated_local_pct=0.90,
            community_lifespan_years=60, externalized_costs=0.05,
            profit_extracted_to_holding_pct=0.05,
            debt_loaded_for_extraction=False,
            subsidiary_liability_shuffling=False,
            sole_employer_dependency=0.10,
            substrate_knowledge_retained=0.95,
        ),
        BusinessProfile(
            name="PE-owned roll-up (debt-loaded extraction)",
            avg_tenure_years=1.2, pension_or_equivalent=False,
            discretionary_effort_index=0.20,
            accident_rate_per_1000=6.0, turnover_rate_pct=85.0,
            local_supplier_pct=0.02, profit_recirculated_local_pct=0.05,
            community_lifespan_years=4, externalized_costs=0.70,
            profit_extracted_to_holding_pct=0.95,
            debt_loaded_for_extraction=True,
            subsidiary_liability_shuffling=True,
            sole_employer_dependency=0.50,
            substrate_knowledge_retained=0.05,
        ),
    ]


def reference_municipalities() -> Dict[str, List[BusinessProfile]]:
    """
    Three illustrative town compositions to show how business mix
    propagates to municipal-level fragility.
    """
    profiles = {p.name: p for p in reference_profiles()}
    manufacturer = profiles["Long-tenure regional manufacturer (Costco-like)"]
    bigbox = profiles["Big-box extraction model (Walmart-like)"]
    farm = profiles["Small local farm cooperative"]
    pe = profiles["PE-owned roll-up (debt-loaded extraction)"]

    return {
        "extraction_town":   [bigbox, bigbox, pe, pe],
        "balanced_town":     [manufacturer, bigbox, farm, pe],
        "substrate_town":    [manufacturer, manufacturer, farm, farm],
    }


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    profiles = reference_profiles()

    for b in profiles:
        result = evaluate_business(b)
        print(f"\n{'='*70}")
        print(f"  {result['name']}")
        print(f"{'='*70}")

        a = result["actuarial"]
        print(f"  ACTUARIAL")
        print(f"    premium_index:        {a['premium_index']}")
        print(f"    short_term_risk:      {a['short_term_risk']}")
        print(f"    systemic_risk:        {a['systemic_risk']}")
        print(f"    commitment_discount:  {a['commitment_discount']}")

        r = result["reputation"]
        print(f"  MUNICIPAL REPUTATION")
        print(f"    score:                {r['score']:+.3f}")
        print(f"    classification:       {r['classification']}")

        t = result["tax_zoning"]
        print(f"  TAX / ZONING")
        print(f"    effective_tax_rate:   {t['effective_tax_rate']}")
        print(f"    zoning_status:        {t['zoning_status']}")
        print(f"    permit_speed:         {t['permit_speed']}")

    print(f"\n{'='*70}")
    print("  HYPOTHESIS")
    print(f"{'='*70}")
    print("  Extraction-model businesses face higher actuarial premiums,")
    print("  worse municipal reputation, and 2-3x effective tax rates.")
    print("  Substrate-contributor businesses get lower premiums, priority")
    print("  zoning, and reduced tax rates.")
    print("  The incentive structure FLIPS without changing the underlying laws --")
    print("  it changes the PRICING of cost-sources and risk pools.")

    print(f"\n{'='*70}")
    print("  COUPLED: per-business incentives -> municipal SystemNode resilience")
    print(f"{'='*70}")
    for town, members in reference_municipalities().items():
        rep = municipal_resilience_report(town, members, energy_dependency=0.7,
                                          shock_magnitude=0.5)
        node = rep["aggregate_node"]
        print(f"\n  {town}")
        print(f"    aggregate extraction_ratio:  {node.extraction_ratio:.3f}")
        print(f"    aggregate cognitive_div:     {node.cognitive_diversity:.3f}")
        print(f"    aggregate redundancy:        {node.redundancy:.3f}")
        print(f"    resilience_score:            {rep['resilience_score']:+.3f}")
        print(f"    shock survival (supply):     {rep['shock_survival']['supply']*100:5.1f}%")
        print(f"    shock survival (energy):     {rep['shock_survival']['energy']*100:5.1f}%")
        print(f"    shock survival (knowledge):  {rep['shock_survival']['knowledge']*100:5.1f}%")
        print(f"    shock survival (revolt):     {rep['shock_survival']['extraction_revolt']*100:5.1f}%")
        print(f"    network survival (synchrony-weighted): "
              f"{rep['synchrony_test']['network_survival']*100:5.1f}%")
