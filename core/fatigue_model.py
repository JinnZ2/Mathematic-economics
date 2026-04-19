#!/usr/bin/env python3
"""
Fatigue Model — Consolidated
Computes human fatigue as energy deficit across physical, cognitive,
environmental, and system-hidden-variable dimensions.

Core equations:
    total_load = (physical + cognitive) * hidden_mult * auto_mult * env_mult
    fatigue = clamp(0, 10, (total_load - energy_input) / energy_input * 10)
    hidden_mult = 1 + 0.1 * count^1.5
    auto_mult = 1 + count * (1 - reliability) * 0.5
    env_mult = 1 + max(0, (15 - temp) * 0.05) + wind * 0.02
"""

import math
from datetime import datetime


# ============================================================
# CORE SCORING FUNCTIONS
# ============================================================

def long_tail_risk(hidden_count):
    """
    Hidden variables are the logarithmic factor for long tail risk.
    Each additional hidden variable multiplies the space of possible
    failure modes -- combinatorial explosion of interaction effects.
    Returns 0-10 scale where the curve goes nonlinear fast.
    """
    if hidden_count == 0:
        return 0.0
    risk = 10 * (1 - math.exp(-0.35 * hidden_count))
    return round(min(risk, 10), 1)


def score_feedback_integrity(delay, hidden_count, gap_score):
    """
    Score how intact the feedback loop is.
    0 = completely broken, 10 = tight feedback.
    """
    score = 10.0
    delay_penalties = {
        "immediate": 0, "days": 1, "weeks": 2,
        "months": 3, "years": 5, "generational": 8
    }
    score -= delay_penalties.get(delay, 4)
    score -= min(hidden_count * 0.5, 3)
    score -= gap_score * 0.3
    return max(round(score, 1), 0)


# ============================================================
# FATIGUE MODEL
# ============================================================

class FatigueModel:
    """
    Compute real-world human fatigue as a function of:
    - Physical load
    - Cognitive load
    - Environmental stress
    - Hidden variables / system inefficiencies
    - Automation monitoring burden
    - Energy input (sleep, food, thermal comfort)

    This models what HOS regulations miss: the ACTUAL energy
    expenditure of operating in complex environments, not just
    hours awake.
    """

    def __init__(self, energy_input=100):
        self.energy_input = energy_input

    def compute_hidden_variable_multiplier(self, hidden_vars_count):
        """Hidden variables increase energy demand nonlinearly."""
        if hidden_vars_count <= 0:
            return 1.0
        return 1 + 0.1 * hidden_vars_count ** 1.5

    def compute_automation_load(self, automation_count, reliability=0.9):
        """
        Each automation system adds cognitive load proportional to
        unreliability. Unreliable automation isn't reducing load --
        it's adding monitoring burden.
        """
        return 1 + automation_count * (1 - reliability) * 0.5

    def compute_environment_multiplier(self, temp_celsius, wind_mps):
        """Cold and wind increase physical and cognitive energy expenditure."""
        temp_stress = max(0, (15 - temp_celsius) * 0.05)
        wind_stress = wind_mps * 0.02
        return 1 + temp_stress + wind_stress

    def compute(self, physical_load, cognitive_load,
                hidden_vars_count=0, automation_count=0,
                automation_reliability=0.9,
                temp_celsius=20, wind_mps=0):
        """Returns fatigue score on 0-10 scale (simple)."""
        total_load = physical_load + cognitive_load
        total_load *= self.compute_hidden_variable_multiplier(hidden_vars_count)
        total_load *= self.compute_automation_load(automation_count, automation_reliability)
        total_load *= self.compute_environment_multiplier(temp_celsius, wind_mps)

        deficit = total_load - self.energy_input
        fatigue_score = max(0, min(10, deficit / self.energy_input * 10))
        return round(fatigue_score, 1)

    def compute_fatigue_score(self, physical_load, cognitive_load,
                              hidden_vars_count=0, automation_count=0,
                              automation_reliability=0.9,
                              temp_celsius=20, wind_mps=0):
        """Returns fatigue score on 0-10 scale with full breakdown."""
        total_load = physical_load + cognitive_load

        hv_mult = self.compute_hidden_variable_multiplier(hidden_vars_count)
        auto_mult = self.compute_automation_load(automation_count, automation_reliability)
        env_mult = self.compute_environment_multiplier(temp_celsius, wind_mps)

        adjusted_load = total_load * hv_mult * auto_mult * env_mult
        deficit = adjusted_load - self.energy_input
        fatigue_score = max(0, min(10, deficit / self.energy_input * 10))

        return {
            "fatigue_score": round(fatigue_score, 1),
            "base_load": total_load,
            "adjusted_load": round(adjusted_load, 1),
            "energy_input": self.energy_input,
            "deficit": round(deficit, 1),
            "multipliers": {
                "hidden_variables": round(hv_mult, 2),
                "automation": round(auto_mult, 2),
                "environment": round(env_mult, 2),
                "combined": round(hv_mult * auto_mult * env_mult, 2)
            }
        }


# ============================================================
# HUMAN SYSTEM COLLAPSE MODEL
# ============================================================
# `HumanSystemModel` lives in `human_system_collapse_model.py` (as
# `HumanSystemCollapseModel`, with a `HumanSystemModel` alias for
# backwards compatibility). It delegates multiplier math to `FatigueModel`
# and adds the distance-to-collapse metric. Kept in a separate module to
# avoid a circular import with `FatigueModel`.


# ============================================================
# COMPOUND RISK INTEGRATION
# ============================================================

def compute_compound_risk_with_fatigue(gap_score, feedback_score, hidden_count,
                                       physical_load, cognitive_load,
                                       automation_count, automation_reliability,
                                       temp_celsius, wind_mps):
    tail_risk = long_tail_risk(hidden_count)
    baseline_risk = (gap_score * 0.5 + (10 - feedback_score) * 0.5)
    compound_risk = round(baseline_risk * (1 + tail_risk / 10), 1)
    compound_risk = min(compound_risk, 10)

    fatigue_model = FatigueModel(energy_input=100)
    fatigue_score = fatigue_model.compute(
        physical_load=physical_load,
        cognitive_load=cognitive_load,
        hidden_vars_count=hidden_count,
        automation_count=automation_count,
        automation_reliability=automation_reliability,
        temp_celsius=temp_celsius,
        wind_mps=wind_mps
    )

    return compound_risk, fatigue_score


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    # Scenario: high-hidden-variable trucking environment
    physical_load = 30
    cognitive_load = 40
    hidden_count = 7
    automation_count = 3
    automation_reliability = 0.85
    temp_celsius = -12
    wind_mps = 15

    # Simple fatigue score
    fatigue = FatigueModel(energy_input=100)
    score = fatigue.compute(
        physical_load, cognitive_load,
        hidden_count, automation_count, automation_reliability,
        temp_celsius, wind_mps
    )
    print(f"Predicted fatigue score: {score}/10")

    # Full breakdown
    breakdown = fatigue.compute_fatigue_score(
        physical_load, cognitive_load,
        hidden_count, automation_count, automation_reliability,
        temp_celsius, wind_mps
    )
    print(f"Breakdown: {breakdown}")

    # Compound risk
    compound, fatigue_s = compute_compound_risk_with_fatigue(
        gap_score=7, feedback_score=4, hidden_count=7,
        physical_load=30, cognitive_load=40,
        automation_count=3, automation_reliability=0.85,
        temp_celsius=-12, wind_mps=15
    )
    print(f"Compound System Risk: {compound}/10")
    print(f"Embodied Fatigue Score: {fatigue_s}/10")
