"""
scope_geometry.py  —  C001

Autonomous trucking ROI requires fixed depot-to-destination geometry.

Falsifier: working autonomous deployment on routes with >20% variance.

A route log is a list of trip dicts; each carries `origin`, `destination`,
distance, and an ordered list of waypoint identifiers. Variance is computed
as the fraction of trips per origin-destination pair whose waypoint sequence
deviates from the modal sequence. A pair with one fixed sequence has
variance 0.0; a pair with N unique sequences across N trips has variance
approaching 1.0.

License: CC0-1.0
"""

from collections import Counter, defaultdict
from typing import Dict, List


def measure_route_variance(route_log: List[dict]) -> float:
    """Fraction of trips that deviate from the modal sequence per OD pair.

    Aggregates across all origin-destination pairs in the log, weighted by
    trip count. Returns 0.0 for perfectly repeated routes; 1.0 when every
    trip on every pair is unique.
    """
    if not route_log:
        return 0.0

    by_pair: Dict[tuple, List[tuple]] = defaultdict(list)
    for trip in route_log:
        origin = trip.get("origin")
        dest = trip.get("destination")
        waypoints = tuple(trip.get("waypoints", []))
        by_pair[(origin, dest)].append(waypoints)

    total_trips = 0
    total_deviating = 0
    for sequences in by_pair.values():
        counts = Counter(sequences)
        modal_count = counts.most_common(1)[0][1]
        n = len(sequences)
        total_trips += n
        total_deviating += (n - modal_count)

    if total_trips == 0:
        return 0.0
    return total_deviating / total_trips


def classify_scope(variance: float, infrastructure_state: dict) -> str:
    """Returns 'automation_viable' | 'hybrid_required' | 'human_only'.

    Combines geometric variance with two infrastructure preconditions:
      - paved_pct: fraction of route surfaces paved (lane-marked, drainage)
      - mapped_pct: fraction of route HD-mapped for the autonomous stack

    Thresholds (claim C001):
      variance < 0.05 AND paved >= 0.95 AND mapped >= 0.95 -> automation_viable
      variance < 0.20 with mixed infrastructure             -> hybrid_required
      otherwise                                              -> human_only
    """
    paved = float(infrastructure_state.get("paved_pct", 0.0))
    mapped = float(infrastructure_state.get("mapped_pct", 0.0))

    if variance < 0.05 and paved >= 0.95 and mapped >= 0.95:
        return "automation_viable"
    if variance < 0.20 and paved >= 0.50 and mapped >= 0.50:
        return "hybrid_required"
    return "human_only"


def c001_verdict(route_log: List[dict], infrastructure_state: dict) -> dict:
    """Compose the C001 audit result."""
    variance = measure_route_variance(route_log)
    classification = classify_scope(variance, infrastructure_state)
    threshold_met = variance < 0.05
    return {
        "claim_id": "C001",
        "variance": variance,
        "classification": classification,
        "threshold_met": threshold_met,
        "falsifier": "working autonomous deployment on routes with >20% variance",
        "notes": (
            "Variance is fraction of trips deviating from modal waypoint "
            "sequence per OD pair, weighted by trip count."
        ),
    }


if __name__ == "__main__":
    fixed_route = [
        {"origin": "depot_A", "destination": "frac_pad_1",
         "waypoints": ["wp1", "wp2", "wp3"]} for _ in range(50)
    ]
    print("fixed:", c001_verdict(fixed_route,
                                  {"paved_pct": 1.0, "mapped_pct": 1.0}))

    variable_route = [
        {"origin": "depot_A", "destination": f"well_{i % 12}",
         "waypoints": [f"wp_{(i * j) % 7}" for j in range(3)]}
        for i in range(50)
    ]
    print("variable:", c001_verdict(variable_route,
                                     {"paved_pct": 0.4, "mapped_pct": 0.3}))
