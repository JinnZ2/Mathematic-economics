# efficiency_report_audit.py
# Audit of "New Efficiency" industry reports (2025-2026).
# Exposes the gap between claimed breakthroughs and systemic reality by running
# representative archetypes through the Six Sigma auditor and field-system
# rule engine, then comparing against a first-principles baseline.

import os
import sys
from datetime import datetime
from typing import Any, Dict

from field_system import effective_yield, fill_state, report
from system_audit import SixSigmaAudit

# Optional PhysicsGuard integration. physics_guard/ is a vendored snapshot
# (see physics_guard/PROVENANCE.md) with flat internal imports, so we add it
# to sys.path rather than importing it as a package. If unavailable, the
# audit runs without the physics-verdict step.
_PG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "physics_guard")
if os.path.isdir(_PG_DIR) and _PG_DIR not in sys.path:
    sys.path.insert(0, _PG_DIR)
try:
    from main import check as physics_check  # type: ignore
    _HAS_PHYSICS_GUARD = True
except Exception:
    _HAS_PHYSICS_GUARD = False

# Optional metabolic-accounting bridge. See audit/metabolic_bridge.py for
# the discovery logic. The import always succeeds; whether it does anything
# at runtime is gated on metabolic_bridge._HAS_METABOLIC_ACCOUNTING.
from metabolic_bridge import (
    basins_from_field_scenario,
    metabolic_check,
    stress_from_field_scenario,
)
from money_signal_bridge import money_signal_metrics


# ---------------------------
# Representative "New Efficiency" Industry Report
# Based on typical 2025-2026 agricultural technology publications
# ---------------------------

class EfficiencyIndustryReport:
    """Structure of a typical 2025-2026 'efficiency breakthrough' report."""

    def __init__(self):
        self.title = (
            "The Precision Agriculture Revolution: "
            "300% Efficiency Gains Through AI-Driven Optimization"
        )
        self.publisher = "Global Agri-Tech Alliance"
        self.date = "Q1 2026"
        self.claims = {
            "productivity_gain": "300% increase in output per input unit",
            "water_efficiency": "50% reduction in water usage through smart irrigation",
            "carbon_footprint": "40% reduction in emissions per unit produced",
            "profit_margin": "25% increase in farmer profitability",
            "scalability": "Deployable across 100M+ acres by 2030",
        }

    def extract_system_parameters(self) -> Dict[str, float]:
        """Translate report claims into field_system parameters."""
        return {
            "soil_trend": -0.08,
            "water_retention": 0.45,
            "input_energy": 2.5,
            "output_yield": 3.0,
            "disturbance": 0.35,
            "waste_factor": 0.65,
            "nutrient_density": 0.35,
            "production_area": 200,
            "ecological_area": 0,
            "coupling_strength": 0.0,
            "ecological_amplification": 1.0,
        }


# ---------------------------
# Audit Multiple "Efficiency" Report Types
# ---------------------------

REPORT_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "precision_ag": {
        "name": "Precision Agriculture 2026",
        "parameters": {
            "soil_trend": -0.05,
            "water_retention": 0.48,
            "input_energy": 2.2,
            "output_yield": 2.8,
            "disturbance": 0.30,
            "waste_factor": 0.60,
            "nutrient_density": 0.40,
            "production_area": 200,
            "ecological_area": 0,
            "coupling_strength": 0.0,
            "ecological_amplification": 1.0,
        },
        "claims": {
            "headline": "AI-driven precision increases efficiency 280%",
            "water_savings": "45% reduction",
            "input_optimization": "30% less fertilizer",
        },
    },
    "vertical_farming": {
        "name": "Vertical Farming Breakthrough 2026",
        "parameters": {
            "soil_trend": 0.0,
            "water_retention": 0.95,
            "input_energy": 4.0,
            "output_yield": 5.0,
            "disturbance": 0.10,
            "waste_factor": 0.30,
            "nutrient_density": 0.65,
            "production_area": 10,
            "ecological_area": 0,
            "coupling_strength": 0.0,
            "ecological_amplification": 1.0,
        },
        "claims": {
            "headline": "500x yield per acre with 95% less water",
            "energy_intensity": "Not disclosed",
            "carbon_footprint": "Variable based on grid mix",
        },
    },
    "regenerative_tech": {
        "name": "Regenerative Tech Hybrid 2026",
        "parameters": {
            "soil_trend": 0.05,
            "water_retention": 0.65,
            "input_energy": 1.2,
            "output_yield": 1.5,
            "disturbance": 0.15,
            "waste_factor": 0.35,
            "nutrient_density": 0.70,
            "production_area": 100,
            "ecological_area": 100,
            "coupling_strength": 0.6,
            "ecological_amplification": 1.8,
        },
        "claims": {
            "headline": "Technology-enabled regeneration boosts efficiency 150%",
            "soil_health": "+15% organic matter",
            "profitability": "20% margin improvement",
        },
    },
}


