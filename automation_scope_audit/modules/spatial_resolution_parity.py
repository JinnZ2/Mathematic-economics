"""
spatial_resolution_parity.py — Phase 8 Task 8.2

For C001 (route variance via Jaccard distance), the comparison is
only meaningful when both route logs are at the same spatial
resolution. GPS-coordinate waypoints (~10 m granularity) and
city-pair waypoints (~100,000 m granularity) differ by ~4 orders of
magnitude; computing Jaccard between them produces a meaningless
number.

This module measures a route log's characteristic resolution (the
median inter-waypoint distance) and refuses parity when two logs
differ by > 2 orders of magnitude.

Acceptance: when route_log_a is GPS-resolution and route_log_b is
city-pair resolution, `parity_check(a, b)` returns
`mismatch=True, ratio=O(1e4)`.

License: CC0-1.0
"""

import math
import statistics
from typing import Dict, List


# Rough physical scale guesses per waypoint-identifier convention.
# Callers can override via `waypoint_scale_table`.
DEFAULT_WAYPOINT_SCALE_M: Dict[str, float] = {
    "gps_lat_lon":        10.0,           # ~10 m
    "gps_decimeter":       1.0,
    "gps_centimeter":      0.1,
    "hd_map_node":        15.0,           # ~15 m
    "lane_segment":       50.0,
    "road_segment":      500.0,
    "intersection":      200.0,
    "named_waypoint":   1_000.0,
    "lease_segment":   2_000.0,
    "city":          100_000.0,
    "state":       1_000_000.0,
    "country":    10_000_000.0,
}


def characteristic_resolution_m(
    route_log: List[dict],
    waypoint_scale_hint: float | None = None,
    waypoint_scale_table: Dict[str, float] | None = None,
) -> dict:
    """Estimate the characteristic resolution (median inter-waypoint distance) for a route log.

    If `waypoint_scale_hint` is supplied, returns that value as the
    authoritative resolution. Otherwise:
      1. If the route log declares `waypoint_convention` (a string in
         DEFAULT_WAYPOINT_SCALE_M), use that.
      2. Otherwise fall back to a token-length heuristic: shorter
         tokens tend to be city / region names; longer tokens tend to
         be coordinate identifiers.
    """
    if waypoint_scale_hint is not None:
        return {
            "resolution_m":  float(waypoint_scale_hint),
            "method":        "explicit_hint",
            "samples":       len(route_log),
        }
    if not route_log:
        return {"resolution_m": float("nan"), "method": "empty_log", "samples": 0}

    table = {**DEFAULT_WAYPOINT_SCALE_M, **(waypoint_scale_table or {})}

    # Method 1: convention declared
    conventions = [t.get("waypoint_convention") for t in route_log
                    if t.get("waypoint_convention")]
    if conventions:
        most_common = max(set(conventions), key=conventions.count)
        if most_common in table:
            return {
                "resolution_m":  table[most_common],
                "method":        "convention_declared",
                "convention":    most_common,
                "samples":       len(route_log),
            }

    # Method 2: heuristic by mean waypoint-token length
    token_lengths = []
    for t in route_log:
        for wp in t.get("waypoints", []):
            if isinstance(wp, str):
                token_lengths.append(len(wp))
    if not token_lengths:
        return {"resolution_m": float("nan"), "method": "no_waypoints",
                "samples": len(route_log)}

    mean_len = statistics.mean(token_lengths)
    # short tokens (1-6) tend to be city/region (~100km); 7-12 tend to
    # be named_waypoint / lease_segment (~1-2km); longer tokens tend to
    # be lane / hd_map / gps coordinates (~10-50 m).
    if mean_len <= 6:
        guess = 100_000.0
    elif mean_len <= 12:
        guess = 1_000.0
    else:
        guess = 50.0
    return {
        "resolution_m":  guess,
        "method":        "heuristic_by_token_length",
        "mean_token_length": mean_len,
        "samples":       len(route_log),
    }


def parity_check(
    log_a: List[dict],
    log_b: List[dict],
    scale_hint_a: float | None = None,
    scale_hint_b: float | None = None,
    waypoint_scale_table: Dict[str, float] | None = None,
    order_of_magnitude_tolerance: float = 2.0,
) -> dict:
    """Compare characteristic resolution of two route logs.

    Returns `mismatch=True` when the logs differ by more than
    `order_of_magnitude_tolerance` orders of magnitude.
    """
    res_a = characteristic_resolution_m(log_a, scale_hint_a, waypoint_scale_table)
    res_b = characteristic_resolution_m(log_b, scale_hint_b, waypoint_scale_table)
    ra, rb = res_a["resolution_m"], res_b["resolution_m"]
    if not (ra > 0 and rb > 0):
        return {
            "log_a_resolution":  res_a,
            "log_b_resolution":  res_b,
            "ratio":             float("nan"),
            "log10_diff":        float("nan"),
            "mismatch":          True,
            "reason":            "one or both resolutions undefined",
        }
    ratio = max(ra, rb) / min(ra, rb)
    log10_diff = abs(math.log10(ra) - math.log10(rb))
    return {
        "log_a_resolution":  res_a,
        "log_b_resolution":  res_b,
        "ratio":             ratio,
        "log10_diff":        log10_diff,
        "tolerance":         order_of_magnitude_tolerance,
        "mismatch":          log10_diff > order_of_magnitude_tolerance,
    }


if __name__ == "__main__":
    gps_log = [{"origin": "A", "destination": "B",
                "waypoints": ["lat_32.7831_lon_-96.8067",
                              "lat_32.7820_lon_-96.8055"],
                "waypoint_convention": "gps_lat_lon"}
               for _ in range(10)]
    city_log = [{"origin": "DAL", "destination": "HOU",
                  "waypoints": ["DFW", "WAC", "HOU"],
                  "waypoint_convention": "city"}
                for _ in range(10)]
    print("parity gps vs city:", parity_check(gps_log, city_log))
    print()
    print("parity gps vs gps:", parity_check(gps_log, gps_log))
