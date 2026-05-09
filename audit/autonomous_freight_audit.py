"""
autonomous_freight_audit.py

Constraint-layer audit of the autonomous long-haul freight narrative against
actual North American operating reality. Physics-grounded, stdlib-only,
falsifiable. CC0.

Premise: the automation narrative survives by cherry-picking ideal corridors
and ignoring the constraint surface where ~90% of actual freight moves.
This module makes that surface measurable.

Architecture:
    1. ConstraintLayer    -> single physical/operational constraint
    2. CorridorProfile    -> a route segment with measurable conditions
    3. audit_corridor()   -> scores feasibility per layer + cascade
    4. cascade_failure()  -> models how layer failures compound

Scoring: 0.0 = automation infeasible, 1.0 = automation viable.
A corridor only "works" if ALL load-bearing layers score >= threshold
simultaneously. Cascade failures lower the joint score multiplicatively,
not additively, because dependencies are coupled.

Falsifiable claims encoded:
    C1: Sensor reliability collapses below -20C (battery + lens icing + lidar drift)
    C2: Lane detection fails when snow obscures markings (Oct-May in Upper Midwest)
    C3: Rural GPS reliability < urban by measurable margin
    C4: Fragmenting an 80klb load into N smaller loads multiplies baseline
        energy cost (idle, rolling resistance, drivetrain) by ~N
    C5: Yard mechanical failures (kingpin, landing gear, glad-hands) require
        on-site human intervention at rate that does not scale with automation
    C6: Sensor recalibration cost in seasonal extremes exceeds labor savings
    C7: Synchronized autonomous response to weather events produces correlated
        failure (gridlock/accident clustering) rather than distributed risk
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from enum import Enum
import math


# -----------------------------------------------------------------------------
# Constraint layers
# -----------------------------------------------------------------------------

class LayerKind(Enum):
    THERMAL          = "thermal"           # temperature operating envelope
    VISIBILITY       = "visibility"        # snow, dust, fog, rain
    INFRASTRUCTURE   = "infrastructure"    # road condition, bridges, frost heaves
    COMMS            = "comms"             # GPS, cellular, satellite
    TOPOGRAPHY       = "topography"        # grades, switchbacks, mountain weather
    SHARED_TRAFFIC   = "shared_traffic"    # buggies, farm equipment, pedestrians
    YARD_MECHANICAL  = "yard_mechanical"   # kingpin, landing gear, glad-hands
    SUPPLY_CHAIN     = "supply_chain"      # rare earth, chips, satellites, helium
    CASCADE_RISK     = "cascade_risk"      # synchronized failure under shared inputs


@dataclass
class ConstraintLayer:
    """A single measurable operational constraint."""
    kind: LayerKind
    score: float                    # 0.0 infeasible -> 1.0 viable
    notes: str = ""
    load_bearing: bool = True       # if True, failure here can fail the whole route

    def passes(self, threshold: float = 0.6) -> bool:
        return self.score >= threshold


# -----------------------------------------------------------------------------
# Corridor profile
# -----------------------------------------------------------------------------

@dataclass
class CorridorProfile:
    """A route segment evaluated against measurable conditions."""
    name: str
    months_of_marginal_visibility: int        # snow / dust / fog months per year
    min_winter_temp_c: float                  # design-case low
    max_summer_temp_c: float                  # design-case high
    rural_fraction: float                     # 0.0 urban -> 1.0 rural
    grade_max_pct: float                      # steepest sustained grade
    shared_traffic_density: float             # 0.0 none -> 1.0 dominant
    gps_reliability: float                    # 0.0 -> 1.0
    seasonal_closure_days: int                # avg days/yr corridor closes
    layers: List[ConstraintLayer] = field(default_factory=list)


# -----------------------------------------------------------------------------
# Layer scoring functions (each is falsifiable against measurable data)
# -----------------------------------------------------------------------------

def score_thermal(c: CorridorProfile) -> ConstraintLayer:
    # Sensor + battery degradation envelope: viable roughly -20C to +45C.
    # Outside that, lithium capacity drops, lidar drifts, lenses fog/ice.
    low_penalty  = max(0.0, (-20.0 - c.min_winter_temp_c) / 30.0)   # -50C -> 1.0 penalty
    high_penalty = max(0.0, (c.max_summer_temp_c - 45.0) / 20.0)
    score = max(0.0, 1.0 - low_penalty - high_penalty)
    return ConstraintLayer(
        kind=LayerKind.THERMAL,
        score=score,
        notes=f"min {c.min_winter_temp_c}C / max {c.max_summer_temp_c}C "
              f"(viable envelope -20C..+45C)"
    )


def score_visibility(c: CorridorProfile) -> ConstraintLayer:
    # Lane detection requires unobscured markings. Snow / dust occludes them.
    # 8 months marginal visibility = ~0.33 viability ceiling.
    score = max(0.0, 1.0 - (c.months_of_marginal_visibility / 12.0))
    return ConstraintLayer(
        kind=LayerKind.VISIBILITY,
        score=score,
        notes=f"{c.months_of_marginal_visibility} months/yr marginal visibility"
    )


def score_infrastructure(c: CorridorProfile) -> ConstraintLayer:
    # Rural fraction proxies for road quality (frost heaves, narrow shoulders,
    # missing markings, deteriorating bridges).
    score = 1.0 - (0.7 * c.rural_fraction)
    return ConstraintLayer(
        kind=LayerKind.INFRASTRUCTURE,
        score=score,
        notes=f"rural fraction {c.rural_fraction:.2f}"
    )


def score_comms(c: CorridorProfile) -> ConstraintLayer:
    return ConstraintLayer(
        kind=LayerKind.COMMS,
        score=c.gps_reliability,
        notes=f"GPS reliability {c.gps_reliability:.2f}"
    )


def score_topography(c: CorridorProfile) -> ConstraintLayer:
    # Grades above 6% sustained require active load-aware brake management.
    # Above 8% it gets thermodynamically dangerous for an 80klb vehicle.
    if c.grade_max_pct <= 4.0:
        score = 1.0
    elif c.grade_max_pct <= 6.0:
        score = 0.75
    elif c.grade_max_pct <= 8.0:
        score = 0.45
    else:
        score = 0.20
    return ConstraintLayer(
        kind=LayerKind.TOPOGRAPHY,
        score=score,
        notes=f"max grade {c.grade_max_pct:.1f}%"
    )


def score_shared_traffic(c: CorridorProfile) -> ConstraintLayer:
    # Buggies, farm equipment, pedestrians: low reflectivity, unpredictable speed,
    # not represented in standard sensor training data.
    score = 1.0 - c.shared_traffic_density
    return ConstraintLayer(
        kind=LayerKind.SHARED_TRAFFIC,
        score=score,
        notes=f"shared-traffic density {c.shared_traffic_density:.2f}"
    )


def score_yard_mechanical() -> ConstraintLayer:
    # Kingpin release, landing gear, glad-hands, pin pulls: failure rate ~25%
    # per coupling cycle in field conditions. Requires on-site human override.
    # Score is a constant ceiling; automation cannot exceed it without solving
    # mechanical reliability first.
    return ConstraintLayer(
        kind=LayerKind.YARD_MECHANICAL,
        score=0.30,
        notes="empirical: ~1 in 4 couplings need human intervention"
    )


def score_supply_chain() -> ConstraintLayer:
    # Rare earth (sensors), chip fab (compute), helium (cooling), satellites
    # (positioning). Current US-domestic supply security: low.
    return ConstraintLayer(
        kind=LayerKind.SUPPLY_CHAIN,
        score=0.35,
        notes="rare earth + chips + helium + LEO comms: external dependence high"
    )


def score_cascade_risk(c: CorridorProfile) -> ConstraintLayer:
    # Identical software stacks responding to identical sensor inputs produce
    # correlated failure. Higher closure-day count = more shared-event exposure.
    score = max(0.0, 1.0 - (c.seasonal_closure_days / 60.0))
    return ConstraintLayer(
        kind=LayerKind.CASCADE_RISK,
        score=score,
        notes=f"{c.seasonal_closure_days} closure-days/yr -> synchronized failure exposure"
    )


# -----------------------------------------------------------------------------
# Audit pipeline
# -----------------------------------------------------------------------------

def audit_corridor(c: CorridorProfile) -> CorridorProfile:
    c.layers = [
        score_thermal(c),
        score_visibility(c),
        score_infrastructure(c),
        score_comms(c),
        score_topography(c),
        score_shared_traffic(c),
        score_yard_mechanical(),
        score_supply_chain(),
        score_cascade_risk(c),
    ]
    return c


def joint_feasibility(c: CorridorProfile) -> float:
    """
    Multiplicative joint score across load-bearing layers.
    Automation requires ALL layers to hold simultaneously, so we compound,
    not average. One weak layer dominates the result.
    """
    score = 1.0
    for layer in c.layers:
        if layer.load_bearing:
            score *= layer.score
    return score


def cascade_failure(c: CorridorProfile, threshold: float = 0.6) -> List[LayerKind]:
    """Return layers below threshold -- these are the breaking constraints."""
    return [layer.kind for layer in c.layers if not layer.passes(threshold)]


def report(c: CorridorProfile) -> str:
    lines = [f"=== {c.name} ==="]
    for layer in c.layers:
        flag = "OK " if layer.passes() else "XX "
        lines.append(f"  {flag} {layer.kind.value:16s} {layer.score:0.2f}  {layer.notes}")
    joint = joint_feasibility(c)
    failed = cascade_failure(c)
    lines.append(f"  joint feasibility (compound): {joint:0.3f}")
    lines.append(f"  failing layers: {[f.value for f in failed] or 'none'}")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Reference corridors -- empirical profiles from the conversation
# -----------------------------------------------------------------------------

CORRIDORS = [
    CorridorProfile(
        name="Tomah WI -> rural Walmart endpoints (Upper Midwest, winter)",
        months_of_marginal_visibility=8,
        min_winter_temp_c=-40.0,
        max_summer_temp_c=38.0,
        rural_fraction=0.85,
        grade_max_pct=5.0,
        shared_traffic_density=0.55,   # buggies + farm equipment
        gps_reliability=0.55,
        seasonal_closure_days=12,
    ),
    CorridorProfile(
        name="I-80 WY winter (Laramie -> Rawlins)",
        months_of_marginal_visibility=6,
        min_winter_temp_c=-35.0,
        max_summer_temp_c=33.0,
        rural_fraction=0.7,
        grade_max_pct=6.5,
        shared_traffic_density=0.10,
        gps_reliability=0.80,
        seasonal_closure_days=25,
    ),
    CorridorProfile(
        name="I-40 TN through Knoxville (mountain segment)",
        months_of_marginal_visibility=2,
        min_winter_temp_c=-15.0,
        max_summer_temp_c=36.0,
        rural_fraction=0.4,
        grade_max_pct=6.0,
        shared_traffic_density=0.15,
        gps_reliability=0.75,
        seasonal_closure_days=4,
    ),
    CorridorProfile(
        name="I-40 OK -> CA (high desert / 'ideal case')",
        months_of_marginal_visibility=2,
        min_winter_temp_c=-10.0,
        max_summer_temp_c=46.0,   # high-desert summer pushes envelope
        rural_fraction=0.55,
        grade_max_pct=4.0,
        shared_traffic_density=0.10,
        gps_reliability=0.85,
        seasonal_closure_days=3,
    ),
    CorridorProfile(
        name="Texas oilfield last-mile (goat-trail access)",
        months_of_marginal_visibility=3,   # dust storms
        min_winter_temp_c=-10.0,
        max_summer_temp_c=44.0,
        rural_fraction=0.95,
        grade_max_pct=4.0,
        shared_traffic_density=0.20,
        gps_reliability=0.40,
        seasonal_closure_days=5,
    ),
]


# -----------------------------------------------------------------------------
# Load fragmentation thermodynamics (claim C4)
# -----------------------------------------------------------------------------

def fragmentation_energy_cost(
    consolidated_lbs: float = 80_000,
    fragment_lbs: float = 10_000,
    baseline_overhead_per_vehicle: float = 0.35,
) -> Dict[str, float]:
    """
    A consolidated load uses 1.0 unit of vehicle baseline.
    Fragmenting into N vehicles uses N * baseline overhead even before
    payload work. baseline_overhead_per_vehicle = idle + rolling resistance
    + drivetrain loss as a fraction of total trip energy.
    """
    n = max(1.0, consolidated_lbs / fragment_lbs)
    consolidated_energy = 1.0
    fragmented_energy   = n * baseline_overhead_per_vehicle + 1.0
    return {
        "vehicles_required": n,
        "consolidated_energy_units": consolidated_energy,
        "fragmented_energy_units": fragmented_energy,
        "energy_multiplier": fragmented_energy / consolidated_energy,
    }


# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    for c in CORRIDORS:
        audit_corridor(c)
        print(report(c))
        print()

    print("--- load fragmentation (80klb -> 10klb) ---")
    frag = fragmentation_energy_cost()
    for k, v in frag.items():
        print(f"  {k}: {v:0.3f}")
