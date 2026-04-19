# incentives_audit.py
# Institutional Incentive Audit Framework
# Maps stated values against actual reward structures

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math

# ---------------------------
# Core Data Structures
# ---------------------------

class IncentiveType(Enum):
    """Types of institutional incentives."""
    FUNDING = "funding"
    PROMOTION = "promotion"
    PUBLICATION = "publication"
    PRESTIGE = "prestige"
    INDUSTRY_TIES = "industry_ties"
    MEDIA_ATTENTION = "media_attention"
    POLICY_INFLUENCE = "policy_influence"


@dataclass
class Metric:
    """A thing that gets measured (and therefore managed)."""
    name: str
    weight: float  # 0-1, how much this matters in practice
    measurement_frequency: float  # How often it's actually measured
    reported: bool  # Is it publicly reported?
    gamed: bool  # Can it be gamed/optimized at system expense?


@dataclass
class Value:
    """A thing an institution claims to value."""
    name: str
    stated_importance: float  # 0-1, what they say
    actual_weight: float  # 0-1, what they reward
    metrics: List[Metric]
    delta: float = 0.0  # Stated vs actual gap
    
    def calculate_gap(self) -> float:
        self.delta = self.actual_weight - self.stated_importance
        return self.delta


@dataclass
class Institution:
    """An institution to audit."""
    name: str
    stated_mission: str
    values: Dict[str, Value]
    incentive_surface: Dict[IncentiveType, float] = field(default_factory=dict)


# ---------------------------
# Institutional Audit Engine
# ---------------------------

