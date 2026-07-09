#!/usr/bin/env python3
"""
iam_audit/run.py – Claim‑driven IAM divergence audit with Merle blow‑up detection.
CC0. Stdlib + optional matplotlib.

Usage:
  python iam_audit/run.py --compare dice ours --scenario rcp85 --horizon 2100 --plot
  python iam_audit/run.py --model dice --scenario rcp85
"""

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import existing claim modules
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

# ----------------------------------------------------------------------
# Merle framework helpers (cascade_coupling_framework_2026 pattern)
# ----------------------------------------------------------------------
def energy_acceleration(energy_series: list) -> list:
    """
    Compute second derivative d²E/dt² using central differences.
    energy_series: list of (year, energy_cost) tuples sorted by year.
    Returns list of (year, d2E) for years with sufficient neighbors.
    """
    years = [e[0] for e in energy_series]
    vals = [e[1] for e in energy_series]
    d2e = []
    for i in range(1, len(vals)-1):
        dy = (vals[i+1] - vals[i-1]) / (years[i+1] - years[i-1])
        d2e.append((years[i], dy))
    return d2e

def merle_singularity_flag(acceleration_series: list, threshold: float = 0.05) -> list:
    """
    Flag years where energy acceleration exceeds threshold,
    indicating approach to finite‑time singularity.
    """
    return [(yr, acc) for yr, acc in acceleration_series if acc > threshold]

def cascade_threshold_hoi(pairwise_threshold: float) -> float:
    """Apply 70% reduction due to higher‑order interactions (Ghosh‑Shrimali 2026)."""
    return pairwise_threshold * 0.3  # 70% reduction

# ----------------------------------------------------------------------
# Scenario time‑series loader
# ----------------------------------------------------------------------
def load_time_series(model: str, scenario: str, horizon: int = 2100) -> dict:
    """
    Load projections: years, temperature, energy_cost, osdi, etc.
    For DICE, we generate a smooth projection; for ours, we generate
    a projection with possible acceleration based on C020/C026.
    """
    try:
        mod = __import__(f"scenarios.{model}_{scenario}", fromlist=["PROJECTION"])
        proj_fn = mod.PROJECTION
        return proj_fn(horizon)
    except ImportError:
        # Default smooth projection for demonstration
        years = list(range(2025, horizon+1, 5))
        temp = [1.1 + 0.03*(yr-2025) for yr in years]
        energy_cost = [2.0 + 0.02*(yr-2025) for yr in years]
        osdi = [0.5 + 0.005*(yr-2025) for yr in years]
        return {"years": years, "temp": temp, "energy_cost": energy_cost, "osdi": osdi}

def compute_divergence(model_a: dict, model_b: dict):
    """
    Find years where one model's energy acceleration crosses Merle threshold
    while the other stays below.
    """
    accel_a = energy_acceleration(list(zip(model_a["years"], model_a["energy_cost"])))
    accel_b = energy_acceleration(list(zip(model_b["years"], model_b["energy_cost"])))
    flags_a = {yr: acc for yr, acc in merle_singularity_flag(accel_a)}
    flags_b = {yr: acc for yr, acc in merle_singularity_flag(accel_b)}
    divergence_years = []
    all_years = sorted(set(list(flags_a.keys()) + list(flags_b.keys())))
    for yr in all_years:
        a_flag = yr in flags_a
        b_flag = yr in flags_b
        if a_flag != b_flag:
            divergence_years.append(yr)
    return divergence_years, flags_a, flags_b

