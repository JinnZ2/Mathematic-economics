"""
embedded_labor_audit.py  —  C002, C006

Wellsite labor (pump ops, terrain navigation, equipment maintenance) is not
automated by haul automation. The marketing claim "we automated trucking"
collapses a heterogeneous task stack into a single category, then prices
only the easiest piece.

Falsifier (C002): documented end-to-end automation including pump operation
at variable sites.

The canonical task inventory is 20 categories with an `automation_status`
field per entry. Allowed values:

    "fully_automated"      — autonomous stack handles 100% of cycles
                              without human intervention
    "partially_automated"  — stack handles base case; human absorbs
                              exceptions
    "remote_operator"      — moved off-truck to a human on a teleop console
    "human_required"       — no production autonomous capability today

`labor_offload_ratio` weights tasks by their operational time share and
counts only "fully_automated" as displaced.

License: CC0-1.0
"""

from typing import Dict, List


# 20 task categories. `share` sums to ~1.0; `automation_status` is set per
# deployment via `apply_status(...)`. The default inventory marks every
# task "human_required" so the baseline corresponds to a non-autonomous
# operation.
CANONICAL_OILFIELD_TASKS: List[dict] = [
    {"task": "interstate_haul",            "category": "haul",        "share": 0.20,
     "automation_status": "human_required"},
    {"task": "intrastate_haul",            "category": "haul",        "share": 0.06,
     "automation_status": "human_required"},
    {"task": "rural_lead_in_navigation",   "category": "navigation",  "share": 0.08,
     "automation_status": "human_required"},
    {"task": "lease_road_navigation",      "category": "navigation",  "share": 0.05,
     "automation_status": "human_required"},
    {"task": "off_road_terrain",           "category": "navigation",  "share": 0.04,
     "automation_status": "human_required"},
    {"task": "wellsite_positioning",       "category": "site_work",   "share": 0.04,
     "automation_status": "human_required"},
    {"task": "pump_hookup_disconnect",     "category": "site_work",   "share": 0.05,
     "automation_status": "human_required"},
    {"task": "pump_operation_monitoring",  "category": "site_work",   "share": 0.08,
     "automation_status": "human_required"},
    {"task": "load_securement",            "category": "site_work",   "share": 0.04,
     "automation_status": "human_required"},
    {"task": "site_supervisor_coordination","category": "site_work",  "share": 0.03,
     "automation_status": "human_required"},
    {"task": "pretrip_inspection",         "category": "monitoring",  "share": 0.04,
     "automation_status": "human_required"},
    {"task": "posttrip_inspection",        "category": "monitoring",  "share": 0.03,
     "automation_status": "human_required"},
    {"task": "fluid_and_tire_checks",      "category": "monitoring",  "share": 0.03,
     "automation_status": "human_required"},
    {"task": "in_motion_anomaly_response", "category": "monitoring",  "share": 0.04,
     "automation_status": "human_required"},
    {"task": "regulatory_paperwork",       "category": "compliance",  "share": 0.03,
     "automation_status": "human_required"},
    {"task": "weigh_station_interaction",  "category": "compliance",  "share": 0.02,
     "automation_status": "human_required"},
    {"task": "dot_inspection_handling",    "category": "compliance",  "share": 0.02,
     "automation_status": "human_required"},
    {"task": "customer_interaction",       "category": "interface",   "share": 0.04,
     "automation_status": "human_required"},
    {"task": "fueling_payment_dispute",    "category": "interface",   "share": 0.02,
     "automation_status": "human_required"},
    {"task": "roadside_incident_response", "category": "interface",   "share": 0.06,
     "automation_status": "human_required"},
]


VALID_STATUSES = {"fully_automated", "partially_automated",
                  "remote_operator", "human_required"}


def enumerate_driver_tasks(deployment_spec: dict | None = None) -> List[dict]:
    """Return the task inventory for a deployment.

    `deployment_spec` may carry `task_inventory` for a custom list;
    otherwise the canonical inventory is returned. Tasks are deep-copied
    so callers can mutate without affecting the module default.
    """
    inv = (deployment_spec or {}).get("task_inventory") or CANONICAL_OILFIELD_TASKS
    return [dict(t) for t in inv]


