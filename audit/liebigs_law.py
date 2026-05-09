"""
liebigs_law.py

Liebig's Law of the Minimum applied to business substrate health.

Origin (von Liebig, 1840s, agronomy): plant growth is limited by the
scarcest essential nutrient, not by the average abundance. A field
with abundant N and K but deficient P will produce at the rate set
by P alone -- adding more N or K does nothing.

The law is empirically validated in agronomy, ecology (Sprengel-Liebig),
and has direct analogues in operations (Theory of Constraints) and
reliability (weakest-link). The mathematical form:

  output_rate = f(min(component_i / requirement_i))

Practical consequence: composite scores that average components are
DISHONEST when applied to substrate health. A firm with workforce=0.9,
knowledge=0.9, community=0.1 is NOT equivalent to a firm with
workforce=0.6, knowledge=0.6, community=0.7 even though both have
the same arithmetic mean (0.633). The first firm's community substrate
is the binding constraint and its actual output is governed by that 0.1.

This module provides the min-based audit alongside the existing weighted
mean from business_resilience_framework.substrate_health_audit, and shows
the gap when they disagree.

License: CC0 1.0 Universal
"""

from typing import Dict, List, Tuple

from business_resilience_framework import (
    BusinessState,
    reference_profiles,
    substrate_health_audit,
)


# -----------------------------------------------------------------------------
# CORE LIEBIG PRIMITIVES
# -----------------------------------------------------------------------------

def liebig_score(components: Dict[str, float]) -> Tuple[float, str]:
    """
    Liebig minimum: output is limited by the scarcest component.
    Returns (limiting_value, limiting_component_name).
    """
    if not components:
        raise ValueError("liebig_score requires at least one component")
    name, value = min(components.items(), key=lambda kv: kv[1])
    return value, name


def mean_score(components: Dict[str, float]) -> float:
    if not components:
        return 0.0
    return sum(components.values()) / len(components)


def liebig_vs_mean_gap(components: Dict[str, float]) -> Dict[str, float]:
    """
    Quantifies how much the weighted-mean view overstates substrate health
    relative to the Liebig minimum view. Large gap => the mean is hiding
    a binding deficiency.
    """
    minv, lim = liebig_score(components)
    m = mean_score(components)
    return {
        "mean": round(m, 3),
        "liebig_min": round(minv, 3),
        "limiting_component": lim,
        "gap": round(m - minv, 3),
        "gap_warns_hidden_deficiency": (m - minv) > 0.20,
    }


# -----------------------------------------------------------------------------
# APPLIED TO BusinessState SUBSTRATE HEALTH
# -----------------------------------------------------------------------------

def liebig_substrate_audit(b: BusinessState) -> dict:
    """
    Replays substrate_health_audit's three subscores (workforce, knowledge,
    community) under Liebig's law: composite = min, not weighted mean.
    Returns both views side-by-side so the gap is visible.
    """
    weighted = substrate_health_audit(b)
    components = {
        "workforce": weighted["workforce"],
        "knowledge": weighted["knowledge"],
        "community": weighted["community"],
    }
    minv, lim = liebig_score(components)
    gap = liebig_vs_mean_gap(components)

    return {
        "components": components,
        "weighted_mean_composite": weighted["composite"],
        "weighted_mean_rating": weighted["rating"],
        "liebig_composite": round(minv, 3),
        "liebig_limiting_component": lim,
        "liebig_rating": (
            "healthy"      if minv > 0.65 else
            "at_risk"      if minv > 0.40 else
            "degrading"    if minv > 0.20 else
            "collapsing"
        ),
        "gap": gap["gap"],
        "hidden_deficiency_warning": gap["gap_warns_hidden_deficiency"],
        "interpretation": (
            "Substrate output is governed by the limiting component. "
            "The weighted-mean view OVERSTATES health because it lets "
            "abundant components compensate for the deficient one -- but "
            "Liebig's law says they can't."
        ),
    }


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== LIEBIG vs MEAN: WHEN DO THEY DISAGREE? ===")
    cases = [
        ("balanced (0.6/0.6/0.7)",   {"a": 0.6, "b": 0.6, "c": 0.7}),
        ("hidden gap (0.9/0.9/0.1)", {"a": 0.9, "b": 0.9, "c": 0.1}),
        ("deeply uniform (0.5/0.5/0.5)", {"a": 0.5, "b": 0.5, "c": 0.5}),
        ("one critical hole (0.8/0.05/0.85)", {"a": 0.8, "b": 0.05, "c": 0.85}),
    ]
    for name, comps in cases:
        rep = liebig_vs_mean_gap(comps)
        warn = "  <-- HIDDEN DEFICIENCY" if rep["gap_warns_hidden_deficiency"] else ""
        print(f"  {name:36s}  mean={rep['mean']:.3f}  liebig={rep['liebig_min']:.3f}  "
              f"limiting={rep['limiting_component']}  gap={rep['gap']:+.3f}{warn}")

    print("\n=== APPLIED TO REFERENCE BUSINESSES ===")
    for b in reference_profiles():
        rep = liebig_substrate_audit(b)
        print(f"\n  {b.name}")
        print(f"    components:                {rep['components']}")
        print(f"    weighted-mean rating:      {rep['weighted_mean_rating']:12s}  composite={rep['weighted_mean_composite']:.3f}")
        print(f"    liebig rating:             {rep['liebig_rating']:12s}  composite={rep['liebig_composite']:.3f}")
        print(f"    limiting component:        {rep['liebig_limiting_component']}")
        if rep["hidden_deficiency_warning"]:
            print(f"    >>> HIDDEN DEFICIENCY: weighted mean overstates by {rep['gap']:.3f}")

    print("\n=== PRINCIPLE ===")
    print("  Liebig's Law: output is set by the scarcest substrate, not")
    print("  the average. Weighted-mean composites let abundant axes mask")
    print("  deficient ones; min-based audits expose the binding constraint.")
    print("  When the gap > 0.20, the mean is lying.")
