# system_audit.py
# Six Sigma audit framework for industrial agriculture claims
# Exposes the gap between claimed metrics and systemic reality

from field_system import report, constraints, regen_capacity
from typing import Dict, Any, List
import math

# ---------------------------
# Six Sigma Audit Framework
# ---------------------------

class SixSigmaAudit:
    """Audit industrial claims against systemic constraints."""
    
    def __init__(self):
        self.tolerances = {
            "soil_trend": {"target": 0.0, "type": "minimum", "weight": 1.5},
            "water_retention": {"target": 0.4, "type": "minimum", "weight": 1.2},
            "nutrient_density": {"target": 0.7, "type": "minimum", "weight": 1.3},
            "waste_factor": {"target": 0.3, "type": "maximum", "weight": 1.4},
            "energy_ratio": {"target": 1.0, "type": "minimum", "weight": 1.1},
            "regen_capacity": {"target": 0.8, "type": "minimum", "weight": 1.0}
        }
        
    def calculate_metrics(self, state: Dict[str, float]) -> Dict[str, Any]:
        """Calculate process capability metrics."""
        # Add derived metrics
        metrics = state.copy()
        metrics["energy_ratio"] = (
            state["output_yield"] / state["input_energy"] 
            if state["input_energy"] > 0 else 0
        )
        metrics["regen_capacity"] = regen_capacity(state)
        
        return metrics
    
    def defect_rate(self, metrics: Dict[str, float]) -> float:
        """Calculate defect rate across tolerances."""
        defects = 0
        total = 0
        
        for key, spec in self.tolerances.items():
            if key in metrics:
                total += 1
                if spec["type"] == "minimum" and metrics[key] < spec["target"]:
                    defects += 1
                elif spec["type"] == "maximum" and metrics[key] > spec["target"]:
                    defects += 1
                    
        return defects / total if total > 0 else 1.0
    
    def process_capability(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate process capability indices (Cp, Cpk analog).
        Higher is better. < 1 indicates process not meeting specs.
        """
        cpk_values = {}
        
        for key, spec in self.tolerances.items():
            if key in metrics:
                # Simplified capability using distance from target
                if spec["type"] == "minimum":
                    # How far above minimum (normalized)
                    margin = max(0, metrics[key] - spec["target"])
                    cpk = margin / (abs(spec["target"]) + 0.1) + 1
                else:  # maximum
                    margin = max(0, spec["target"] - metrics[key])
                    cpk = margin / (abs(spec["target"]) + 0.1) + 1
                    
                cpk_values[key] = min(2.0, cpk)  # Cap at 2.0 for readability
                
        return cpk_values
    
    def thermodynamic_efficiency(self, metrics: Dict[str, float]) -> float:
        """
        Calculate true thermodynamic efficiency accounting for waste.
        Industrial metrics ignore waste heat/entropy.
        """
        output_energy = metrics["output_yield"] * metrics["nutrient_density"]
        input_energy = metrics["input_energy"]
        
        if input_energy <= 0:
            return 0
            
        # Account for waste and degradation
        waste_penalty = 1 - metrics["waste_factor"]
        regen_penalty = metrics["regen_capacity"] / 1.5  # Normalized
        
        true_efficiency = (output_energy / input_energy) * waste_penalty * regen_penalty
        
        return max(0, min(1.0, true_efficiency))
    
    def audit_claim(self, claim_state: Dict[str, float], claim_text: str) -> Dict[str, Any]:
        """Full audit of an industrial claim."""
        # Get baseline report
        field_report = report(claim_state)
        metrics = self.calculate_metrics(claim_state)
        
        # Calculate audit metrics
        def_rate = self.defect_rate(metrics)
        cpk = self.process_capability(metrics)
        true_efficiency = self.thermodynamic_efficiency(metrics)
        
        # Calculate claimed vs actual
        claimed_efficiency = (
            claim_state["output_yield"] / claim_state["input_energy"]
            if claim_state["input_energy"] > 0 else 0
        )
        
        efficiency_gap = claimed_efficiency - true_efficiency
        yield_gap = claim_state["output_yield"] - metrics["regen_capacity"]
        
        # Determine if claim is "plausible"
        is_plausible = (
            def_rate < 0.3 and  # Fewer than 30% defects
            true_efficiency > 0.3 and  # Thermodynamically plausible
            all(v > 0.8 for v in cpk.values())  # Process capable
        )
        
        return {
            "claim_text": claim_text,
            "audit_score": 1.0 - def_rate,  # Higher is better
            "defect_rate": def_rate,
            "process_capability": cpk,
            "true_efficiency": true_efficiency,
            "claimed_efficiency": claimed_efficiency,
            "efficiency_gap": efficiency_gap,
            "yield_gap": yield_gap,
            "is_plausible": is_plausible,
            "constraints_violated": [k for k, v in field_report["drift"].items() if v],
            "system_state": field_report["state"],
            "suggestions": field_report["suggestions"]["actions"]
        }


# ---------------------------
# Industrial Claim Scenarios
# ---------------------------

def create_industrial_claim(
    productivity_gain: float = 2.7,  # 270%
    soil_trend: float = -0.05,  # Slight depletion
    waste_factor: float = 0.7,  # High waste
    nutrient_density: float = 0.4,  # Low quality
    ecological_area: float = 0  # No wild space
) -> Dict[str, float]:
    """Create an industrial agriculture claim scenario."""
    return {
        "soil_trend": soil_trend,
        "water_retention": 0.5,  # Marginal
        "input_energy": 2.0,  # High inputs
        "output_yield": productivity_gain,  # Claimed productivity
        "disturbance": 0.25,  # High disturbance
        "waste_factor": waste_factor,
        "nutrient_density": nutrient_density,
        "production_area": 200,
        "ecological_area": ecological_area,
        "coupling_strength": 0.0,
        "ecological_amplification": 1.0
    }


def create_regenerative_alternative(
    soil_trend: float = 0.1,
    nutrient_density: float = 0.9,
    waste_factor: float = 0.1,
    coupling_strength: float = 0.9,
    production_area: float = 30,
    ecological_area: float = 170
) -> Dict[str, float]:
    """Create a regenerative stewardship scenario."""
    return {
        "soil_trend": soil_trend,
        "water_retention": 0.85,  # High retention
        "input_energy": 0.8,  # Low external inputs
        "output_yield": 1.2,  # Moderate yield
        "disturbance": 0.08,  # Low disturbance
        "waste_factor": waste_factor,
        "nutrient_density": nutrient_density,
        "production_area": production_area,
        "ecological_area": ecological_area,
        "coupling_strength": coupling_strength,
        "ecological_amplification": 2.0
    }


# ---------------------------
# Run the Audit
# ---------------------------

if __name__ == "__main__":
    auditor = SixSigmaAudit()
    
    # Test claim: "AI-managed precision ag will increase productivity 270%"
    industrial_claim_text = (
        "AI-managed precision agriculture will increase productivity 270% by 2030 "
        "while keeping emissions in check through optimized resource management."
    )
    
    industrial_scenario = create_industrial_claim()
    regenerative_scenario = create_regenerative_alternative()
    
    print("=" * 80)
    print("SIX SIGMA AUDIT: Industrial Agriculture Claim")
    print("=" * 80)
    
    audit_result = auditor.audit_claim(industrial_scenario, industrial_claim_text)
    
    print(f"\nClaim: {audit_result['claim_text']}")
    print(f"\nAudit Score: {audit_result['audit_score']:.2%}")
    print(f"Defect Rate: {audit_result['defect_rate']:.2%}")
    print(f"Is Plausible: {audit_result['is_plausible']}")
    
    print(f"\nClaimed Efficiency: {audit_result['claimed_efficiency']:.2f}")
    print(f"True Efficiency: {audit_result['true_efficiency']:.2%}")
    print(f"Efficiency Gap: {audit_result['efficiency_gap']:.2f}")
    print(f"Yield Gap: {audit_result['yield_gap']:.2f} units")
    
    print(f"\nConstraint Violations: {audit_result['constraints_violated']}")
    print(f"\nSix Sigma Diagnostics:")
    for metric, cpk in audit_result['process_capability'].items():
        status = "✓" if cpk >= 1.0 else "⚠"
        print(f"  {status} {metric}: Cpk = {cpk:.2f}")
    
    print(f"\nPrescribed Actions:")
    for action in audit_result['suggestions'][:3]:
        print(f"  • {action}")
    
    # Compare with regenerative alternative
    print("\n" + "=" * 80)
    print("COMPARISON: Regenerative Stewardship Alternative")
    print("=" * 80)
    
    regen_report = report(regenerative_scenario)
    regen_metrics = auditor.calculate_metrics(regenerative_scenario)
    regen_defect = auditor.defect_rate(regen_metrics)
    regen_efficiency = auditor.thermodynamic_efficiency(regen_metrics)
    
    print(f"\nAudit Score: {(1 - regen_defect):.2%}")
    print(f"Defect Rate: {regen_defect:.2%}")
    print(f"True Efficiency: {regen_efficiency:.2%}")
    print(f"Total Nourishment: {regen_report['yield_analysis']['total_nourishment_units']:.1f} units")
    print(f"Ecological Amplification: {regen_report['yield_analysis']['ecological_amplification_factor']:.2f}x")
    
    print("\n" + "=" * 80)
    print("SUMMARY: The Industrial Gap")
    print("=" * 80)
    
    industrial_total = audit_result['system_state']['output_yield'] * 200
    regenerative_total = regen_report['yield_analysis']['total_nourishment_units']
    
    print(f"\nIndustrial 'Productivity' (200 acres): {industrial_total:.0f} gross units")
    print(f"Regenerative True Nourishment (30 acres): {regenerative_total:.1f} net units")
    print(f"Efficiency Ratio: {regenerative_total / industrial_total:.2f}x more nourishment on 15% of land")
    print(f"Waste Gap: {(audit_result['system_state']['waste_factor'] - regen_metrics['waste_factor']) * 100:.0f}% less waste")
    print(f"Soil Trend: {regenerative_scenario['soil_trend'] - industrial_scenario['soil_trend']:.2f} improvement")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    if not audit_result['is_plausible']:
        print("\n⚠ The industrial claim FAILS the Six Sigma audit.")
        print("  • Missing variables: soil entropy, nutrient density, waste loops, ecological coupling")
        print("  • 'Efficiency' ignores thermodynamic reality and externalized costs")
        print("  • Defect rate exceeds acceptable thresholds for systemic health")
    else:
        print("\n✓ Claim passes basic plausibility checks.")
    
    print("\nThe '270% productivity' is a ghost metric—it counts extraction as value")
    print("while ignoring the soil carbon loss, water depletion, and nutrient bankruptcy")
    print("that make that 'productivity' possible. This is not efficiency; it's entropy.")
