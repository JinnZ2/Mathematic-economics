"""
scope_geometry.py  —  C001

Autonomous trucking ROI requires fixed depot-to-destination geometry.

Falsifier: working autonomous deployment on routes with >20% variance.

A route log is a list of trip dicts; each carries `origin`, `destination`,
and a list of waypoint identifiers. Variance is computed as the mean
pairwise Jaccard distance between trips of the same origin-destination
pair, weighted by trip count.

Jaccard distance is:

    d(A, B) = 1 - |A ∩ B| / |A ∪ B|

For two trips covering identical waypoint sets, d = 0. For two trips with
no shared waypoints, d = 1. The metric is a proper metric (symmetric,
zero on identity, triangle inequality holds for the family used here) and
is robust to waypoint *ordering* — two trips that hit the same nodes in a
different order register as identical, which matches how HD-mapped lane
graphs are routed by autonomous stacks.

License: CC0-1.0
"""

from collections import defaultdict
from itertools import combinations
from typing import Dict, List


def _jaccard_distance(a: set, b: set) -> float:
    union = a | b
    if not union:
        return 0.0
    return 1.0 - len(a & b) / len(union)


def measure_route_variance(route_log: List[dict]) -> float:
    """Trip-weighted mean pairwise Jaccard distance between same-OD trips.

    For each OD pair with >= 2 trips, compute the mean Jaccard distance
    between all unordered trip pairs. Aggregate across OD pairs weighted
    by the number of trips on that pair. OD pairs with a single trip
    contribute zero (no observed variance).

    Returns 0.0 for perfectly repeated routes; approaches 1.0 when every
    trip on a pair visits a disjoint waypoint set.
    """
    if not route_log:
        return 0.0

    by_pair: Dict[tuple, List[set]] = defaultdict(list)
    for trip in route_log:
        origin = trip.get("origin")
        dest = trip.get("destination")
        waypoints = set(trip.get("waypoints", []))
        by_pair[(origin, dest)].append(waypoints)

    weighted_sum = 0.0
    total_weight = 0
    for sequences in by_pair.values():
        n = len(sequences)
        if n < 2:
            total_weight += n
            continue
        pair_distances = [
            _jaccard_distance(a, b) for a, b in combinations(sequences, 2)
        ]
        mean_d = sum(pair_distances) / len(pair_distances)
        weighted_sum += mean_d * n
        total_weight += n

    if total_weight == 0:
        return 0.0
    return weighted_sum / total_weight


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


VARIANCE_TIERS = [
    ("fixed",          0.00, 0.10, "Automation-viable corridor: variance below 10%."),
    ("hybrid_viable",  0.10, 0.30, "Hybrid (autonomous on corridor + human at touchpoints)."),
    ("variable",       0.30, 0.60, "Mostly human; autonomy applies only to stable sub-segments."),
    ("chaotic",        0.60, 1.01, "Human-only; no stable geometry to anchor autonomy."),
]


def variance_tier(variance: float) -> dict:
    """Bin a route-variance measurement into the four-tier scale.

    Bins (Jaccard distance):
      0.00-0.10  -> "fixed"
      0.10-0.30  -> "hybrid_viable"
      0.30-0.60  -> "variable"
      >= 0.60    -> "chaotic"
    """
    for name, lo, hi, note in VARIANCE_TIERS:
        if lo <= variance < hi:
            return {"tier": name, "lo": lo, "hi": hi, "note": note}
    return {"tier": "chaotic", "lo": 0.60, "hi": 1.01,
            "note": VARIANCE_TIERS[-1][3]}


def c001_verdict(route_log: List[dict], infrastructure_state: dict) -> dict:
    """Compose the C001 audit result with both binary and tiered output."""
    variance = measure_route_variance(route_log)
    classification = classify_scope(variance, infrastructure_state)
    tier = variance_tier(variance)
    threshold_met = variance < 0.05
    return {
        "claim_id": "C001",
        "variance": variance,
        "tier": tier["tier"],
        "tier_note": tier["note"],
        "tier_bounds": [tier["lo"], tier["hi"]],
        "classification": classification,
        "threshold_met": threshold_met,
        "falsifier": "working autonomous deployment on routes with >20% variance",
        "notes": (
            "Variance is trip-weighted mean pairwise Jaccard distance per "
            "OD pair. Tier is the graduated bin (fixed / hybrid_viable / "
            "variable / chaotic); threshold_met is the binary 5%% gate."
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
