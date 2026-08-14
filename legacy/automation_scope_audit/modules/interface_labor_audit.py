"""
interface_labor_audit.py  —  C011, C012, C013

Every connection point a driver currently mediates — fuel, customer,
dispatch, maintenance, regulatory, roadside service, payment systems —
is unpriced flexibility. Replacing the driver requires either replacing
every interface or absorbing the failure cost when an unmediated
interface degrades.

C011: Driver-mediated interfaces are unpriced flexibility that must be replaced.
C012: Autonomous deployments shift energy cost off-vehicle into remote
      diagnostic / dispatch / customer service infrastructure not counted
      in vehicle TCO.
C013: Driver adaptation across novel fault modes is unpriced general-purpose
      problem-solving.

License: CC0-1.0
"""

from typing import Dict, List


# Canonical interfaces a driver currently mediates for an oilfield / haul
# operation. Each carries a `frequency_per_week`, a list of typical fault
# modes the driver historically handled in-stride, and `adaptation_score`
# (0.0 - 1.0) reflecting how much novelty the human absorbs vs how much is
# scripted.
INTERFACES_CLASS8: List[dict] = [
    {"interface": "fuel_system",
     "frequency_per_week": 6,
     "fault_modes": ["card_decline", "pump_malfunction", "wrong_grade",
                     "spill_response", "tank_locking_issue"],
     "adaptation_score": 0.6},
    {"interface": "customer_receiving",
     "frequency_per_week": 14,
     "fault_modes": ["site_locked", "wrong_pad", "supervisor_absent",
                     "rig_state_change", "load_rejected", "scale_mismatch"],
     "adaptation_score": 0.9},
    {"interface": "dispatch",
     "frequency_per_week": 14,
     "fault_modes": ["reroute_request", "load_change", "weather_hold",
                     "regulatory_check"],
     "adaptation_score": 0.7},
    {"interface": "maintenance",
     "frequency_per_week": 2,
     "fault_modes": ["intermittent_warning", "minor_field_fix",
                     "fluid_top_up", "fuse_replace", "limp_home_decision"],
     "adaptation_score": 0.85},
    {"interface": "regulatory",
     "frequency_per_week": 3,
     "fault_modes": ["weigh_station", "DOT_inspection",
                     "load_paperwork_anomaly", "ELD_dispute"],
     "adaptation_score": 0.8},
    {"interface": "roadside_services",
     "frequency_per_week": 0.5,
     "fault_modes": ["jump_start", "tire_change_assist",
                     "minor_collision_response", "police_interaction"],
     "adaptation_score": 0.95},
    {"interface": "payment_systems",
     "frequency_per_week": 6,
     "fault_modes": ["card_decline", "alternate_payment",
                     "receipt_dispute", "fraud_flag"],
     "adaptation_score": 0.7},
]


# Default replacement-cost stack per interface.
# - `onboard_driver`:    driver does it; cost is the marginal driver time.
# - `remote_diagnostic`: server farm + on-call specialist; per-event cost.
# - `mobile_tech`:       dispatched technician; cost includes vehicle +
#                        staff time + truck downtime + cargo dwell.
DEFAULT_RESOLUTION_COSTS_USD: Dict[str, Dict[str, float]] = {
    "fuel_system":        {"onboard_driver":  5.0,
                            "remote_diagnostic": 90.0,
                            "mobile_tech":    400.0},
    "customer_receiving": {"onboard_driver": 12.0,
                            "remote_diagnostic": 220.0,
                            "mobile_tech":    900.0},
    "dispatch":           {"onboard_driver":  3.0,
                            "remote_diagnostic":  60.0,
                            "mobile_tech":    350.0},
    "maintenance":        {"onboard_driver": 20.0,
                            "remote_diagnostic": 180.0,
                            "mobile_tech":  1_200.0},
    "regulatory":         {"onboard_driver": 25.0,
                            "remote_diagnostic": 250.0,
                            "mobile_tech":  1_400.0},
    "roadside_services":  {"onboard_driver": 45.0,
                            "remote_diagnostic": 500.0,
                            "mobile_tech":  2_800.0},
    "payment_systems":    {"onboard_driver":  4.0,
                            "remote_diagnostic":  90.0,
                            "mobile_tech":    400.0},
}