def audit_efficiency_report(report_type: str, auditor: SixSigmaAudit) -> Dict[str, Any]:
    """Run audit on one of the efficiency-report archetypes.

    When PhysicsGuard is available, the report's headline claim is also
    screened against physical conservation laws. A CORRUPTED physics
    verdict means the claim is impossible regardless of what the Six Sigma
    audit concludes downstream.
    """
    report_data = REPORT_ARCHETYPES.get(report_type, REPORT_ARCHETYPES["precision_ag"])
    scenario = report_data["parameters"]

    audit = auditor.audit_claim(scenario, report_data["name"])
    yield_analysis = effective_yield(fill_state(scenario))

    result = {
        "report_type": report_data["name"],
        "claims": report_data["claims"],
        "audit": audit,
        "true_yield": yield_analysis,
        "thermodynamic_assessment": auditor.thermodynamic_efficiency(
            auditor.calculate_metrics(scenario)
        ),
        # Ratio of missing wild space relative to a 200-acre reference.
        "ecological_debt": 1.0 - (scenario["ecological_area"] / 200),
    }

    if _HAS_PHYSICS_GUARD:
        headline = report_data["claims"].get("headline", "")
        result["physics_verdict"] = physics_check(headline) if headline else None
    else:
        result["physics_verdict"] = None

    # Metabolic-accounting verdict. Revenue / operating-cost are scaled
    # from the scenario's energy ratio (no real currency in the input),
    # so the absolute profit numbers are not meaningful — but the
    # GREEN/AMBER/RED/BLACK signal and basin trajectory are.
    revenue_proxy = scenario.get("output_yield", 0.0) * 100.0
    cost_proxy = scenario.get("input_energy", 0.0) * 100.0
    result["metabolic_verdict"] = metabolic_check(
        revenue=revenue_proxy,
        direct_operating_cost=cost_proxy,
        regeneration_paid=0.0,
        stress=stress_from_field_scenario(scenario),
        basin_overrides=basins_from_field_scenario(scenario),
    )

    # Money-signal metrics (minsky / magnitude / sign-flips). Uses the
    # bridge's neutral default context; scenarios that want to vary the
    # six dimensions should call money_signal_bridge.money_signal_metrics
    # directly. None when the upstream package is not importable.
    result["money_signal_metrics"] = money_signal_metrics()

    return result


# ---------------------------
# First Principles Baseline
# ---------------------------

def first_principles_baseline() -> Dict[str, Any]:
    """Parameters a system would use if designed from first principles."""
    return {
        "soil_trend": 0.1,
        "water_retention": 0.85,
        "input_energy": 0.7,
        "output_yield": 1.2,
        "disturbance": 0.05,
        "waste_factor": 0.1,
        "nutrient_density": 0.9,
        "production_area": 30,
        "ecological_area": 170,
        "coupling_strength": 0.9,
        "ecological_amplification": 2.0,
    }


# ---------------------------
# Run Full Audit Suite
# ---------------------------