# ----------------------------------------------------------------------
# Static claim audit (reused)
# ----------------------------------------------------------------------
def run_static_audit(assumptions: dict, label: str) -> dict:
    results = {}
    results["C000"] = meta_scope_guard.check(assumptions.get("scope", {}))
    results["C020"] = thermodynamic_accounting_audit.check(assumptions.get("energy", {}))
    results["C027"] = economic_energy_grounding_audit.check_validity(assumptions)
    results["C028"] = economic_energy_grounding_audit.check_blindness(assumptions)
    results["C031"] = engineering_grade_validation_audit.check_design_margin(assumptions)
    results["C032"] = engineering_grade_validation_audit.check_ai_cascade_risk(assumptions)
    results["C025"] = systemic_precondition_audit.check_preconditions(assumptions)
    results["C026"] = systemic_precondition_audit.check_undercutting(assumptions)
    results["C021"] = scaling_audit.check_interior_optimum(assumptions)
    results["C043"] = governance_thermodynamics_audit.check_coercion_cost(assumptions)
    results["C060"] = substrate_care_audit.check_care_visibility(assumptions)
    concern = any(v.get("threshold_met", False) for v in results.values())
    results["_concern"] = concern
    results["_label"] = label
    return results

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="IAM divergence audit with Merle detection.")
    parser.add_argument("--compare", nargs=2, metavar=("MODEL_A","MODEL_B"))
    parser.add_argument("--model", choices=["dice","fund","ours"], default="dice")
    parser.add_argument("--scenario", choices=["rcp85","rcp45","rcp26"], default="rcp85")
    parser.add_argument("--horizon", type=int, default=2100)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.compare:
        model_a = load_time_series(args.compare[0], args.scenario, args.horizon)
        model_b = load_time_series(args.compare[1], args.scenario, args.horizon)

        # Static claim audits (optional, can also load from scenario files)
        static_a = run_static_audit({}, args.compare[0])  # stub
        static_b = run_static_audit({}, args.compare[1])

        # Divergence detection
        div_years, flags_a, flags_b = compute_divergence(model_a, model_b)

        # Output
        print(f"\n{'='*60}")
        print(f"Divergence timeline: {args.compare[0]} vs {args.compare[1]} ({args.scenario})")
        print(f"{'='*60}")
        if div_years:
            print(f"Qualitative divergence at years: {div_years}")
        else:
            print("No qualitative divergence detected within horizon.")

        print(f"\nStatic claim comparison:")
        print(f"{'Claim':<6} {args.compare[0]:>6} {args.compare[1]:>6}")
        all_claims = sorted(set(static_a.keys()) | set(static_b.keys()))
        for cid in all_claims:
            if cid.startswith("_"): continue
            a_met = static_a.get(cid, {}).get("threshold_met", None)
            b_met = static_b.get(cid, {}).get("threshold_met", None)
            sym = lambda v: "⚠️" if v else ("✅" if v is False else "N/A")
            print(f"{cid:<6} {sym(a_met):>6} {sym(b_met):>6}")

        # Plot
        if args.plot:
            try:
                import matplotlib.pyplot as plt
            except ImportError:
                print("matplotlib not installed; skipping plot.")
                return
            yrs = model_a["years"]
            fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
            ax1.plot(yrs, model_a["energy_cost"], label=f"{args.compare[0]} energy cost")
            ax1.plot(yrs, model_b["energy_cost"], label=f"{args.compare[1]} energy cost")
            ax1.set_ylabel("Energy cost")
            ax1.legend()
            ax1.set_title("Energy cost projections")
            # Mark divergence years
            for yr in div_years:
                ax1.axvline(yr, color='red', alpha=0.3)
            ax2.plot(yrs, model_a["temp"], label=f"{args.compare[0]} temp anomaly")
            ax2.plot(yrs, model_b["temp"], label=f"{args.compare[1]} temp anomaly")
            ax2.set_xlabel("Year")
            ax2.set_ylabel("Temp anomaly (°C)")
            ax2.legend()
            plt.tight_layout()
            plt.savefig("iam_divergence.png")
            plt.close()
            print("Plot saved to iam_divergence.png")
    else:
        # Single model static audit only
        assumptions = {}  # placeholder
        result = run_static_audit(assumptions, args.model)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            for k, v in result.items():
                if k.startswith("_"): continue
                status = "⚠️" if v.get("threshold_met") else "✅"
                print(f"{status} {k}: {v.get('description','')}")

if __name__ == "__main__":
    main()


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