# Off-vehicle energy stack for autonomous operations, scaled per truck.
# Annual joules and annual USD; both are exposed because the surrounding
# repository explicitly avoids monetary monoculture.
DEFAULT_OFFVEHICLE_STACK_PER_TRUCK = {
    "remote_diagnostic_center": {"annual_joules": 1.5e10, "annual_usd": 4_800.0},
    "telemetry_network":        {"annual_joules": 4.0e9,  "annual_usd": 3_200.0},
    "mobile_tech_fleet_share":  {"annual_joules": 8.0e9,  "annual_usd": 5_500.0},
    "customer_service_staff":   {"annual_joules": 2.5e9,  "annual_usd": 3_600.0},
    "software_maintenance":     {"annual_joules": 1.2e9,  "annual_usd": 2_400.0},
    "regulatory_compliance":    {"annual_joules": 0.8e9,  "annual_usd": 1_500.0},
}


def enumerate_interfaces(truck_type: str = "class8") -> List[dict]:
    """Return every connection point a driver currently mediates."""
    if truck_type != "class8":
        raise KeyError(f"only class8 interfaces are bundled: got {truck_type}")
    return [dict(i) for i in INTERFACES_CLASS8]


def model_resolution_costs(interface: dict, resolution_type: str,
                           cost_table: Dict[str, Dict[str, float]] | None = None
                           ) -> dict:
    """Per-event cost and annual cost to resolve faults at this interface.

    `resolution_type` in {"onboard_driver", "remote_diagnostic", "mobile_tech"}.
    """
    table = cost_table or DEFAULT_RESOLUTION_COSTS_USD
    name = interface["interface"]
    if name not in table:
        raise KeyError(f"no cost row for interface {name}")
    if resolution_type not in table[name]:
        raise KeyError(f"unknown resolution type {resolution_type}")
    per_event = table[name][resolution_type]
    events_per_year = interface["frequency_per_week"] * 50.0
    annual = per_event * events_per_year
    return {
        "interface":           name,
        "resolution_type":     resolution_type,
        "per_event_usd":       per_event,
        "events_per_year":     events_per_year,
        "annual_cost_usd":     annual,
    }


def energetic_cost_stack(autonomous_deployment: dict,
                         stack: Dict[str, dict] | None = None) -> dict:
    """Aggregate off-vehicle energy / dollars per truck per year.

    `autonomous_deployment` may carry:
      - `fleet_size` (int)
      - `multipliers` (dict) keyed by stack component, default 1.0.

    Returns totals scaled to the whole fleet so the operator can see the
    "off-book" line items.
    """
    base = stack or DEFAULT_OFFVEHICLE_STACK_PER_TRUCK
    multipliers = autonomous_deployment.get("multipliers") or {}
    fleet_size = int(autonomous_deployment.get("fleet_size", 1))

    per_truck_joules = 0.0
    per_truck_usd = 0.0
    line_items = {}
    for k, v in base.items():
        m = float(multipliers.get(k, 1.0))
        j = v["annual_joules"] * m
        d = v["annual_usd"] * m
        per_truck_joules += j
        per_truck_usd += d
        line_items[k] = {"annual_joules": j, "annual_usd": d}

    return {
        "fleet_size":                 fleet_size,
        "per_truck_annual_joules":    per_truck_joules,
        "per_truck_annual_usd":       per_truck_usd,
        "fleet_annual_joules":        per_truck_joules * fleet_size,
        "fleet_annual_usd":           per_truck_usd * fleet_size,
        "line_items":                 line_items,
    }


def unpriced_driver_adaptation(interface: dict) -> float:
    """Annualized count of fault modes a driver handles without escalation.

    Quantified as: number of distinct fault modes × adaptation score ×
    frequency per year. The output is a count, not a dollar value: the
    point of the metric is that this is *not currently priced*.
    """
    fault_modes = interface.get("fault_modes") or []
    score = float(interface.get("adaptation_score", 0.0))
    events_per_year = float(interface.get("frequency_per_week", 0.0)) * 50.0
    return len(fault_modes) * score * events_per_year


