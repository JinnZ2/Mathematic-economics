# -*- coding: utf-8 -*-
"""
Coupled Risk Possibility Matrix for LEO/GEO debris, Maneuver Load, and Solar Activity
Author: Kavik / Monday-style
"""

import numpy as np
import itertools

# --- 1. Define states for each subsystem ---

# Debris stategy
debris_states = {
    "baseline_cataloged": 0.0,      # base probability multiplier
    "fragmented_tracked": 1.5,      # 50% increase in collision probability
    "fragmented_untracked": 3.0     # 200% increase in collision probability
}

# Maneuver load state
maneuver_states = {
    "nominal": 0.0,                  # base stress
    "high_frequency": 0.2,           # 20% operational stress probability
    "extreme": 0.5                   # 50% operational stress probability
}

# Solar activity state
solar_states = {
    "quiet": 0.0,                     # no additional effect
    "moderate": 0.15,                  # 15% increase in uncertainty / stress
    "high": 0.3                        # 30% increase
}

# --- 2. Define function to compute conditional stress probability ---
def compute_operational_stress(debris, maneuver, solar):
    """
    Calculate combined probability of operational stress given subsystem states.
    Multiplicative model: base probability (from debris) multiplied by
    maneuver load and solar multipliers.
    """
    base = debris_states[debris]
    maneuver_effect = maneuver_states[maneuver]
    solar_effect = solar_states[solar]
    
    # Conditional coupling: base + (1 + base) * maneuver + (1 + base + maneuver) * solar
    # This approximates conditional dependency without overcomplication
    stress_prob = base + (1 + base) * maneuver_effect
    stress_prob = stress_prob + (1 + stress_prob) * solar_effect
    
    # Cap at 1.0
    return min(stress_prob, 1.0)

# --- 3. Generate possibility matrix for all combinations ---
subsystems = [debris_states.keys(), maneuver_states.keys(), solar_states.keys()]
matrix = {}

for combo in itertools.product(*subsystems):
    debris, maneuver, solar = combo
    key = f"{debris} | {maneuver} | {solar}"
    matrix[key] = compute_operational_stress(debris, maneuver, solar)

# --- 4. Display matrix ---
for k, v in matrix.items():
    print(f"{k}: {v:.2f}")
