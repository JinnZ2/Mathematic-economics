"""
theory_of_constraints.py

Goldratt's Theory of Constraints applied to business process flow.
Provides the math-grounded answer to "which improvement first?"

Foundation (LP duality / network flow):
  System throughput = min(capacity_i)  across all stations
  Improvements at non-bottleneck stations do not change system throughput
  Once the bottleneck is elevated, the constraint MOVES -- the new
  bottleneck becomes the next focus

The five focusing steps (Goldratt):
  1. Identify the constraint
  2. Exploit it (maximize throughput at the bottleneck before any spend)
  3. Subordinate everything else (don't overproduce upstream)
  4. Elevate it (invest to raise its capacity)
  5. Repeat (the constraint will move)

This complements business_resilience_framework.transition_pathway:
that module lists Phase 1 actions; ToC tells you which ONE matters
right now and why the others are wasted spend until the constraint shifts.

License: CC0 1.0 Universal
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# -----------------------------------------------------------------------------
# PROCESS STATION
# -----------------------------------------------------------------------------

@dataclass
class ProcessStation:
    name: str
    capacity_per_period: float    # throughput limit if it were the only constraint
    current_load_pct: float = 0.0  # 0..1, fraction of capacity in use
    elevation_cost: float = 0.0    # cost to add 1 unit of capacity at this station


@dataclass
class ImprovementOption:
    station_name: str
    capacity_gain: float    # added capacity per period
    cost: float             # one-time cost to implement


# -----------------------------------------------------------------------------
# CORE TOC PRIMITIVES
# -----------------------------------------------------------------------------

def identify_constraint(stations: List[ProcessStation]) -> ProcessStation:
    """Step 1: the bottleneck is the station with lowest capacity."""
    if not stations:
        raise ValueError("need at least one station")
    return min(stations, key=lambda s: s.capacity_per_period)


def system_throughput(stations: List[ProcessStation]) -> float:
    """The system can only move as fast as its slowest station."""
    return min(s.capacity_per_period for s in stations)


def utilization_report(stations: List[ProcessStation]) -> Dict[str, dict]:
    """
    Step 3 diagnostic: shows which stations are over-capacity relative
    to the bottleneck. Anything above the bottleneck's capacity is wasted
    work-in-progress / inventory build-up if it's actually being run.
    """
    throughput = system_throughput(stations)
    out = {}
    for s in stations:
        excess = max(0.0, s.capacity_per_period - throughput)
        out[s.name] = {
            "capacity": s.capacity_per_period,
            "effective_throughput": throughput,
            "excess_capacity": round(excess, 3),
            "wasted_potential_pct": round(excess / s.capacity_per_period, 3) if s.capacity_per_period > 0 else 0.0,
            "is_bottleneck": s.capacity_per_period == throughput,
        }
    return out


# -----------------------------------------------------------------------------
# IMPROVEMENT PRIORITIZATION
# -----------------------------------------------------------------------------

def improvement_priority(
    stations: List[ProcessStation],
    options: List[ImprovementOption],
) -> List[dict]:
    """
    Step 4 diagnostic: rank improvement options by throughput gain per
    dollar. Improvements at non-bottleneck stations score zero (or
    near-zero, accounting for the post-elevation case where the constraint
    moves to a new station).
    """
    baseline = system_throughput(stations)
    by_name = {s.name: s for s in stations}

    ranked = []
    for opt in options:
        if opt.station_name not in by_name:
            continue
        new_stations = [
            ProcessStation(
                s.name,
                s.capacity_per_period + (opt.capacity_gain if s.name == opt.station_name else 0.0),
                s.current_load_pct,
                s.elevation_cost,
            )
            for s in stations
        ]
        new_throughput = system_throughput(new_stations)
        gain = new_throughput - baseline
        ranked.append({
            "station": opt.station_name,
            "capacity_gain": opt.capacity_gain,
            "cost": opt.cost,
            "throughput_gain": round(gain, 3),
            "throughput_per_dollar": round(gain / opt.cost, 6) if opt.cost > 0 else 0.0,
            "wasted_spend": gain == 0.0,
        })

    ranked.sort(key=lambda r: r["throughput_per_dollar"], reverse=True)
    return ranked


def simulate_elevation(
    stations: List[ProcessStation],
    station_name: str,
    new_capacity: float,
) -> dict:
    """
    Step 5 diagnostic: elevate one station's capacity and show:
      - the new system throughput
      - whether the constraint moved
      - the new bottleneck
    """
    before_bottleneck = identify_constraint(stations)
    before_throughput = system_throughput(stations)

    new_stations = [
        ProcessStation(s.name,
                       new_capacity if s.name == station_name else s.capacity_per_period,
                       s.current_load_pct,
                       s.elevation_cost)
        for s in stations
    ]
    after_bottleneck = identify_constraint(new_stations)
    after_throughput = system_throughput(new_stations)

    return {
        "before": {
            "bottleneck": before_bottleneck.name,
            "throughput": before_throughput,
        },
        "after": {
            "bottleneck": after_bottleneck.name,
            "throughput": after_throughput,
        },
        "constraint_moved": before_bottleneck.name != after_bottleneck.name,
        "throughput_gain": round(after_throughput - before_throughput, 3),
    }


# -----------------------------------------------------------------------------
# COUPLING: rank SPOFs from cascade_vulnerability_scan by ToC priority
# -----------------------------------------------------------------------------

def rank_spofs_by_toc(spofs: List[dict]) -> List[dict]:
    """
    Takes the `single_points_of_failure` list from
    business_resilience_framework.cascade_vulnerability_scan and ranks
    by their cascade weight (proxy for capacity to absorb shock).
    The highest-weight SPOF is the binding constraint -- address it
    before any other Phase 1 action.

    This is the bridge from cascade_vulnerability_scan (qualitative SPOF
    list) to ToC sequencing (which one first).
    """
    return sorted(spofs, key=lambda s: s.get("weight", 0.0), reverse=True)


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    line = [
        ProcessStation("raw_material_intake", capacity_per_period=120, elevation_cost=10000),
        ProcessStation("machining",           capacity_per_period=80,  elevation_cost=50000),
        ProcessStation("heat_treatment",      capacity_per_period=60,  elevation_cost=40000),
        ProcessStation("assembly",            capacity_per_period=90,  elevation_cost=15000),
        ProcessStation("quality_inspection",  capacity_per_period=110, elevation_cost=8000),
    ]

    print("\n=== STEP 1: IDENTIFY THE CONSTRAINT ===")
    bn = identify_constraint(line)
    print(f"  bottleneck: {bn.name} at capacity {bn.capacity_per_period}")
    print(f"  system throughput: {system_throughput(line)} per period")

    print("\n=== STEP 3: UTILIZATION (excess capacity above bottleneck = wasted) ===")
    for name, info in utilization_report(line).items():
        marker = "  <-- BOTTLENECK" if info["is_bottleneck"] else ""
        print(f"  {name:22s}  cap={info['capacity']:6.1f}  excess={info['excess_capacity']:6.1f}  "
              f"wasted_pct={info['wasted_potential_pct']*100:5.1f}%{marker}")

    print("\n=== STEP 4: IMPROVEMENT PRIORITY ===")
    options = [
        ImprovementOption("raw_material_intake", capacity_gain=20, cost=10000),
        ImprovementOption("machining",           capacity_gain=20, cost=50000),
        ImprovementOption("heat_treatment",      capacity_gain=20, cost=40000),
        ImprovementOption("assembly",            capacity_gain=20, cost=15000),
        ImprovementOption("quality_inspection",  capacity_gain=20, cost=8000),
    ]
    for r in improvement_priority(line, options):
        flag = "  WASTED" if r["wasted_spend"] else ""
        print(f"  {r['station']:22s}  gain={r['throughput_gain']:5.1f}  "
              f"cost=${r['cost']:>7}  per_dollar={r['throughput_per_dollar']:.6f}{flag}")

    print("\n=== STEP 5: ELEVATE HEAT_TREATMENT BY 30 UNITS ===")
    rep = simulate_elevation(line, "heat_treatment", 90)
    print(f"  before: bottleneck={rep['before']['bottleneck']:22s}  throughput={rep['before']['throughput']}")
    print(f"  after:  bottleneck={rep['after']['bottleneck']:22s}  throughput={rep['after']['throughput']}")
    print(f"  constraint moved: {rep['constraint_moved']}")
    print("  (the new bottleneck is the next focus -- ToC repeats)")

    print("\n=== ToC PRINCIPLE ===")
    print("  Improvements at non-bottleneck stations DO NOT raise system")
    print("  throughput. They only build inventory. The math is simple:")
    print("  throughput = min(capacity_i). Anything else is local optimization")
    print("  paid for at the global level.")
