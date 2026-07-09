# iam_audit/run.py
#!/usr/bin/env python3
"""
iam_audit/run.py – Claim‑driven IAM divergence audit.
CC0. Stdlib only. Imports claim modules from automation_scope_audit.

Usage:
  python iam_audit/run.py --model dice --scenario rcp85
  python iam_audit/run.py --model ours --scenario rcp85
  python iam_audit/run.py --compare dice ours --scenario rcp85  # side‑by‑side
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path so we can import automation_scope_audit modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from automation_scope_audit.modules import (
    thermodynamic_accounting_audit,
    economic_energy_grounding_audit,
    engineering_grade_validation_audit,
    systemic_precondition_audit,
    scaling_audit,
    governance_thermodynamics_audit,
    substrate_care_audit,
    meta_scope_guard,
)

def load_scenario(model: str, scenario: str) -> dict:
    """Load a model scenario from scenarios/ directory."""
    try:
        mod = __import__(f"scenarios.{model}_{scenario}", fromlist=["ASSUMPTIONS"])
        return mod.ASSUMPTIONS
    except ImportError:
        print(f"Scenario not found: {model}_{scenario}")
        return {}

def run_audit(assumptions: dict, label: str) -> dict:
    """Run all applicable claim checks against the given assumptions."""
    results = {}
    # C000 scope guard
    results["C000"] = meta_scope_guard.check(assumptions.get("scope", {}))

    # Thermodynamic accounting
    results["C020"] = thermodynamic_accounting_audit.check(assumptions.get("energy", {}))

    # Energy grounding
    results["C027"] = economic_energy_grounding_audit.check_validity(assumptions)
    results["C028"] = economic_energy_grounding_audit.check_blindness(assumptions)

    # Engineering grade
    results["C031"] = engineering_grade_validation_audit.check_design_margin(assumptions)
    results["C032"] = engineering_grade_validation_audit.check_ai_cascade_risk(assumptions)

    # Systemic preconditions
    results["C025"] = systemic_precondition_audit.check_preconditions(assumptions)
    results["C026"] = systemic_precondition_audit.check_undercutting(assumptions)

    # Scaling
    results["C021"] = scaling_audit.check_interior_optimum(assumptions)

    # Governance
    results["C043"] = governance_thermodynamics_audit.check_coercion_cost(assumptions)

    # Substrate care
    results["C060"] = substrate_care_audit.check_care_visibility(assumptions)

    # Mark overall concern
    concern = any(v.get("threshold_met", False) for v in results.values())
    results["_concern"] = concern
    results["_label"] = label
    return results

def compare_models(model_a: str, model_b: str, scenario: str):
    a = load_scenario(model_a, scenario)
    b = load_scenario(model_b, scenario)
    res_a = run_audit(a, model_a)
    res_b = run_audit(b, model_b)
    # Print side-by-side
    print(f"{'Claim':<6} {model_a:>6} {model_b:>6}")
    for claim_id in sorted(set(res_a.keys()) | set(res_b.keys())):
        if claim_id.startswith("_"):
            continue
        a_met = res_a.get(claim_id, {}).get("threshold_met", None)
        b_met = res_b.get(claim_id, {}).get("threshold_met", None)
        def sym(v):
            if v is True: return "⚠️"
            if v is False: return "✅"
            return "N/A"
        print(f"{claim_id:<6} {sym(a_met):>6} {sym(b_met):>6}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["dice","fund","ours"], default="dice")
    parser.add_argument("--scenario", choices=["rcp85","rcp45","rcp26"], default="rcp85")
    parser.add_argument("--compare", nargs=2, metavar=("MODEL_A","MODEL_B"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.compare:
        compare_models(args.compare[0], args.compare[1], args.scenario)
    else:
        assumptions = load_scenario(args.model, args.scenario)
        result = run_audit(assumptions, args.model)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for k, v in result.items():
                if k.startswith("_"): continue
                status = "⚠️" if v.get("threshold_met") else "✅"
                print(f"{status} {k}: {v.get('description','')}")

if __name__ == "__main__":
    main()