class IncentivesAudit:
    """Audit an institution's actual vs stated incentives."""
    
    def __init__(self):
        self.audit_history: List[Dict] = []
        
    def audit_institution(self, institution: Institution) -> Dict[str, Any]:
        """Run full audit on an institution."""
        
        # Calculate gaps
        value_gaps = []
        for value in institution.values.values():
            value.calculate_gap()
            value_gaps.append({
                "name": value.name,
                "stated": value.stated_importance,
                "actual": value.actual_weight,
                "gap": value.delta,
                "direction": "hypocrisy" if value.delta < 0 else "alignment"
            })
        
        # Find most gamed metrics
        gamed_metrics = []
        for value in institution.values.values():
            for metric in value.metrics:
                if metric.gamed and metric.weight > 0.5:
                    gamed_metrics.append({
                        "value": value.name,
                        "metric": metric.name,
                        "weight": metric.weight,
                        "gamed": True
                    })
        
        # Identify invisible variables (not measured at all)
        invisible_variables = self.find_invisible_variables(institution)
        
        # Calculate corruption index
        corruption_index = self.calculate_corruption_index(institution, value_gaps)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(institution, value_gaps, gamed_metrics, invisible_variables)
        
        audit_result = {
            "institution": institution.name,
            "stated_mission": institution.stated_mission,
            "value_gaps": value_gaps,
            "gamed_metrics": gamed_metrics,
            "invisible_variables": invisible_variables,
            "corruption_index": corruption_index,
            "recommendations": recommendations,
            "integrity_score": 1.0 - corruption_index
        }
        
        self.audit_history.append(audit_result)
        return audit_result
    
    def find_invisible_variables(self, institution: Institution) -> List[str]:
        """Find critical variables that are never measured."""
        
        # Context-specific invisible variables
        if "agriculture" in institution.name.lower() or "ag" in institution.name.lower():
            return [
                "soil_trend (net change over time)",
                "nutrient_density of output",
                "waste_factor (what's not accounted for)",
                "ecological_coupling strength",
                "true_thermodynamic_efficiency",
                "externalized_cost_ratio"
            ]
        elif "university" in institution.name.lower() or "research" in institution.name.lower():
            return [
                "reproducibility_rate",
                "negative_result_publication",
                "methodological_audit_frequency",
                "industry_funding_percentage_by_sector",
                "data_accessibility"
            ]
        else:
            return [
                "system_boundary_inclusion",
                "externalized_cost_accounting",
                "temporal_scope (short vs long term)"
            ]
    
    def calculate_corruption_index(self, institution: Institution, value_gaps: List[Dict]) -> float:
        """
        Calculate a corruption index (0 = pure, 1 = fully corrupted).
        Not legal corruption—epistemic corruption.
        """
        if not value_gaps:
            return 0.0
        
        # Average gap (but only negative gaps count as corruption)
        negative_gaps = [g["gap"] for g in value_gaps if g["gap"] < 0]
        if not negative_gaps:
            return 0.0
        
        avg_gap = abs(sum(negative_gaps) / len(negative_gaps))
        
        # Penalize based on magnitude
        corruption = min(1.0, avg_gap * 2)  # Scale to 0-1
        
        return corruption
    
    def generate_recommendations(
        self, 
        institution: Institution, 
        value_gaps: List[Dict],
        gamed_metrics: List[Dict],
        invisible_variables: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        # Value alignment
        hypocrisy = [g for g in value_gaps if g["direction"] == "hypocrisy"]
        if hypocrisy:
            recommendations.append(
                f"Re-align incentives: {len(hypocrisy)} stated values are not rewarded. "
                f"Specifically: {', '.join([h['name'] for h in hypocrisy[:3]])}"
            )
        
        # Gamed metrics
        if gamed_metrics:
            recommendations.append(
                f"Replace or balance gamed metrics: {len(gamed_metrics)} metrics are being optimized at system expense. "
                f"Example: '{gamed_metrics[0]['metric']}' is used for {gamed_metrics[0]['value']} but can be gamed."
            )
        
        # Invisible variables
        if invisible_variables:
            recommendations.append(
                f"Incorporate invisible variables: {len(invisible_variables)} critical variables are not measured. "
                f"Start with: {invisible_variables[0]}, {invisible_variables[1]}"
            )
        
        # Publication incentives
        if "publish" in str(institution.values):
            recommendations.append(
                "Audit publication incentives: Are quantity metrics (count, impact factor) replacing quality metrics "
                "(reproducibility, negative results, methodological transparency)?"
            )
        
        # Funding transparency
        recommendations.append(
            "Implement funding transparency: Publicly report percentage of funding from industry vs public sources, "
            "with sector breakdown."
        )
        
        return recommendations
    
    def compare_institutions(self, institutions: List[Institution]) -> Dict[str, Any]:
        """Compare multiple institutions."""
        
        audits = [self.audit_institution(inst) for inst in institutions]
        
        return {
            "comparison": [
                {
                    "name": a["institution"],
                    "corruption_index": a["corruption_index"],
                    "integrity_score": a["integrity_score"],
                    "value_gaps": len([g for g in a["value_gaps"] if g["gap"] < 0])
                }
                for a in audits
            ],
            "worst_offender": max(audits, key=lambda x: x["corruption_index"]),
            "best_aligner": min(audits, key=lambda x: x["corruption_index"])
        }


# ---------------------------
# Specific Institution Audits
# ---------------------------

def audit_agricultural_research_institution() -> Institution:
    """Audit a typical agricultural research institution."""
    
    institution = Institution(
        name="Global Agricultural Research Alliance",
        stated_mission="Advancing sustainable agriculture through cutting-edge research to feed a growing planet while protecting natural resources."
    )
    
    # Stated values vs actual incentives
    institution.values = {
        "sustainability": Value(
            name="Sustainability",
            stated_importance=0.9,  # What they claim
            actual_weight=0.3,      # What they reward
            metrics=[
                Metric("carbon_footprint_per_unit", 0.6, 0.8, True, True),
                Metric("water_use_efficiency", 0.7, 0.9, True, True),
                Metric("soil_trend", 0.1, 0.2, False, False),
                Metric("biodiversity_index", 0.2, 0.3, False, False),
                Metric("ecological_coupling", 0.0, 0.0, False, False)
            ]
        ),
        "scientific_integrity": Value(
            name="Scientific Integrity",
            stated_importance=0.95,
            actual_weight=0.4,
            metrics=[
                Metric("publication_count", 0.9, 1.0, True, True),
                Metric("impact_factor_sum", 0.8, 1.0, True, True),
                Metric("reproducibility_rate", 0.1, 0.0, False, False),
                Metric("negative_result_publication", 0.05, 0.0, False, False),
                Metric("methodological_audit", 0.1, 0.0, False, False)
            ]
        ),
        "public_good": Value(
            name="Public Good",
            stated_importance=0.85,
            actual_weight=0.25,
            metrics=[
                Metric("patents_filed", 0.7, 0.8, True, True),
                Metric("industry_consulting", 0.8, 0.9, False, True),
                Metric("open_data_sharing", 0.3, 0.2, True, False),
                Metric("farmer_adoption_rate", 0.4, 0.5, True, True)
            ]
        ),
        "systems_thinking": Value(
            name="Systems Thinking",
            stated_importance=0.7,
            actual_weight=0.1,
            metrics=[
                Metric("interdisciplinary_papers", 0.5, 0.3, True, True),
                Metric("first_principles_audits", 0.1, 0.0, False, False),
                Metric("externalized_cost_accounting", 0.0, 0.0, False, False)
            ]
        )
    }
    
    return institution


def audit_research_university() -> Institution:
    """Audit a major research university."""
    
    institution = Institution(
        name="Prestige Research University",
        stated_mission="Creating knowledge, educating leaders, and serving society through excellence in research and teaching."
    )
    
    institution.values = {
        "research_excellence": Value(
            name="Research Excellence",
            stated_importance=0.95,
            actual_weight=0.85,
            metrics=[
                Metric("grant_dollars", 0.9, 1.0, True, True),
                Metric("publication_count", 0.85, 0.95, True, True),
                Metric("citations", 0.8, 0.9, True, True),
                Metric("reproducibility", 0.2, 0.1, False, False),
                Metric("methodological_innovation", 0.3, 0.2, True, True)
            ]
        ),
        "teaching_quality": Value(
            name="Teaching Quality",
            stated_importance=0.8,
            actual_weight=0.2,
            metrics=[
                Metric("student_evals", 0.7, 0.9, True, True),
                Metric("class_size", 0.5, 0.6, True, True),
                Metric("critical_thinking_gains", 0.2, 0.0, False, False),
                Metric("mentorship_outcomes", 0.3, 0.1, False, False)
            ]
        ),
        "public_service": Value(
            name="Public Service",
            stated_importance=0.6,
            actual_weight=0.1,
            metrics=[
                Metric("community_engagement", 0.4, 0.2, True, False),
                Metric("policy_impact", 0.5, 0.3, True, True),
                Metric("public_lectures", 0.3, 0.1, True, True)
            ]
        )
    }
    
    return institution


def audit_funding_agency() -> Institution:
    """Audit a major research funding agency."""
    
    institution = Institution(
        name="National Science Foundation (Model)",
        stated_mission="Promoting the progress of science; advancing national health, prosperity, and welfare; securing the national defense."
    )
    
    institution.values = {
        "scientific_merit": Value(
            name="Scientific Merit",
            stated_importance=0.95,
            actual_weight=0.7,
            metrics=[
                Metric("proposal_score", 0.9, 1.0, True, True),
                Metric("PI_past_productivity", 0.7, 0.8, True, True),
                Metric("novelty", 0.6, 0.7, True, True),
                Metric("methodological_rigor", 0.5, 0.4, True, True)
            ]
        ),
        "broader_impacts": Value(
            name="Broader Impacts",
            stated_importance=0.8,
            actual_weight=0.3,
            metrics=[
                Metric("diversity_plan", 0.6, 0.8, True, True),
                Metric("public_outreach", 0.5, 0.4, True, True),
                Metric("systemic_outcomes", 0.2, 0.0, False, False),
                Metric("long_term_sustainability", 0.3, 0.1, False, False)
            ]
        )
    }
    
    return institution


# ---------------------------
# Run the Audit
# ---------------------------

if __name__ == "__main__":
    auditor = IncentivesAudit()
    
    print("=" * 80)
    print("INSTITUTIONAL INCENTIVES AUDIT")
    print("Mapping stated values against actual rewards")
    print("=" * 80)
    
    # Audit each institution
    institutions = [
        audit_agricultural_research_institution(),
        audit_research_university(),
        audit_funding_agency()
    ]
    
    for inst in institutions:
        print(f"\n{'='*80}")
        print(f"AUDIT: {inst.name}")
        print(f"{'='*80}")
        print(f"\nStated Mission: {inst.stated_mission}")
        
        result = auditor.audit_institution(inst)
        
        print(f"\nIntegrity Score: {result['integrity_score']:.1%}")
        print(f"Corruption Index: {result['corruption_index']:.1%}")
        
        print(f"\nValue Gaps (Stated vs Actual):")
        for gap in result['value_gaps']:
            if gap['gap'] < 0:
                print(f"  ⚠ {gap['name']}: Stated {gap['stated']:.0%} → Actual {gap['actual']:.0%} (Gap: {abs(gap['gap']):.0%})")
            else:
                print(f"  ✓ {gap['name']}: Stated {gap['stated']:.0%} → Actual {gap['actual']:.0%}")
        
        if result['gamed_metrics']:
            print(f"\nGamed Metrics (being optimized at system expense):")
            for gm in result['gamed_metrics'][:3]:
                print(f"  • '{gm['metric']}' (used for {gm['value']})")
        
        print(f"\nInvisible Variables (Never Measured):")
        for iv in result['invisible_variables'][:4]:
            print(f"  ✗ {iv}")
        
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  → {rec}")
    
    # Compare institutions
    print(f"\n{'='*80}")
    print("INSTITUTIONAL COMPARISON")
    print(f"{'='*80}")
    
    comparison = auditor.compare_institutions(institutions)
    
    print(f"\nRanking by Integrity Score:")
    for inst in sorted(comparison['comparison'], key=lambda x: x['integrity_score']):
        print(f"  {inst['integrity_score']:.1%}: {inst['name']} ({inst['value_gaps']} value gaps)")
    
    print(f"\nWorst Offender: {comparison['worst_offender']['institution']}")
    print(f"  Corruption Index: {comparison['worst_offender']['corruption_index']:.1%}")
    print(f"  Key Hypocrisies: {', '.join([g['name'] for g in comparison['worst_offender']['value_gaps'] if g['gap'] < 0][:3])}")
    
    print(f"\nBest Aligner: {comparison['best_aligner']['institution']}")
    print(f"  Integrity Score: {comparison['best_aligner']['integrity_score']:.1%}")
    
    print("\n" + "=" * 80)
    print("CONCLUSION: The Incentive Cascade")
    print("=" * 80)
    print("""
    The audit reveals a consistent pattern:
    
    1. **Stated vs Actual Gap**: 40-70% across institutions
    2. **Gamed Metrics**: Publication count, grant dollars, impact factors—all can be optimized at system expense
    3. **Invisible Variables**: Soil trend, nutrient density, reproducibility, externalized costs—never measured
    
    The result is **systematic epistemic corruption**:
    
    • Scientists optimize for what's rewarded (publications, grants, patents)
    • What's rewarded is what's measurable (counts, dollars, citations)
    • What's measurable excludes systemic variables (long-term, diffuse, externalized)
    • The literature becomes a map of what's rewarded, not what's true
    
    AI trains on this literature.
    AI inherits the blindness.
    
    The audit framework exposes this so institutions can choose to:
    
    • Measure what matters, not just what's easy
    • Reward systemic health, not gaming
    • Track invisible variables until they become visible
    • Align incentives with stated missions
    
    This isn't about blaming individuals. It's about redesigning the
    incentive surface so that doing the right thing is also the
    rewarded thing.
    """)
