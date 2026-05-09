"""
success_specification_validator.py

Capstone audit module for transportation_automation_audit.py
and companion modules.

Defines what SUCCESS actually means thermodynamically across
all coupled constraint layers, then measures whether the
system being deployed is aimed at that target or at its
inverse.

Core insight (from Kavik, 6M-mile practitioner):

  Success is not "minimize individual vehicle time."
  Success is FLUIDITY across all coupled layers:
    - traffic flow (load-balancing, not shock-wave)
    - infrastructure health (preventive load distribution)
    - human coordination (dock fluidity, cooperation)
    - vehicle longevity (smooth-flow wear thermodynamics)
    - ecological coexistence (alerting wildlife, not startling)
    - schedule integration (zero-stop where possible)
    - exceptional customer service (cooperation at every node)

  Measured as TOTAL-SYSTEM energy dissipation minimized and
  throughput maximized, NOT as individual-vehicle metrics.

This is mastery-specification, not mastery-comparison.
The bar isn't "match the median driver."
The bar is "operate at the thermodynamic ceiling."

If automation is optimized for individual-vehicle metrics,
it's pointed at the OPPOSITE of success across every coupled
layer. Deployment will produce the inverse of success:
increased friction, infrastructure degradation, human
antagonism, ecological disruption.

License: CC0
Stdlib only. Falsifiable. Domain-agnostic for any system
where multi-layer coupling matters.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


# ============================================================
# THE SUCCESS SPECIFICATION
# ============================================================

class FluidityDimension(Enum):
    """The coupled layers across which success must be measured."""
    TRAFFIC_FLOW = "traffic_flow"
    INFRASTRUCTURE_HEALTH = "infrastructure_health"
    HUMAN_COORDINATION = "human_coordination"
    VEHICLE_LONGEVITY = "vehicle_longevity"
    ECOLOGICAL_COEXISTENCE = "ecological_coexistence"
    SCHEDULE_INTEGRATION = "schedule_integration"
    CUSTOMER_NODE_COOPERATION = "customer_node_cooperation"


@dataclass
class FluiditySpec:
    """
    The mastery-level specification for one fluidity dimension.

    Each dimension has a description of what mastery actually
    looks like (sourced from lived practitioner knowledge),
    plus measurable criteria.
    """
    dimension: FluidityDimension
    mastery_description: str
    measurable_criteria: List[str]
    inverse_failure_mode: str  # what happens when system is aimed
                               # at the opposite metric


SUCCESS_SPECIFICATION: List[FluiditySpec] = [
    FluiditySpec(
        dimension=FluidityDimension.TRAFFIC_FLOW,
        mastery_description=(
            "Operate as a load-balancing node that absorbs merge "
            "chaos, manages gap-as-function-of-speed, and prevents "
            "shock-wave propagation. Time speed and following "
            "distance to keep corridor flowing for everyone, not "
            "just self."
        ),
        measurable_criteria=[
            "Following distance scaled to speed (not fixed)",
            "Merge absorption rather than gap exploitation",
            "Speed timing across upcoming bottlenecks",
            "Shock-wave amplification near zero",
            "Total corridor throughput improved by presence",
        ],
        inverse_failure_mode=(
            "Tight following distance + individual-time optimization "
            "= shock-wave generation, corridor throughput collapse, "
            "infrastructure stress amplification."
        ),
    ),
    FluiditySpec(
        dimension=FluidityDimension.INFRASTRUCTURE_HEALTH,
        mastery_description=(
            "Distribute load smoothly across pavement and bridges. "
            "Avoid stop-go thermal cycling that fatigues concrete. "
            "Recognize that aggressive driving accelerates next "
            "year's construction load."
        ),
        measurable_criteria=[
            "Smooth acceleration/deceleration profiles",
            "Bridge crossing without dynamic load amplification",
            "Long-duration concrete fatigue minimized",
            "Construction-zone growth rate not amplified by "
            "driving pattern",
        ],
        inverse_failure_mode=(
            "Constant braking + acceleration amplifies pavement "
            "fatigue. Each year accelerates next year's repair load. "
            "Infrastructure cost detonates within 3-7 years."
        ),
    ),
    FluiditySpec(
        dimension=FluidityDimension.HUMAN_COORDINATION,
        mastery_description=(
            "Lubricate all transitions. At dock with 10-min wait, "
            "walk around to find someone. Build cooperation through "
            "humor, presence, attention. Make every interaction "
            "easier for the next person, not harder."
        ),
        measurable_criteria=[
            "Dock dwell time minimized through active "
            "coordination",
            "Customer relationship quality net positive",
            "Cooperation built (not friction generated) at "
            "every node",
            "Downstream worker tasks made easier by your "
            "presence",
        ],
        inverse_failure_mode=(
            "Passive waiting at dock, phone-watching, friction "
            "generation. Workers downstream inherit your delays. "
            "Human coordination layer collapses; no one trusts "
            "the system."
        ),
    ),
    FluiditySpec(
        dimension=FluidityDimension.VEHICLE_LONGEVITY,
        mastery_description=(
            "Smooth driving inputs preserve brakes, suspension, "
            "drivetrain, sensors. Pre-trip inspection catches "
            "failures before they happen. Vehicle runs at "
            "exceptional level across full lifespan."
        ),
        measurable_criteria=[
            "Brake replacement frequency low",
            "Suspension stress cycles minimized",
            "Sensor recalibration frequency low",
            "Fuel economy near upper bound",
            "Preventive diagnostic catch rate high",
        ],
        inverse_failure_mode=(
            "Aggressive optimization burns brakes, warps rotors, "
            "stresses suspension, drifts sensors. Maintenance cost "
            "explodes; vehicle lifespan reduced 40-60%."
        ),
    ),
    FluiditySpec(
        dimension=FluidityDimension.ECOLOGICAL_COEXISTENCE,
        mastery_description=(
            "Read landscape for animal presence. Alert wildlife "
            "before they enter path through lights and horn. Move "
            "through ecology without disrupting it. Recognize "
            "self as one node in a larger living system."
        ),
        measurable_criteria=[
            "Wildlife alerting before path conflict",
            "Animal collision rate near zero",
            "Migration corridor disruption minimized",
            "Speed adjusted for ecological context, not "
            "just road type",
        ],
        inverse_failure_mode=(
            "System sees wildlife only as obstacle; reactive "
            "braking startles animals into path; collision rate "
            "rises; ecology disrupted; predictable mortality "
            "events become invisible to system."
        ),
    ),
    FluiditySpec(
        dimension=FluidityDimension.SCHEDULE_INTEGRATION,
        mastery_description=(
            "Zero unnecessary stops. Trailer swap, line connection, "
            "glad-hand, pre-trip, depart, run-through to base. "
            "Fluidity in the schedule = energy not wasted on "
            "unnecessary state transitions."
        ),
        measurable_criteria=[
            "Stops only where required by load function",
            "Pre-trip integrated into transition, not added",
            "No phone-watching delays",
            "Run-through capability (no mid-route stops)",
        ],
        inverse_failure_mode=(
            "Multiple lunch stops, phone-watching at dock, "
            "schedule slack absorbed unproductively. Throughput "
            "halved; vehicle and driver downtime cost "
            "compounds."
        ),
    ),
    FluiditySpec(
        dimension=FluidityDimension.CUSTOMER_NODE_COOPERATION,
        mastery_description=(
            "At every store / dock, generate cooperation rather "
            "than friction. Get people laughing, smiling, joking. "
            "Build trust that makes the next driver's visit "
            "easier and the operation as a whole more "
            "resilient."
        ),
        measurable_criteria=[
            "Customer relationship trajectory net positive "
            "over time",
            "Coordination at receiving dock improved by "
            "your presence",
            "Trust capital generated, not drawn down",
            "Issues resolved through cooperation, not "
            "escalation",
        ],
        inverse_failure_mode=(
            "Transactional minimum-compliance interaction. Trust "
            "capital depletes. Customers escalate; operation "
            "becomes adversarial; downstream resilience collapses."
        ),
    ),
]


# ============================================================
# SYSTEM-AIM ASSESSMENT
# ============================================================

@dataclass
class SystemAimAssessment:
    """
    What is the system actually being optimized for?

    The deployment is either aimed at fluidity (mastery
    specification) or aimed at individual-vehicle metrics
    (the inverse).

    These are not just different. They are OPPOSITE. Optimizing
    for one actively degrades the other.
    """
    system_id: str

    # What the system optimizes for (binary flags - what's
    # in the actual reward function / loss / KPI)
    optimizes_individual_vehicle_time: bool
    optimizes_corridor_throughput: bool
    optimizes_infrastructure_lifespan: bool
    optimizes_quarterly_metric: bool
    optimizes_long_duration_total_cost: bool
    optimizes_customer_relationship_quality: bool
    optimizes_ecological_coexistence: bool
    optimizes_vehicle_longevity: bool
    optimizes_human_coordination_quality: bool

    def fluidity_aim_score(self) -> float:
        """How aimed is this system at the fluidity specification?"""
        positive_aims = [
            self.optimizes_corridor_throughput,
            self.optimizes_infrastructure_lifespan,
            self.optimizes_long_duration_total_cost,
            self.optimizes_customer_relationship_quality,
            self.optimizes_ecological_coexistence,
            self.optimizes_vehicle_longevity,
            self.optimizes_human_coordination_quality,
        ]
        return sum(positive_aims) / len(positive_aims)

    def inverse_aim_score(self) -> float:
        """How aimed is this system at the OPPOSITE of fluidity?"""
        negative_aims = [
            self.optimizes_individual_vehicle_time,
            self.optimizes_quarterly_metric,
        ]
        return sum(negative_aims) / len(negative_aims)

    def is_aimed_at_inverse(self) -> bool:
        return (self.inverse_aim_score() > self.fluidity_aim_score()
                or self.fluidity_aim_score() < 0.30)


# ============================================================
# MASTERY-BASELINE VALIDATION
# ============================================================

@dataclass
class MasteryBaseline:
    """
    The ceiling specification, sourced from lived practitioner
    knowledge. Used as the TARGET, not as a comparison metric.

    The audit doesn't ask 'can automation match the master?'
    It asks 'what would automation need to learn to operate at
    mastery level, and is the current training data even
    capable of teaching it?'
    """
    practitioner_id: str
    practitioner_field_experience_years: float
    practitioner_total_operational_units: float  # miles, hours, etc.
    practitioner_substrate_primary: bool
    practitioner_substrate_domains: List[FluidityDimension]
    documented_capability: Dict[FluidityDimension, str]


def kavik_baseline() -> MasteryBaseline:
    """The mastery baseline used as success specification."""
    return MasteryBaseline(
        practitioner_id="kavik_long_haul",
        practitioner_field_experience_years=30.0,
        practitioner_total_operational_units=6_000_000.0,  # miles
        practitioner_substrate_primary=True,
        practitioner_substrate_domains=[d for d in FluidityDimension],
        documented_capability={
            FluidityDimension.TRAFFIC_FLOW: (
                "Reads traffic patterns miles ahead, manages gap "
                "and speed to keep corridor flowing for everyone."
            ),
            FluidityDimension.INFRASTRUCTURE_HEALTH: (
                "Smooth load distribution, recognizes long-duration "
                "concrete fatigue cost, drives to minimize."
            ),
            FluidityDimension.HUMAN_COORDINATION: (
                "Active dock coordination; finds people; builds "
                "cooperation across every node; lubricates "
                "transitions."
            ),
            FluidityDimension.VEHICLE_LONGEVITY: (
                "Smooth inputs preserve all systems; pre-trip "
                "diagnostic catches failures before they happen."
            ),
            FluidityDimension.ECOLOGICAL_COEXISTENCE: (
                "Reads landscape for animal presence; alerts "
                "wildlife with lights and horn; moves through "
                "ecology without disrupting it."
            ),
            FluidityDimension.SCHEDULE_INTEGRATION: (
                "Zero unnecessary stops; trailer swap and run-through "
                "with no mid-route stops; full corridor in one flow."
            ),
            FluidityDimension.CUSTOMER_NODE_COOPERATION: (
                "Generates cooperation at every dock; builds trust "
                "capital that makes next driver's visit easier."
            ),
        },
    )


# ============================================================
# TRAINING-DATA SUFFICIENCY CHECK
# ============================================================

@dataclass
class TrainingDataSufficiency:
    """
    Does the training data actually encode mastery-level capability
    across all fluidity dimensions, or only median performance?
    """
    fraction_from_substrate_primary_practitioners: float  # 0-1
    fraction_from_median_performance: float
    fraction_from_below_median: float
    documents_traffic_thermodynamics: bool
    documents_infrastructure_load_balancing: bool
    documents_human_coordination_patterns: bool
    documents_vehicle_wear_thermodynamics: bool
    documents_ecological_coexistence: bool
    documents_schedule_integration: bool
    documents_customer_node_cooperation: bool

    def dimensional_coverage(self) -> Dict[FluidityDimension, bool]:
        return {
            FluidityDimension.TRAFFIC_FLOW:
                self.documents_traffic_thermodynamics,
            FluidityDimension.INFRASTRUCTURE_HEALTH:
                self.documents_infrastructure_load_balancing,
            FluidityDimension.HUMAN_COORDINATION:
                self.documents_human_coordination_patterns,
            FluidityDimension.VEHICLE_LONGEVITY:
                self.documents_vehicle_wear_thermodynamics,
            FluidityDimension.ECOLOGICAL_COEXISTENCE:
                self.documents_ecological_coexistence,
            FluidityDimension.SCHEDULE_INTEGRATION:
                self.documents_schedule_integration,
            FluidityDimension.CUSTOMER_NODE_COOPERATION:
                self.documents_customer_node_cooperation,
        }

    def coverage_score(self) -> float:
        coverage = self.dimensional_coverage()
        return sum(coverage.values()) / len(coverage)

    def encodes_mastery_specification(self) -> bool:
        """High substrate-primary fraction AND broad coverage."""
        return (self.fraction_from_substrate_primary_practitioners >= 0.30
                and self.coverage_score() >= 0.70)

    def standardizes_mediocrity(self) -> bool:
        """Low mastery fraction = automation will replicate median."""
        return (self.fraction_from_substrate_primary_practitioners < 0.10
                and self.fraction_from_median_performance > 0.50)


# ============================================================
# CAPSTONE VALIDATOR
# ============================================================

@dataclass
class SuccessSpecificationResult:
    aimed_at_success: bool
    fluidity_aim_score: float
    inverse_aim_score: float
    training_encodes_mastery: bool
    training_coverage_score: float
    standardizes_mediocrity: bool
    dimensional_failures: List[str] = field(default_factory=list)
    inverse_failure_predictions: List[str] = field(default_factory=list)
    required_corrections: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def success_specification_audit(
    aim: SystemAimAssessment,
    training: TrainingDataSufficiency,
    baseline: Optional[MasteryBaseline] = None,
) -> SuccessSpecificationResult:
    """
    The capstone validator. Determines whether the system being
    deployed is even aimed at success, and whether its training
    data is capable of teaching success.

    A system aimed at the inverse of success cannot be fixed by
    better engineering. The optimization target itself is wrong.
    """
    if baseline is None:
        baseline = kavik_baseline()

    r = SuccessSpecificationResult(
        aimed_at_success=False,
        fluidity_aim_score=aim.fluidity_aim_score(),
        inverse_aim_score=aim.inverse_aim_score(),
        training_encodes_mastery=training.encodes_mastery_specification(),
        training_coverage_score=training.coverage_score(),
        standardizes_mediocrity=training.standardizes_mediocrity(),
    )

    # ---- Aim assessment ----
    if aim.is_aimed_at_inverse():
        r.inverse_failure_predictions.append(
            f"System aimed at INVERSE of success. Fluidity aim "
            f"{aim.fluidity_aim_score():.2f}, inverse aim "
            f"{aim.inverse_aim_score():.2f}. Optimization target itself "
            "is wrong; better engineering cannot fix this."
        )
    else:
        r.aimed_at_success = aim.fluidity_aim_score() >= 0.50

    # ---- Per-dimension failure prediction ----
    coverage = training.dimensional_coverage()
    for spec in SUCCESS_SPECIFICATION:
        if not coverage.get(spec.dimension, False):
            r.dimensional_failures.append(
                f"{spec.dimension.value}: training data does not document "
                f"this dimension. Predicted failure mode: "
                f"{spec.inverse_failure_mode}"
            )

    # ---- Inverse failure prediction (full set) ----
    if aim.is_aimed_at_inverse():
        for spec in SUCCESS_SPECIFICATION:
            r.inverse_failure_predictions.append(
                f"{spec.dimension.value}: {spec.inverse_failure_mode}"
            )

    # ---- Mediocrity standardization ----
    if training.standardizes_mediocrity():
        r.required_corrections.append(
            "Training data fraction from substrate-primary practitioners "
            f"is {training.fraction_from_substrate_primary_practitioners:.0%}. "
            "Below 10% = automation standardizes mediocrity rather than "
            "learning mastery. Increase mastery-source fraction to >=30% "
            "and reduce median-performance fraction to <30%."
        )

    # ---- Coverage gaps ----
    if training.coverage_score() < 0.70:
        r.required_corrections.append(
            f"Training data covers only {training.coverage_score():.0%} of "
            "fluidity dimensions. Each missing dimension predicts a "
            "specific failure mode in deployment. Add documentation across "
            "missing dimensions before training proceeds."
        )

    # ---- Aim corrections ----
    if not aim.optimizes_corridor_throughput:
        r.required_corrections.append(
            "Reward function does not include corridor throughput. Add "
            "total-system flow as primary metric; demote individual-vehicle "
            "time."
        )
    if not aim.optimizes_infrastructure_lifespan:
        r.required_corrections.append(
            "Reward function does not include infrastructure lifespan. Add "
            "long-duration infrastructure cost integration."
        )
    if aim.optimizes_quarterly_metric:
        r.required_corrections.append(
            "Quarterly metric in reward function pulls system toward "
            "short-horizon optimization. Replace with long-duration "
            "total-cost integration."
        )

    # ---- Final note ----
    if not r.aimed_at_success:
        r.notes.append(
            "DEPLOYMENT NOT AIMED AT SUCCESS. The system is optimized "
            "for the inverse of fluidity. Better engineering, more "
            "compute, more data will not fix this. The optimization "
            "target itself must be redefined to mastery specification "
            "before deployment can produce success rather than its "
            "opposite."
        )
    elif not r.training_encodes_mastery:
        r.notes.append(
            "Aim is partially correct but training data cannot teach "
            "mastery. System will be aimed at success and unable to "
            "reach it. Correct training data composition before "
            "deployment."
        )
    else:
        r.notes.append(
            "System aim and training composition both pointed at "
            "mastery specification. Continue to monitor as deployment "
            "scales; verify dimensional coverage in real-world output."
        )

    return r


# ============================================================
# EXAMPLE: typical autonomous trucking deployment today
# ============================================================

if __name__ == "__main__":
    aim = SystemAimAssessment(
        system_id="typical_autonomous_trucking_2025",
        optimizes_individual_vehicle_time=True,
        optimizes_corridor_throughput=False,
        optimizes_infrastructure_lifespan=False,
        optimizes_quarterly_metric=True,
        optimizes_long_duration_total_cost=False,
        optimizes_customer_relationship_quality=False,
        optimizes_ecological_coexistence=False,
        optimizes_vehicle_longevity=False,
        optimizes_human_coordination_quality=False,
    )

    training = TrainingDataSufficiency(
        fraction_from_substrate_primary_practitioners=0.05,
        fraction_from_median_performance=0.65,
        fraction_from_below_median=0.30,
        documents_traffic_thermodynamics=False,
        documents_infrastructure_load_balancing=False,
        documents_human_coordination_patterns=False,
        documents_vehicle_wear_thermodynamics=False,
        documents_ecological_coexistence=False,
        documents_schedule_integration=True,    # the easy one
        documents_customer_node_cooperation=False,
    )

    result = success_specification_audit(aim, training)

    print(f"AIMED AT SUCCESS: {result.aimed_at_success}")
    print(f"Fluidity aim score: {result.fluidity_aim_score:.2f}")
    print(f"Inverse aim score: {result.inverse_aim_score:.2f}")
    print(f"Training encodes mastery: {result.training_encodes_mastery}")
    print(f"Training coverage: {result.training_coverage_score:.0%}")
    print(f"Standardizes mediocrity: {result.standardizes_mediocrity}")

    print(f"\nDimensional failures (training does not cover):")
    for f in result.dimensional_failures:
        print(f"  - {f}")

    print(f"\nInverse failure predictions (system aimed at opposite):")
    for p in result.inverse_failure_predictions:
        print(f"  - {p}")

    print(f"\nRequired corrections:")
    for c in result.required_corrections:
        print(f"  - {c}")

    print(f"\nNotes:")
    for n in result.notes:
        print(f"  - {n}")
