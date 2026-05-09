"""
transportation_automation_audit.py

Pre-deployment audit framework for transportation automation systems.
Maps hidden dependencies as constraint layers + differential cascade.

License: CC0
Stdlib only. Falsifiable. Regionally forkable.

Architecture:
    Layer 0: Energy/thermodynamic base (power, GPS, sensor grid)
    Layer 1: Infrastructure substrate (concrete, lane markers, sensors)
    Layer 2: Data layer (map data, routing, GPS coordinates)
    Layer 3: Supply chain (parts, materials, replacement cycles)
    Layer 4: Labor thermodynamics (skill encoding, wage inversion)
    Layer 5: Climate/regional boundary conditions
    Layer 6: Vehicle-geometry-to-route matching
    Layer 7: Cascade detection (single-point failures)
    Layer 8: Skill-debt timer (atrophy under automation)

All layers couple. Failure in one propagates.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


# ============================================================
# LAYER 0: ENERGY / THERMODYNAMIC BASE
# ============================================================

@dataclass
class GPSReliability:
    """GPS as foundational assumption - usually false."""
    corridor_id: str
    canopy_obstruction_pct: float          # tree cover blocking signal
    canyon_effect_zones: int               # urban + terrain multipath
    seasonal_solar_disruption_days: int    # ionosphere events/yr
    annual_outage_hours_observed: float    # empirical, not theoretical
    coordinate_accuracy_pct: float         # how often coords match reality
    map_data_lag_days_avg: float           # update latency
    map_data_lag_days_max: float

    def reliability_score(self) -> float:
        """0.0 = unusable, 1.0 = perfect. Multiplicative because layers stack."""
        canopy = 1.0 - (self.canopy_obstruction_pct / 100)
        canyon = max(0.0, 1.0 - (self.canyon_effect_zones / 50))
        solar = max(0.0, 1.0 - (self.seasonal_solar_disruption_days / 30))
        outage = max(0.0, 1.0 - (self.annual_outage_hours_observed / 200))
        coord = self.coordinate_accuracy_pct / 100
        lag = max(0.0, 1.0 - (self.map_data_lag_days_avg / 90))
        return canopy * canyon * solar * outage * coord * lag

    def is_single_point_of_failure(self) -> bool:
        """If both automation AND human fallback rely on GPS, this is fatal."""
        return self.reliability_score() < 0.6


# ============================================================
# LAYER 1: INFRASTRUCTURE SUBSTRATE
# ============================================================

@dataclass
class InfrastructureStability:
    """Roads as constantly degrading assets, not stable platforms."""
    corridor_id: str
    frost_heave_events_per_year: int
    annual_construction_zones: int
    construction_zone_avg_duration_days: float
    flood_buckling_events_5yr: int
    heat_warping_days_per_year: int
    lane_marker_repaint_cycle_months: float
    sensor_array_durability_winters: float

    def annual_change_rate(self) -> float:
        """How many disruptive infrastructure events per year."""
        return (self.frost_heave_events_per_year
                + self.annual_construction_zones
                + self.flood_buckling_events_5yr / 5
                + self.heat_warping_days_per_year / 7)

    def map_update_lag_vs_change_ratio(self, gps: GPSReliability) -> float:
        """If change_rate > update_rate, system is always behind reality."""
        # 365 days / lag = update events per year
        update_rate = 365 / max(gps.map_data_lag_days_avg, 1)
        return self.annual_change_rate() / max(update_rate, 0.1)


# ============================================================
# LAYER 2: VEHICLE-GEOMETRY-TO-ROUTE MATCHING
# ============================================================

@dataclass
class VehicleGeometry:
    """79-ft semi can't recover from a bad route."""
    bumper_to_bumper_ft: float
    weight_lbs: int
    turning_radius_ft: float
    bridge_height_clearance_required_ft: float

    def recovery_agility(self) -> float:
        """Lower = less ability to absorb routing errors."""
        # Heavier + longer = less recovery
        return 1.0 / (1.0 + (self.weight_lbs / 80000) * (self.bumper_to_bumper_ft / 79))


# ============================================================
# LAYER 3: LABOR THERMODYNAMICS
# ============================================================

class SkillEncodingDepth(Enum):
    SUBSTRATE_PRIMARY = 0.95     # neuroplasticity-window encoded (farm kid, 6M-mile driver)
    EXPERIENCED_ADULT = 0.75     # learned through repeated consequence
    JOURNEYMAN = 0.55            # competent but not deep
    CERTIFIED_ONLY = 0.30        # passed test, no consequence-learning
    DESPERATION_HIRE = 0.15      # survival-mode, no investment in system