def run_audit_suite():
    auditor = SixSigmaAudit()
    baseline = first_principles_baseline()

    print("=" * 80)
    print("EFFICIENCY REPORT AUDIT 2026")
    print("First Principles Analysis of Industry 'Breakthrough' Claims")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 80)

    audit_results = []
    for report_type in REPORT_ARCHETYPES:
        result = audit_efficiency_report(report_type, auditor)
        audit_results.append(result)

        print(f"\n{'=' * 80}")
        print(f"REPORT: {result['report_type']}")
        print(f"{'=' * 80}")

        print("\nClaims Made:")
        for claim, value in result["claims"].items():
            print(f"  - {claim}: {value}")

        verdict = result.get("physics_verdict")
        if verdict is not None:
            print("\nPhysicsGuard Pre-Screen (headline claim):")
            print(f"  Verdict:    {verdict['verdict']}")
            print(f"  Score:      {verdict['score']:.3f}")
            print(f"  Confidence: {verdict['confidence']:.0%}")
            if verdict.get("reason"):
                print(f"  Reason:     {verdict['reason']}")
            for viol in verdict.get("violations", [])[:2]:
                print(f"  ! {viol['law']}: {viol['description']}")

        audit = result["audit"]
        print("\nAudit Results:")
        print(f"  Audit Score: {audit['audit_score']:.1%}")
        print(f"  Defect Rate: {audit['defect_rate']:.1%}")
        print(f"  True Efficiency: {audit['true_efficiency']:.1%}")
        print(f"  Claimed vs Actual Gap: {audit['efficiency_gap']:.2f}x")

        state = audit["system_state"]
        print("\nSystem State:")
        print(f"  Soil Trend: {state['soil_trend']:.2f}")
        print(f"  Water Retention: {state['water_retention']:.2f}")
        print(f"  Nutrient Density: {state['nutrient_density']:.2f}")
        print(f"  Waste Factor: {state['waste_factor']:.2f}")

        print("\nEcological Debt:")
        print(f"  Missing Wild Space: {result['ecological_debt']:.0%}")
        print(
            f"  Ecological Amplification: "
            f"{result['true_yield']['ecological_amplification_factor']:.2f}x"
        )

        print("\nThermodynamic Reality:")
        print(
            f"  True Nourishment: {result['true_yield']['total_nourishment_units']:.1f} units"
        )
        print(
            f"  Thermodynamic Efficiency: {result['thermodynamic_assessment']:.1%}"
        )

        if audit["constraints_violated"]:
            print("\nViolated Constraints:")
            for violation in audit["constraints_violated"]:
                print(f"  ! {violation}")

    # First Principles Baseline Comparison
    print("\n" + "=" * 80)
    print("FIRST PRINCIPLES BASELINE")
    print("What a system would look like if designed for regeneration")
    print("=" * 80)

    baseline_metrics = auditor.calculate_metrics(baseline)
    baseline_efficiency = auditor.thermodynamic_efficiency(baseline_metrics)
    baseline_yield = effective_yield(fill_state(baseline))

    print("\nBaseline Characteristics:")
    print(f"  Production Area: {baseline['production_area']} acres")
    print(f"  Ecological Buffer: {baseline['ecological_area']} acres")
    print(f"  Soil Trend: +{baseline['soil_trend']} (building)")
    print(f"  Nutrient Density: {baseline['nutrient_density']:.1f} (high)")
    print(f"  Waste Factor: {baseline['waste_factor']:.1f} (closed-loop)")

    print("\nBaseline Performance:")
    print(f"  True Nourishment: {baseline_yield['total_nourishment_units']:.1f} units")
    print(f"  Thermodynamic Efficiency: {baseline_efficiency:.1%}")
    print(
        f"  Ecological Amplification: "
        f"{baseline_yield['ecological_amplification_factor']:.2f}x"
    )
    print(f"  Defect Rate: {auditor.defect_rate(baseline_metrics):.1%}")

    print("\n" + "=" * 80)
    print("CONCLUSION: The Efficiency Paradox")
    print("=" * 80)

    print("\nIndustry 'Efficiency' reports consistently:")
    print("  1. Measure what's easy (yield volume, water use) not what matters "
          "(nutrient density, soil health)")
    print("  2. Assume externalities are infinite (ecological buffers, carbon sinks)")
    print("  3. Ignore thermodynamic limits (energy efficiency claims violate physics)")
    print("  4. Treat waste as 'disposed' not 'accumulated'")
    print("  5. Confuse technological substitution with systemic health")

    print("\nThe First Principles baseline shows:")
    print("  - 85% less waste through closed-loop design")
    print("  - 2.5x more true nourishment on 15% of the land")
    print("  - Positive soil trend vs degradation")
    print("  - 2x ecological amplification vs zero")

    return audit_results


if __name__ == "__main__":
    run_audit_suite()

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    print(
        """
    For any 'efficiency' report, demand:

    1. Soil Trend (delta soil over time) - Is it positive or negative?
    2. Nutrient Density (not just yield volume) - What's actually in the food?
    3. Waste Factor - Where does the waste go?
    4. Ecological Coupling - What's the buffer?
    5. True Nourishment per Acre - Not just gross yield

    Until these variables are measured, 'efficiency' is just a story told
    to maintain a system that's thermodynamically bankrupt.
    """
    )
