#!/usr/bin/env python3
"""
TAF Diagnostic Engine — Institutional Friction as Heat Leak

When an institution's stated plan diverges from physical reality, the
divergence shows up as wasted time, wasted fuel, and elevated stress on
the organism doing the work. In thermodynamic terms these are heat leaks:
energy the organism spent that produced no mission output.

Core quantities:

    heat_leak_hours    = friction_minutes / 60
    prediction_error   = clamp(0, 1, (search_minutes - tolerance) / scale)
    system_efficiency  = 1 - heat_leak_hours / shift_hours

Mechanical failures compound biological fatigue, so a mechanical-failure
flag multiplies the heat leak.

Dependencies: stdlib only.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# -----------------------------
# Pure computations
# -----------------------------

def compute_heat_leak(search_minutes: float, mechanical_failure: bool = False,
                      mechanical_multiplier: float = 2.0) -> float:
    """Return heat leak measured in lost hours.

    search_minutes:        minutes of search / retry / friction activity
    mechanical_failure:    whether the friction involved a mechanical failure
    mechanical_multiplier: how much mechanical failure compounds the leak
    """
    leak_hours = max(0.0, search_minutes) / 60.0
    if mechanical_failure:
        leak_hours *= mechanical_multiplier
    return leak_hours


def compute_prediction_error(search_minutes: float,
                             tolerance_minutes: float = 5.0,
                             saturation_minutes: float = 30.0) -> float:
    """Continuous 0-1 score for how badly reality diverged from the plan.

    Below `tolerance_minutes` the error is zero (within normal noise).
    At `saturation_minutes` the error saturates at 1.0.
    """
    if search_minutes <= tolerance_minutes:
        return 0.0
    span = max(saturation_minutes - tolerance_minutes, 1e-9)
    return min(1.0, (search_minutes - tolerance_minutes) / span)


def compute_system_efficiency(heat_leak_hours: float,
                              shift_hours: float = 14.0) -> float:
    """Fraction of the shift that produced mission output.

    shift_hours defaults to 14h (common long-haul trucking on-duty window).
    """
    shift_hours = max(shift_hours, 1e-9)
    return max(0.0, 1.0 - heat_leak_hours / shift_hours)


def classify_status(prediction_error: float) -> str:
    """Label the organism state from its prediction error."""
    if prediction_error <= 0.0:
        return "Homeostasis"
    if prediction_error < 0.5:
        return "Mild Prediction Error (Irritation)"
    if prediction_error < 0.9:
        return "High Prediction Error (Frustration)"
    return "Saturated Prediction Error (Dissociation)"


def classify_root_cause(search_minutes: float,
                        mechanical_failure: bool) -> str:
    """Label the dominant failure mode."""
    if search_minutes <= 0 and not mechanical_failure:
        return "Optimal Flow"
    if mechanical_failure and search_minutes > 0:
        return "Compounded Failure (Data + Mechanical)"
    if mechanical_failure:
        return "Mechanical Failure"
    return "Data Fidelity Failure"


# -----------------------------
# Event + shift analysis
# -----------------------------

@dataclass
class HeatLeakEvent:
    label: str
    planned_miles: float
    actual_miles: float
    search_minutes: float
    mechanical_failure: bool = False


@dataclass
class HeatLeakAnalyzer:
    """TAF diagnostic engine. Analyzes friction events against a shift baseline."""
    shift_hours: float = 14.0
    tolerance_minutes: float = 5.0
    saturation_minutes: float = 30.0
    mechanical_multiplier: float = 2.0
    events: List[HeatLeakEvent] = field(default_factory=list)

    def analyze_event(self, planned_miles: float, actual_miles: float,
                      search_minutes: float, mechanical_failure: bool = False,
                      label: Optional[str] = None) -> Dict[str, object]:
        leak = compute_heat_leak(
            search_minutes, mechanical_failure, self.mechanical_multiplier)
        err = compute_prediction_error(
            search_minutes, self.tolerance_minutes, self.saturation_minutes)
        eff = compute_system_efficiency(leak, self.shift_hours)
        mile_gap = max(0.0, planned_miles - actual_miles)

        event = HeatLeakEvent(
            label=label or f"event_{len(self.events) + 1}",
            planned_miles=planned_miles,
            actual_miles=actual_miles,
            search_minutes=search_minutes,
            mechanical_failure=mechanical_failure,
        )
        self.events.append(event)

        return {
            "label":             event.label,
            "heat_leak_hours":   round(leak, 3),
            "prediction_error":  round(err, 3),
            "system_efficiency": round(eff, 4),
            "efficiency_pct":    f"{eff:.2%}",
            "mile_gap":          mile_gap,
            "mammal_status":     classify_status(err),
            "root_cause":        classify_root_cause(search_minutes, mechanical_failure),
        }

    def analyze_shift(self) -> Dict[str, object]:
        """Aggregate all logged events into a shift-level summary."""
        if not self.events:
            return {
                "event_count": 0,
                "total_heat_leak_hours": 0.0,
                "shift_efficiency": 1.0,
                "mean_prediction_error": 0.0,
            }
        total_leak = sum(
            compute_heat_leak(e.search_minutes, e.mechanical_failure,
                              self.mechanical_multiplier)
            for e in self.events
        )
        mean_err = sum(
            compute_prediction_error(e.search_minutes,
                                     self.tolerance_minutes,
                                     self.saturation_minutes)
            for e in self.events
        ) / len(self.events)
        return {
            "event_count":            len(self.events),
            "total_heat_leak_hours":  round(total_leak, 3),
            "shift_efficiency":       round(compute_system_efficiency(total_leak, self.shift_hours), 4),
            "mean_prediction_error":  round(mean_err, 3),
        }


# Backwards-compatibility alias (older code used TAF_Engine)
TAF_Engine = HeatLeakAnalyzer


# -----------------------------
# Example usage
# -----------------------------

if __name__ == "__main__":
    taf = HeatLeakAnalyzer()

    scenarios = [
        ("yard_search_30min_flat_tires",
         dict(planned_miles=500, actual_miles=0,
              search_minutes=30, mechanical_failure=True)),
        ("mild_detour",
         dict(planned_miles=500, actual_miles=470,
              search_minutes=8, mechanical_failure=False)),
        ("clean_run",
         dict(planned_miles=500, actual_miles=500,
              search_minutes=0, mechanical_failure=False)),
    ]

    for label, kw in scenarios:
        result = taf.analyze_event(label=label, **kw)
        print("---", result["label"])
        print(f"  efficiency:        {result['efficiency_pct']}")
        print(f"  heat_leak_hours:   {result['heat_leak_hours']}")
        print(f"  prediction_error:  {result['prediction_error']}")
        print(f"  mammal_status:     {result['mammal_status']}")
        print(f"  root_cause:        {result['root_cause']}")

    print("--- shift summary")
    summary = taf.analyze_shift()
    for k, v in summary.items():
        print(f"  {k}: {v}")