def c011_verdict(truck_type: str = "class8",
                 cost_table: Dict[str, Dict[str, float]] | None = None,
                 onboard_hourly_rate: float = 30.0) -> dict:
    interfaces = enumerate_interfaces(truck_type)
    onboard_total = 0.0
    remote_total = 0.0
    mobile_total = 0.0
    by_interface = []
    for iface in interfaces:
        onboard = model_resolution_costs(iface, "onboard_driver", cost_table)
        remote = model_resolution_costs(iface, "remote_diagnostic", cost_table)
        mobile = model_resolution_costs(iface, "mobile_tech", cost_table)
        onboard_total += onboard["annual_cost_usd"]
        remote_total  += remote["annual_cost_usd"]
        mobile_total  += mobile["annual_cost_usd"]
        by_interface.append({
            "interface": iface["interface"],
            "onboard_driver_annual_usd": onboard["annual_cost_usd"],
            "remote_diagnostic_annual_usd": remote["annual_cost_usd"],
            "mobile_tech_annual_usd": mobile["annual_cost_usd"],
        })
    autonomous_total = remote_total + mobile_total * 0.25  # 25% escalate to mobile
    ratio = (autonomous_total / onboard_total) if onboard_total > 0 else float("inf")
    return {
        "claim_id":                "C011",
        "by_interface":            by_interface,
        "onboard_driver_annual_usd": onboard_total,
        "autonomous_blended_annual_usd": autonomous_total,
        "remote_only_annual_usd":  remote_total,
        "mobile_only_annual_usd":  mobile_total,
        "cost_ratio_autonomous_to_driver": ratio,
        "threshold_met":           ratio > 2.0,
        "falsifier": "autonomous deployment with documented interface coverage at <2x driver-mediated cost",
    }


def c012_verdict(autonomous_deployment: dict,
                 reported_vehicle_tco_per_truck_usd: float,
                 stack: Dict[str, dict] | None = None) -> dict:
    stack_out = energetic_cost_stack(autonomous_deployment, stack)
    offvehicle = stack_out["per_truck_annual_usd"]
    share = (offvehicle /
             (offvehicle + reported_vehicle_tco_per_truck_usd)
             if (offvehicle + reported_vehicle_tco_per_truck_usd) > 0
             else 0.0)
    return {
        "claim_id":              "C012",
        "off_vehicle_annual_usd_per_truck": offvehicle,
        "reported_vehicle_tco_per_truck_usd": reported_vehicle_tco_per_truck_usd,
        "off_vehicle_share":     share,
        "threshold_met":         share > 0.30,
        "stack":                 stack_out,
        "falsifier": "audited TCO showing remote operations < 10% of total",
    }


def c013_verdict(truck_type: str = "class8",
                 autonomous_handled_per_year: int = 0) -> dict:
    """Compares total driver-adaptation events against documented autonomous
    coverage.
    """
    interfaces = enumerate_interfaces(truck_type)
    driver_total = sum(unpriced_driver_adaptation(i) for i in interfaces)
    ratio = (driver_total / autonomous_handled_per_year
             if autonomous_handled_per_year > 0 else float("inf"))
    return {
        "claim_id":                  "C013",
        "driver_adaptation_per_year": driver_total,
        "autonomous_handled_per_year": autonomous_handled_per_year,
        "coverage_ratio_driver_to_autonomous": ratio,
        "threshold_met":             ratio > 5.0,
        "falsifier": "documented autonomous system handling >80% of historical driver exceptions",
    }


if __name__ == "__main__":
    print("C011:", c011_verdict())
    print("C012:", c012_verdict(
        {"fleet_size": 50,
         "multipliers": {"remote_diagnostic_center": 1.0}},
        reported_vehicle_tco_per_truck_usd=55_000.0))
    print("C013:", c013_verdict(autonomous_handled_per_year=200))