@dataclass
class LaborSubstrate:
    """The Mighty Atom problem: certification != capacity."""
    region_id: str
    experienced_drivers_available: int
    desperation_hires_available: int
    mechanic_generalists_remaining: int    # the Kens still working
    certified_only_mechanics: int          # standing-around class
    avg_wage_experienced: float
    avg_wage_certified: float
    knowledge_exodus_rate_per_yr: float    # old timers walking off
    farm_or_trade_background_pct: float    # substrate-primary candidates

    def wage_inversion_present(self) -> bool:
        """Is the experienced person paid LESS than certificate-holder?"""
        return self.avg_wage_experienced < self.avg_wage_certified

    def encoding_depth_score(self) -> float:
        """Weighted average of who's actually available."""
        total = (self.experienced_drivers_available
                 + self.desperation_hires_available
                 + self.mechanic_generalists_remaining
                 + self.certified_only_mechanics)
        if total == 0:
            return 0.0
        weighted = (
            self.experienced_drivers_available * SkillEncodingDepth.SUBSTRATE_PRIMARY.value
            + self.mechanic_generalists_remaining * SkillEncodingDepth.EXPERIENCED_ADULT.value
            + self.certified_only_mechanics * SkillEncodingDepth.CERTIFIED_ONLY.value
            + self.desperation_hires_available * SkillEncodingDepth.DESPERATION_HIRE.value
        )
        return weighted / total

    def is_labor_undeployable(self) -> bool:
        """Region can't actually source the skill needed."""
        return (self.encoding_depth_score() < 0.40
                or self.wage_inversion_present()
                or self.knowledge_exodus_rate_per_yr > 0.15)


# ============================================================
# LAYER 4: SKILL-DEBT TIMER (atrophy under automation)
# ============================================================

@dataclass
class SkillDebtTimer:
    """How fast does fallback competence decay when automation handles most cases?"""
    automation_handles_pct: float          # % of miles automated
    fallback_intervention_per_1k_mi: float # how often human takes over
    spatial_encoding_baseline: float       # 0-1, did driver build mental map?
    diagnostic_practice_per_shift: int     # operator self-diagnoses per shift
    years_deployed: float

    def atrophy_rate_per_year(self) -> float:
        """Substrate-primary skills decay when not exercised under consequence."""
        # The more automation handles, the less consequence-learning happens
        unused_pct = self.automation_handles_pct / 100
        return unused_pct * 0.18  # ~18%/yr for fully-handled tasks (rough empirical)

    def current_competence(self) -> float:
        """Competence = baseline * (1 - atrophy)^years."""
        decay = (1 - self.atrophy_rate_per_year()) ** self.years_deployed
        return self.spatial_encoding_baseline * decay

    def years_until_recovery_unviable(self, threshold: float = 0.35) -> float:
        """When does fallback layer become decorative?"""
        if self.current_competence() < threshold:
            return 0.0
        rate = self.atrophy_rate_per_year()
        if rate <= 0:
            return float('inf')
        # solve baseline * (1-rate)^t = threshold
        return math.log(threshold / self.spatial_encoding_baseline) / math.log(1 - rate)


# ============================================================
# LAYER 5: EDGE-CASE FAILURE ENVIRONMENT
# ============================================================

@dataclass
class EdgeCaseEnvironment:
    """Ash, mud, -30F, sensor drift. Automation tested at none of these."""
    corridor_id: str
    cold_extreme_days_below_neg20F: int
    mud_season_days: int
    ash_smoke_event_days: int
    battery_withdrawal_curve_validated: bool
    sensor_recalibration_under_stress_validated: bool
    failure_modes_documented: int
    failure_modes_estimated_total: int

    def edge_case_load_days(self) -> int:
        return (self.cold_extreme_days_below_neg20F
                + self.mud_season_days
                + self.ash_smoke_event_days)

    def failure_mode_coverage(self) -> float:
        if self.failure_modes_estimated_total == 0:
            return 0.0
        return self.failure_modes_documented / self.failure_modes_estimated_total

    def stress_validation_score(self) -> float:
        bool_score = (int(self.battery_withdrawal_curve_validated)
                      + int(self.sensor_recalibration_under_stress_validated)) / 2
        return bool_score * self.failure_mode_coverage()


# ============================================================
# LAYER 6: ACCOUNTING / HIDDEN COST MEASUREMENT
# ============================================================

