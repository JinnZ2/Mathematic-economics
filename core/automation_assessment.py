#!/usr/bin/env python3
"""
Thermodynamic Automation Assessment Engine v2
Maps hidden variables, human energy, and automation as dynamic entropy.
Calculates fatigue, collapse risk, and system stress numerically.
"""

import math
from datetime import datetime

# -----------------------------
# Utility functions
# -----------------------------
def clear():
    print("\n" * 2)

def header(title="THERMODYNAMIC AUTOMATION ASSESSMENT"):
    print("=" * 60)
    print(f"  {title}")
    print("  Modeling humans, hidden variables, and automation entropy")
    print("=" * 60)

def get_input(prompt, required=True, allow_list=False):
    """Get user input, optionally as a list"""
    while True:
        val = input(f"\n  {prompt}\n  > ").strip()
        if val or not required:
            if allow_list and val:
                return [v.strip() for v in val.split(",") if v.strip()]
            return val if val else "Unknown / Not stated"
        print("  (Required field - press enter to mark as Unknown)")

# -----------------------------
# Core functions
# -----------------------------
def calculate_hidden_entropy(hidden_vars):
    """
    Maps hidden variables to a numeric entropy load (0-10 per variable)
    Uses log scaling for combinatorial effects.
    """
    count = len(hidden_vars) if isinstance(hidden_vars, list) else 0
    if count == 0:
        return 0.0
    return round(10 * (1 - math.exp(-0.35 * count)), 1)

def automation_entropy(automation_modules, hidden_vars, environment_factor=1.0):
    """
    Automation can reduce load (negative) or increase it (positive) depending on complexity and hidden variables.
    environment_factor: multiplier for environmental stress (1.0 = normal, >1 = extreme)
    """
    if not automation_modules:
        return 0.0
    base_entropy = 0
    for module in automation_modules:
        # default assumption: each module reduces load by 0-3, but edge complexity flips it
        # User provides 'impact' for each module: "helpful" or "complex"
        impact = module.get("impact", "helpful")
        if impact == "helpful":
            delta = -2  # reduces load
        else:
            delta = 3 * environment_factor  # adds entropy under stress
        base_entropy += delta
    return base_entropy

def total_human_load(base_human_energy, hidden_vars, automation_modules, environment_factor=1.0):
    hidden_load = calculate_hidden_entropy(hidden_vars)
    auto_load = automation_entropy(automation_modules, hidden_vars, environment_factor)
    net_load = base_human_energy + hidden_load + auto_load
    return max(net_load, 0)

def fatigue_score(net_load, energy_capacity=10.0):
    """
    Maps net human load to fatigue score (0=fully rested, 10=critical overload)
    """
    score = (net_load / energy_capacity) * 10
    return min(round(score, 1), 10)

def collapse_risk(fatigue, hidden_entropy):
    """
    Maps fatigue + hidden variable load to a 0-10 collapse risk
    """
    baseline = fatigue * 0.5 + hidden_entropy * 0.5
    return min(round(baseline, 1), 10)


# -----------------------------
# Programmatic assessment
# -----------------------------
def assess(base_human_energy, hidden_vars=None, automation_modules=None,
           environment_factor=1.0):
    """
    Programmatic entry point. Takes data directly and returns a dict.
    Mirrors run_example() but without any stdin interaction.

    base_human_energy:     float, 0-10 scale
    hidden_vars:           list[str] of hidden variable names
    automation_modules:    list[dict] with keys 'name' (str), 'impact' ('helpful'|'complex')
    environment_factor:    float, 1.0 = normal, >1 = extreme stress

    Returns dict with counts, net_load, fatigue_score, collapse_risk.
    """
    hidden_vars = hidden_vars or []
    automation_modules = automation_modules or []

    hidden_entropy = calculate_hidden_entropy(hidden_vars)
    net_load = total_human_load(base_human_energy, hidden_vars,
                                automation_modules, environment_factor)
    fatigue = fatigue_score(net_load)
    risk = collapse_risk(fatigue, hidden_entropy)

    return {
        "hidden_var_count":   len(hidden_vars),
        "hidden_vars":        list(hidden_vars),
        "automation_modules": list(automation_modules),
        "environment_factor": environment_factor,
        "hidden_entropy":     hidden_entropy,
        "net_load":           net_load,
        "fatigue_score":      fatigue,
        "collapse_risk":      risk,
    }


# -----------------------------
# Interactive run (stdin-driven)
# -----------------------------
def run_example():
    header()

    # Base human energy (arbitrary 0-10 scale)
    base_human_energy = float(get_input("Base human energy for shift (0-10):"))

    # Hidden variables
    hidden_vars = get_input(
        "List hidden variables to account for (comma-separated):", allow_list=True
    )

    # Automation modules
    automation_modules = []
    while True:
        add_auto = get_input("Add automation module? (y/n):", required=True)
        if add_auto.lower() != "y":
            break
        name = get_input("Module name:")
        impact = get_input("Impact on load? (helpful / complex):")
        automation_modules.append({"name": name, "impact": impact})

    # Environment factor (1=normal, >1=extreme)
    environment_factor = float(get_input("Environment stress multiplier (1=normal):"))

    # Compute using the programmatic core
    result = assess(
        base_human_energy=base_human_energy,
        hidden_vars=hidden_vars if isinstance(hidden_vars, list) else [],
        automation_modules=automation_modules,
        environment_factor=environment_factor,
    )

    # Report
    print("\n" + "-"*60)
    print("THERMODYNAMIC AUTOMATION REPORT")
    print("-"*60)
    print(f"Hidden Variables Count: {result['hidden_var_count']}")
    for v in result['hidden_vars']:
        print(f"  - {v}")
    print(f"Net Human Load: {result['net_load']}/10")
    print(f"Estimated Fatigue Score: {result['fatigue_score']}/10")
    print(f"Estimated Collapse Risk: {result['collapse_risk']}/10")
    print("-"*60)

if __name__ == "__main__":
    run_example()
