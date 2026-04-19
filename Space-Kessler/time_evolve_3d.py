# -*- coding: utf-8 -*-
"""
Time-Evolving Coupled Risk Simulation
Subsystems: LEO/GEO Debris, Maneuver Load, Solar Activity
Author: Kavik / Monday-style
"""

import numpy as np
import matplotlib.pyplot as plt

# --- 1. Define subsystem states ---

debris_states = {
    "baseline_cataloged": 0.0,
    "fragmented_tracked": 1.5,
    "fragmented_untracked": 3.0
}

maneuver_states = {
    "nominal": 0.0,
    "high_frequency": 0.2,
    "extreme": 0.5
}

solar_states = {
    "quiet": 0.0,
    "moderate": 0.15,
    "high": 0.3
}

# --- 2. Function to compute conditional stress probability ---
def compute_operational_stress(debris, maneuver, solar):
    base = debris_states[debris]
    maneuver_effect = maneuver_states[maneuver]
    solar_effect = solar_states[solar]
    
    stress_prob = base + (1 + base) * maneuver_effect
    stress_prob = stress_prob + (1 + stress_prob) * solar_effect
    return min(stress_prob, 1.0)

# --- 3. Define simulation parameters ---
days = 5  # simulation horizon
time_steps_per_day = 24  # e.g., hourly steps
total_steps = days * time_steps_per_day

# Simple projected state evolution for demonstration
# (these could be dynamically updated from real inputs in practice)
debris_schedule = ["fragmented_untracked"] * total_steps
maneuver_schedule = ["high_frequency"] * total_steps
solar_schedule = ["moderate"] * total_steps

# --- 4. Simulate stress over time ---
stress_time_series = []

for t in range(total_steps):
    stress = compute_operational_stress(
        debris=debris_schedule[t],
        maneuver=maneuver_schedule[t],
        solar=solar_schedule[t]
    )
    stress_time_series.append(stress)

stress_time_series = np.array(stress_time_series)

# --- 5. Plot stress accumulation over time ---
plt.figure(figsize=(12,5))
plt.plot(np.arange(total_steps)/time_steps_per_day, stress_time_series, marker='o')
plt.title("Coupled Operational Stress Probability Over Time")
plt.xlabel("Days")
plt.ylabel("Stress Probability [0-1]")
plt.grid(True)
plt.show()

# --- 6. Optional: Export matrix for AI ingestion ---
# Can save time series as CSV for AI to ingest
import pandas as pd
df = pd.DataFrame({
    "day": np.arange(total_steps)/time_steps_per_day,
    "stress_probability": stress_time_series
})
df.to_csv("coupled_risk_time_series.csv", index=False)