@dataclass
class HiddenCostLedger:
    """What current accounting refuses to measure."""
    region_id: str
    downtime_per_failure_event_hrs: float
    failure_events_per_month: float
    coordination_overhead_per_event_hrs: float
    mechanics_dispatched_per_event: int
    actual_diagnostic_person_wage: float   # the Mighty Atom / Ken
    certified_mechanic_wage: float
    cascading_production_loss_per_hr: float

    def true_cost_per_failure(self) -> float:
        """What the books don't show."""
        labor = (self.coordination_overhead_per_event_hrs
                 * self.mechanics_dispatched_per_event
                 * self.certified_mechanic_wage)
        downtime = self.downtime_per_failure_event_hrs * self.cascading_production_loss_per_hr
        return labor + downtime

    def value_inversion_ratio(self) -> float:
        """If certified > experienced wage, system is paying for credentials, not output."""
        if self.actual_diagnostic_person_wage == 0:
            return float('inf')
        return self.certified_mechanic_wage / self.actual_diagnostic_person_wage


# ============================================================
# LAYER 7: CASCADE DETECTION
# ============================================================

@dataclass
class CascadeAuditResult:
    deployable: bool
    failure_modes: List[str] = field(default_factory=list)
    single_points_of_failure: List[str] = field(default_factory=list)
    skill_debt_horizon_years: float = 0.0
    estimated_true_cost_multiplier: float = 1.0
    notes: List[str] = field(default_factory=list)


def cascade_audit(
    gps: GPSReliability,
    infra: InfrastructureStability,
    vehicle: VehicleGeometry,
    labor: LaborSubstrate,
    skill_debt: SkillDebtTimer,
    edge: EdgeCaseEnvironment,
    cost: HiddenCostLedger,
) -> CascadeAuditResult:
    """
    Run all coupled constraint checks. Any single critical failure
    flips deployable to False. This is the differential cascade:
    failure in one layer propagates to dependent layers.
    """
    r = CascadeAuditResult(deployable=True)

    # ---- GPS / data layer ----
    if gps.is_single_point_of_failure():
        r.deployable = False
        r.single_points_of_failure.append(
            f"GPS reliability {gps.reliability_score():.2f} - both "
            f"automation and human fallback depend on same corrupted data layer"
        )

    # ---- Infrastructure volatility vs map update lag ----
    ratio = infra.map_update_lag_vs_change_ratio(gps)
    if ratio > 1.0:
        r.deployable = False
        r.failure_modes.append(
            f"Infrastructure changes {ratio:.1f}x faster than map updates. "
            "Routing data is structurally behind reality."
        )

    # ---- Vehicle geometry vs recovery ----
    agility = vehicle.recovery_agility()
    if agility < 0.4 and ratio > 0.5:
        r.failure_modes.append(
            f"Vehicle agility {agility:.2f} too low to absorb routing errors "
            f"in volatile infrastructure (ratio {ratio:.1f}). "
            "79-ft rig cannot reroute mid-maneuver."
        )

    # ---- Labor undeployable ----
    if labor.is_labor_undeployable():
        r.deployable = False
        r.failure_modes.append(
            f"Region labor-undeployable: encoding depth {labor.encoding_depth_score():.2f}, "
            f"wage inversion={labor.wage_inversion_present()}, "
            f"exodus rate={labor.knowledge_exodus_rate_per_yr:.2f}/yr"
        )

    # ---- Skill-debt timer ----
    horizon = skill_debt.years_until_recovery_unviable()
    r.skill_debt_horizon_years = horizon
    if horizon < 5.0:
        r.failure_modes.append(
            f"Fallback competence becomes decorative in {horizon:.1f} years. "
            "Automation creates atrophy faster than skill can be replenished."
        )

    # ---- Edge-case validation ----
    sv = edge.stress_validation_score()
    if sv < 0.5 and edge.edge_case_load_days() > 30:
        r.deployable = False
        r.failure_modes.append(
            f"Edge-case validation {sv:.2f} with {edge.edge_case_load_days()} stress-days/yr. "
            "System untested at the conditions where it will operate."
        )

    # ---- Hidden cost / accounting inversion ----
    inversion = cost.value_inversion_ratio()
    if inversion > 1.5:
        r.notes.append(
            f"Wage-to-capacity inversion {inversion:.2f}: paying for credentials, "
            "not thermodynamic output. Pattern matches manufacturing cascade-failure precedent."
        )

    # True cost multiplier for deployment
    base_failure_cost = cost.true_cost_per_failure() * cost.failure_events_per_month * 12
    # Skill atrophy compounds this over time
    r.estimated_true_cost_multiplier = 1.0 + (
        (1 - skill_debt.current_competence()) * 2.5
    )

    if r.deployable:
        r.notes.append("Deployment viable under current constraint layer values.")
    else:
        r.notes.append(
            "DEPLOYMENT NOT VIABLE. Forcing deployment guarantees cascade failure "
            "with cost detonation in 3-7 year window."
        )

    return r