def apply_status(tasks: List[dict], status_map: Dict[str, str]) -> List[dict]:
    """Annotate `tasks` with per-task automation_status from `status_map`."""
    for s in status_map.values():
        if s not in VALID_STATUSES:
            raise ValueError(f"invalid automation_status: {s!r}; "
                             f"must be one of {sorted(VALID_STATUSES)}")
    out = []
    for t in tasks:
        t2 = dict(t)
        if t2["task"] in status_map:
            t2["automation_status"] = status_map[t2["task"]]
        out.append(t2)
    return out


def labor_offload_ratio(tasks: List[dict]) -> float:
    """Time-share displaced by automation.

    Counts only tasks marked `fully_automated`. Tasks marked
    `partially_automated`, `remote_operator`, or `human_required`
    contribute zero to the offload ratio — the labor moved, it did not
    disappear.
    """
    total = sum(t["share"] for t in tasks)
    if total <= 0:
        return 0.0
    offloaded = sum(t["share"] for t in tasks
                    if t.get("automation_status") == "fully_automated")
    return offloaded / total


def category_coverage(tasks: List[dict]) -> Dict[str, float]:
    """Per-category time-share fully_automated."""
    totals: Dict[str, float] = {}
    offloaded: Dict[str, float] = {}
    for t in tasks:
        cat = t["category"]
        totals[cat] = totals.get(cat, 0.0) + t["share"]
        if t.get("automation_status") == "fully_automated":
            offloaded[cat] = offloaded.get(cat, 0.0) + t["share"]
    return {cat: (offloaded.get(cat, 0.0) / totals[cat]) if totals[cat] else 0.0
            for cat in totals}


def status_distribution(tasks: List[dict]) -> Dict[str, float]:
    """Time-share by automation_status across the whole inventory."""
    total = sum(t["share"] for t in tasks)
    if total <= 0:
        return {s: 0.0 for s in VALID_STATUSES}
    out = {s: 0.0 for s in VALID_STATUSES}
    for t in tasks:
        out[t.get("automation_status", "human_required")] += t["share"]
    return {s: v / total for s, v in out.items()}


def driver_hours_per_delivery_change(pre_hours: float, post_hours: float) -> dict:
    """C002 explicit gate: did driver hours actually drop?"""
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


def c002_verdict(deployment_spec: dict | None = None,
                 status_map: Dict[str, str] | None = None,
                 pre_hours: float | None = None,
                 post_hours: float | None = None) -> dict:
    tasks = enumerate_driver_tasks(deployment_spec)
    if status_map:
        tasks = apply_status(tasks, status_map)
    ratio = labor_offload_ratio(tasks)
    cat_cov = category_coverage(tasks)
    dist = status_distribution(tasks)
    site_share = cat_cov.get("site_work", 0.0)
    scope_collapse_risk = ratio < 0.6 and site_share < 0.2
    out: dict = {
        "claim_id":            "C002",
        "labor_offload_ratio": ratio,
        "category_coverage":   cat_cov,
        "status_distribution": dist,
        "site_work_offloaded": site_share,
        "scope_collapse_risk": scope_collapse_risk,
        "falsifier": "documented end-to-end automation including pump operation at variable sites",
    }
    if pre_hours is not None and post_hours is not None:
        delta = driver_hours_per_delivery_change(pre_hours, post_hours)
        out["driver_hours_delta"] = delta
        out["threshold_met"] = bool(delta["threshold_met"]) or scope_collapse_risk
    else:
        out["threshold_met"] = scope_collapse_risk
    return out


if __name__ == "__main__":
    # Vendor claim: "we automated trucking" — actually automated interstate haul only
    print("haul-only:", c002_verdict(
        status_map={"interstate_haul": "fully_automated"},
        pre_hours=8.0, post_hours=7.5))
    # Realistic upper bound for an HD-mapped Permian corridor
    print("permian:", c002_verdict(
        status_map={
            "interstate_haul":          "fully_automated",
            "intrastate_haul":          "fully_automated",
            "rural_lead_in_navigation": "fully_automated",
            "lease_road_navigation":    "partially_automated",
            "pretrip_inspection":       "remote_operator",
            "posttrip_inspection":      "remote_operator",
        },
        pre_hours=8.0, post_hours=6.0))
