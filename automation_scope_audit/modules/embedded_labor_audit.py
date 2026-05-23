"""
embedded_labor_audit.py  —  C002, C006

Wellsite labor (pump ops, terrain navigation, equipment maintenance) is not
automated by haul automation. The marketing claim "we automated trucking"
collapses a heterogeneous task stack into a single category, then prices
only the easiest piece.

Falsifier (C002): documented end-to-end automation including pump operation
at variable sites.

Each deployment is decomposed into the full driver-touchpoint task list.
`labor_offload_ratio` is the fraction of operational time genuinely
displaced — explicitly NOT the fraction of marketing claims displaced.

License: CC0-1.0
"""

from typing import Dict, List


# Canonical task inventory for oilfield haul, with rough fraction of total
# operational time per delivery cycle. Sums approximately to 1.0.
CANONICAL_OILFIELD_TASKS: List[dict] = [
    {"task": "interstate_haul",            "category": "haul",       "share": 0.30},
    {"task": "rural_lead_in_navigation",   "category": "navigation", "share": 0.12},
    {"task": "lease_road_navigation",      "category": "navigation", "share": 0.08},
    {"task": "wellsite_positioning",       "category": "site_work",  "share": 0.04},
    {"task": "pump_hookup_disconnect",     "category": "site_work",  "share": 0.06},
    {"task": "pump_operation_monitoring",  "category": "site_work",  "share": 0.10},
    {"task": "load_securement",            "category": "site_work",  "share": 0.04},
    {"task": "pretrip_inspection",         "category": "monitoring", "share": 0.05},
    {"task": "posttrip_inspection",        "category": "monitoring", "share": 0.04},
    {"task": "fluid_and_tire_checks",      "category": "monitoring", "share": 0.03},
    {"task": "in_motion_anomaly_response", "category": "monitoring", "share": 0.06},
    {"task": "regulatory_paperwork",       "category": "compliance", "share": 0.04},
    {"task": "customer_interaction",       "category": "interface",  "share": 0.04},
]


def enumerate_driver_tasks(deployment_spec: dict) -> List[str]:
    """Return the task inventory the deployment must replace.

    `deployment_spec` may carry a custom `task_inventory` list; otherwise the
    canonical oilfield-haul inventory is returned (task names only).
    """
    inv = deployment_spec.get("task_inventory") or CANONICAL_OILFIELD_TASKS
    return [t["task"] if isinstance(t, dict) else t for t in inv]


def labor_offload_ratio(automated_tasks: List[str],
                        total_tasks: List[dict] | List[str] | None = None) -> float:
    """Share of *operational time* genuinely displaced by automation.

    If `total_tasks` is a list of dicts with `share` fields, the ratio is
    time-weighted: automating a 30%-share task counts six times more than
    automating a 5%-share task. If it is a plain list of names, the ratio
    is unweighted. None defaults to the canonical inventory.

    The point is to detect scope collapse: a system that automates
    `interstate_haul` (30%) and nothing else displaces 30% of operator
    time, not "the job".
    """
    if total_tasks is None:
        total_tasks = CANONICAL_OILFIELD_TASKS

    if total_tasks and isinstance(total_tasks[0], dict):
        total_share = sum(t["share"] for t in total_tasks)
        if total_share == 0:
            return 0.0
        offloaded_share = sum(
            t["share"] for t in total_tasks if t["task"] in set(automated_tasks)
        )
        return offloaded_share / total_share

    total_names = [t for t in total_tasks]  # type: ignore[assignment]
    if not total_names:
        return 0.0
    return sum(1 for a in automated_tasks if a in total_names) / len(total_names)


def category_coverage(automated_tasks: List[str],
                      total_tasks: List[dict] | None = None) -> Dict[str, float]:
    """Per-category time-share displaced. Surfaces *which* labor was offloaded.

    A deployment that scores 0.30 overall but only displaces the `haul`
    category has done nothing about `site_work`, `monitoring`, `compliance`,
    or `interface` labor — and the claim that the trucker has been replaced
    is structurally false.
    """
    if total_tasks is None:
        total_tasks = CANONICAL_OILFIELD_TASKS
    auto = set(automated_tasks)

    totals: Dict[str, float] = {}
    offloaded: Dict[str, float] = {}
    for t in total_tasks:
        cat = t["category"]
        totals[cat] = totals.get(cat, 0.0) + t["share"]
        if t["task"] in auto:
            offloaded[cat] = offloaded.get(cat, 0.0) + t["share"]

    return {cat: (offloaded.get(cat, 0.0) / totals[cat]) if totals[cat] else 0.0
            for cat in totals}


def driver_hours_per_delivery_change(pre_hours: float, post_hours: float) -> dict:
    """C002 explicit gate: did driver hours actually drop?

    Many "autonomous" deployments shift hours from in-cab to remote-monitor
    or to on-site contractors and report only the in-cab number. Pass both
    measured hours per delivery (sum of all human time touching the cycle).
    """
    delta_pct = ((post_hours - pre_hours) / pre_hours * 100.0) if pre_hours > 0 else 0.0
    return {
        "pre_hours":   pre_hours,
        "post_hours":  post_hours,
        "delta_pct":   delta_pct,
        "threshold_met": post_hours >= pre_hours,
        "interpretation": "C002 threshold met (hours unchanged or higher) — "
                          "automation did not displace integrated labor"
        if post_hours >= pre_hours else
        "Hours dropped — investigate whether displaced hours moved off-book "
        "to remote monitoring / contractors / customer staff",
    }


def c002_verdict(deployment_spec: dict, automated_tasks: List[str],
                 pre_hours: float | None = None,
                 post_hours: float | None = None) -> dict:
    inventory = deployment_spec.get("task_inventory") or CANONICAL_OILFIELD_TASKS
    ratio = labor_offload_ratio(automated_tasks, inventory)
    cat_cov = category_coverage(automated_tasks, inventory)
    site_share = cat_cov.get("site_work", 0.0)
    scope_collapse_risk = ratio < 0.6 and site_share < 0.2
    out: dict = {
        "claim_id":            "C002",
        "labor_offload_ratio": ratio,
        "category_coverage":   cat_cov,
        "site_work_offloaded": site_share,
        "scope_collapse_risk": scope_collapse_risk,
        "falsifier": "documented end-to-end automation including pump operation at variable sites",
    }
    # Threshold per spec: driver hours per delivery unchanged or increased
    # post-automation. Fall back to scope_collapse_risk when hours are not
    # provided.
    if pre_hours is not None and post_hours is not None:
        delta = driver_hours_per_delivery_change(pre_hours, post_hours)
        out["driver_hours_delta"] = delta
        out["threshold_met"] = bool(delta["threshold_met"]) or scope_collapse_risk
    else:
        out["threshold_met"] = scope_collapse_risk
    return out


if __name__ == "__main__":
    spec = {"deployment": "Permian sand haul"}
    # Vendor claim: "we automated trucking"
    # Actually automated: interstate_haul only
    print("haul-only:", c002_verdict(spec, ["interstate_haul"],
                                      pre_hours=8.0, post_hours=7.5))
    # Realistic upper bound: haul + rural lead-in + HD-mapped lease road
    print("haul+lead-in:", c002_verdict(
        spec,
        ["interstate_haul", "rural_lead_in_navigation",
         "lease_road_navigation"],
        pre_hours=8.0, post_hours=6.0))