# ============================================================
# DIFFERENTIAL CASCADE: layer coupling
# ============================================================

def differential_cascade_step(
    gps_score: float,
    infra_change_rate: float,
    labor_depth: float,
    skill_debt_years: float,
    dt: float = 1.0,
) -> Dict[str, float]:
    """
    Single time-step of coupled differential equations.
    Each layer feeds into the next. Run iteratively for trajectory.

    dGPS/dt   = -alpha * infra_change_rate / 365   (data lag accumulates)
    dInfra/dt = +beta  * climate_stress            (infrastructure degrades)
    dLabor/dt = -gamma * automation_pct - exodus   (skill walks off)
    dDebt/dt  = +delta * (1 - labor_depth)         (debt grows when skill thin)
    """
    alpha, beta, gamma, delta = 0.02, 0.05, 0.08, 0.12

    d_gps = -alpha * (infra_change_rate / 365) * dt
    d_infra = +beta * dt  # climate stress proxy
    d_labor = -gamma * dt
    d_debt = +delta * (1 - labor_depth) * dt

    return {
        "gps_score": max(0.0, gps_score + d_gps),
        "infra_change_rate": infra_change_rate + d_infra,
        "labor_depth": max(0.0, labor_depth + d_labor),
        "skill_debt_years": max(0.0, skill_debt_years - d_debt),
    }


if __name__ == "__main__":
    # Example: Tomah-Superior corridor, food distribution
    gps = GPSReliability(
        corridor_id="tomah_superior",
        canopy_obstruction_pct=35.0,
        canyon_effect_zones=12,
        seasonal_solar_disruption_days=8,
        annual_outage_hours_observed=140.0,
        coordinate_accuracy_pct=78.0,
        map_data_lag_days_avg=45.0,
        map_data_lag_days_max=180.0,
    )
    infra = InfrastructureStability(
        corridor_id="tomah_superior",
        frost_heave_events_per_year=22,
        annual_construction_zones=47,
        construction_zone_avg_duration_days=32.0,
        flood_buckling_events_5yr=6,
        heat_warping_days_per_year=18,
        lane_marker_repaint_cycle_months=14.0,
        sensor_array_durability_winters=3.5,
    )
    vehicle = VehicleGeometry(
        bumper_to_bumper_ft=79.0, weight_lbs=80000,
        turning_radius_ft=55.0, bridge_height_clearance_required_ft=13.6,
    )
    labor = LaborSubstrate(
        region_id="upper_midwest_rural",
        experienced_drivers_available=120,
        desperation_hires_available=400,
        mechanic_generalists_remaining=18,
        certified_only_mechanics=85,
        avg_wage_experienced=26.0,
        avg_wage_certified=67.0,
        knowledge_exodus_rate_per_yr=0.22,
        farm_or_trade_background_pct=14.0,
    )
    skill_debt = SkillDebtTimer(
        automation_handles_pct=85.0,
        fallback_intervention_per_1k_mi=2.4,
        spatial_encoding_baseline=0.85,
        diagnostic_practice_per_shift=1,
        years_deployed=4.0,
    )
    edge = EdgeCaseEnvironment(
        corridor_id="tomah_superior",
        cold_extreme_days_below_neg20F=22,
        mud_season_days=35,
        ash_smoke_event_days=14,
        battery_withdrawal_curve_validated=False,
        sensor_recalibration_under_stress_validated=False,
        failure_modes_documented=42,
        failure_modes_estimated_total=180,
    )
    cost = HiddenCostLedger(
        region_id="upper_midwest_rural",
        downtime_per_failure_event_hrs=4.5,
        failure_events_per_month=6.5,
        coordination_overhead_per_event_hrs=3.0,
        mechanics_dispatched_per_event=4,
        actual_diagnostic_person_wage=22.0,
        certified_mechanic_wage=67.0,
        cascading_production_loss_per_hr=850.0,
    )

    result = cascade_audit(gps, infra, vehicle, labor, skill_debt, edge, cost)
    print(f"DEPLOYABLE: {result.deployable}")
    print(f"Skill-debt horizon: {result.skill_debt_horizon_years:.1f} yrs")
    print(f"True cost multiplier: {result.estimated_true_cost_multiplier:.2f}x")
    print("\nFailure modes:")
    for f in result.failure_modes:
        print(f"  - {f}")
    print("\nSingle points of failure:")
    for s in result.single_points_of_failure:
        print(f"  - {s}")
    print("\nNotes:")
    for n in result.notes:
        print(f"  - {n}")
