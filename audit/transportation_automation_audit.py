"""
transportation_automation_audit.py

Pre-deployment audit framework for transportation automation systems.
Maps hidden dependencies as constraint layers + differential cascade.

License: CC0
Stdlib only. Falsifiable. Regionally forkable.

Architecture:
    Layer 0:  Energy/thermodynamic base (power, GPS, sensor grid)
    Layer 1:  Infrastructure substrate (concrete, lane markers, sensors)
    Layer 2:  Data layer (map data, routing, GPS coordinates)
    Layer 3:  Vehicle geometry vs route recovery
    Layer 4:  Labor thermodynamics (skill encoding, wage inversion)
    Layer 5:  Skill-debt timer (atrophy under automation)
    Layer 6:  Edge-case environment (ash, mud, -30F, sensor drift)
    Layer 7:  Hidden cost ledger (what accounting refuses to measure)
    Layer 8:  Traffic thermodynamics (load-balancing vs shock-wave)
    Layer 9:  Vehicle wear thermodynamics (driving-style cost)
    Layer 10: Social backlash coefficient (induced-conflict accidents)
    Layer 11: Infrastructure long-duration integrator (5-10yr cascades)
    Layer 12: False-accounting detector (apples-to-oranges flagging)
    Layer 13: Cascade detection (couples all layers)
    Layer 14: Differential cascade step (time-evolution)

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
# LAYER 8: TRAFFIC THERMODYNAMICS (load-balancing vs shock-wave)
# ============================================================

@dataclass
class TrafficThermodynamics:
    """
    Skilled drivers act as load-balancing nodes: they manage gap-as-function-
    of-speed, absorb merges, position to enable fair flow. Aggressive drivers
    and naive automation generate shock waves that propagate backward.

    A skilled driver's actual throughput is HIGHER over 1000 miles because
    they don't sit in chaos they generated. The 3% individual gain is fiction.
    """
    corridor_id: str
    fairness_encoded_drivers_pct: float         # % who absorb merges, share lanes
    aggressive_driver_pct: float                # cut merges, exploit gaps
    automation_following_distance_ft: float     # rigid following = shock wave
    automation_optimizes_individual_only: bool  # vs corridor throughput
    avg_merge_density_per_mile: float           # how many merges per mile
    bottleneck_zones_per_corridor: int

    def shock_wave_amplification(self) -> float:
        """0 = pure load-balancing, 1 = maximum oscillation."""
        # Tight following + aggressive culture + individual-only optimization
        rigid = max(0.0, 1.0 - (self.automation_following_distance_ft / 60))
        aggressive = self.aggressive_driver_pct / 100
        individual = 0.4 if self.automation_optimizes_individual_only else 0.0
        return min(1.0, rigid * 0.5 + aggressive * 0.3 + individual)

    def corridor_throughput_loss_pct(self) -> float:
        """How much actual throughput is lost to shock waves."""
        sw = self.shock_wave_amplification()
        # More merges = more amplification opportunity
        merge_factor = min(1.0, self.avg_merge_density_per_mile / 3.0)
        return sw * merge_factor * 100

    def fairness_capacity_collapsed(self) -> bool:
        """Has skilled-driver exodus already broken load-balancing?"""
        return self.fairness_encoded_drivers_pct < 15.0


# ============================================================
# LAYER 9: VEHICLE WEAR THERMODYNAMICS (driving-style cost)
# ============================================================

@dataclass
class VehicleWearThermodynamics:
    """
    Aggressive driving style burns brakes, warps rotors, stresses suspension,
    drifts sensors, decreases fuel economy. Smooth-flow driving extends
    vehicle lifespan dramatically. Over 6M miles, the difference is huge.

    Current accounting measures "trip time saved" but not "$40K bearing
    replacement at year 4 because driving style amplified stress cycles."
    """
    annual_brake_replacements_aggressive: float
    annual_brake_replacements_smooth: float
    suspension_stress_cycles_aggressive: int
    suspension_stress_cycles_smooth: int
    sensor_recalibration_freq_aggressive_per_mo: float
    sensor_recalibration_freq_smooth_per_mo: float
    fuel_economy_mpg_aggressive: float
    fuel_economy_mpg_smooth: float
    annual_miles: int

    def maintenance_cost_differential(
        self,
        brake_cost: float = 1800,
        suspension_cost_per_cycle: float = 0.18,
        sensor_recal_cost: float = 240,
        fuel_cost_per_gal: float = 4.10,
    ) -> float:
        """Annual cost penalty of aggressive driving style."""
        brake_diff = (self.annual_brake_replacements_aggressive
                      - self.annual_brake_replacements_smooth) * brake_cost
        susp_diff = (self.suspension_stress_cycles_aggressive
                     - self.suspension_stress_cycles_smooth) * suspension_cost_per_cycle
        sensor_diff = ((self.sensor_recalibration_freq_aggressive_per_mo
                        - self.sensor_recalibration_freq_smooth_per_mo)
                       * 12 * sensor_recal_cost)
        # Fuel: gallons used = miles / mpg, diff in gallons * cost
        if self.fuel_economy_mpg_aggressive > 0 and self.fuel_economy_mpg_smooth > 0:
            fuel_diff = (
                (self.annual_miles / self.fuel_economy_mpg_aggressive
                 - self.annual_miles / self.fuel_economy_mpg_smooth)
                * fuel_cost_per_gal
            )
        else:
            fuel_diff = 0.0
        return brake_diff + susp_diff + sensor_diff + fuel_diff

    def lifespan_reduction_pct(self) -> float:
        """How much shorter vehicle service life under aggressive style."""
        # Heuristic: stress cycles dominate
        if self.suspension_stress_cycles_smooth == 0:
            return 0.0
        ratio = (self.suspension_stress_cycles_aggressive
                 / self.suspension_stress_cycles_smooth)
        return min(60.0, max(0.0, (ratio - 1.0) * 100))


# ============================================================
# LAYER 10: SOCIAL BACKLASH COEFFICIENT (induced-conflict accidents)
# ============================================================

@dataclass
class SocialBacklash:
    """
    Aggressive trucks/automation create hostility. Smaller vehicles will
    bait, brake-check, set up induced-collision scenarios, especially when
    they perceive the offender as automation. Skilled drivers carrying
    fairness norms get cooperation. Aggressive ones get baited.

    Insurance/liability cost gets buried in different line items so it
    looks unrelated to driving-style choice.
    """
    corridor_id: str
    induced_collision_attempts_per_yr_aggressive: float
    induced_collision_attempts_per_yr_smooth: float
    avg_claim_per_incident: float
    automation_perceived_as_aggressive: bool
    public_anti_automation_sentiment: float    # 0-1

    def annual_backlash_cost(self) -> float:
        diff = (self.induced_collision_attempts_per_yr_aggressive
                - self.induced_collision_attempts_per_yr_smooth)
        multiplier = 1.0
        if self.automation_perceived_as_aggressive:
            multiplier += 0.5
        multiplier += self.public_anti_automation_sentiment * 0.4
        return diff * self.avg_claim_per_incident * multiplier

    def backlash_amplifies_with_automation(self) -> bool:
        return (self.automation_perceived_as_aggressive
                and self.public_anti_automation_sentiment > 0.4)


# ============================================================
# LAYER 11: INFRASTRUCTURE LONG-DURATION INTEGRATOR
# ============================================================

@dataclass
class InfrastructureLongDuration:
    """
    Quarterly metrics ignore 5-10yr concrete fatigue, pavement thermal
    stress, bearing wear from sustained shock-wave loading. Each year of
    aggressive-style traffic accelerates next year's construction load,
    which compounds the volatility that breaks routing data.

    Externalizing infrastructure cost is accounting fiction.
    """
    corridor_id: str
    concrete_fatigue_baseline_yrs: float       # design life, no shock loading
    shock_wave_acceleration_factor: float      # 1.0 = none, 2.0 = doubles wear
    pavement_thermal_stress_amplifier: float   # stop-go heat cycling
    annual_repair_budget_baseline: float
    construction_zone_growth_rate_yoy: float   # % more zones each year

    def effective_concrete_life_yrs(self) -> float:
        if self.shock_wave_acceleration_factor <= 0:
            return self.concrete_fatigue_baseline_yrs
        return (self.concrete_fatigue_baseline_yrs
                / self.shock_wave_acceleration_factor)

    def cumulative_repair_cost(self, years: int = 10) -> float:
        """Compounding construction cost over deployment lifetime."""
        total = 0.0
        budget = self.annual_repair_budget_baseline
        for _ in range(years):
            total += budget
            budget *= (1 + self.construction_zone_growth_rate_yoy)
        return total

    def cascade_detonation_year(self) -> float:
        """Year when repair cost exceeds 2x baseline (rough tipping point)."""
        if self.construction_zone_growth_rate_yoy <= 0:
            return float('inf')
        return math.log(2) / math.log(1 + self.construction_zone_growth_rate_yoy)


# ============================================================
# LAYER 12: FALSE-ACCOUNTING DETECTOR
# ============================================================

@dataclass
class FalseAccountingFlags:
    """
    The 3% efficiency narrative is built on false comparisons:
      - Automation runs nonstop; human required to take 30-min break
        (regulation, not biology). Comparing them isn't apples-to-apples.
      - Time-to-destination measured; infrastructure wear externalized.
      - Aggressive style measured for individual gain; corridor throughput
        ignored.
      - Maintenance, claims, fuel buried in separate ledgers.

    Module flags these comparisons as not valid for deployment decisions.
    """
    automation_break_constraint_imposed: bool         # is auto held to driver rules?
    infrastructure_cost_externalized: bool
    accident_claims_in_separate_ledger: bool
    maintenance_cost_in_separate_ledger: bool
    fuel_cost_normalized_per_unit: bool
    measures_corridor_throughput_not_just_individual: bool

    def false_comparison_count(self) -> int:
        """How many ledger inversions are present."""
        return sum([
            not self.automation_break_constraint_imposed,
            self.infrastructure_cost_externalized,
            self.accident_claims_in_separate_ledger,
            self.maintenance_cost_in_separate_ledger,
            not self.fuel_cost_normalized_per_unit,
            not self.measures_corridor_throughput_not_just_individual,
        ])

    def is_efficiency_claim_credible(self) -> bool:
        """If 3+ inversions present, the claimed gains are accounting fiction."""
        return self.false_comparison_count() < 3


# ============================================================
# LAYER 13: CASCADE DETECTION
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
    traffic: TrafficThermodynamics,
    wear: VehicleWearThermodynamics,
    backlash: SocialBacklash,
    longdur: InfrastructureLongDuration,
    accounting: FalseAccountingFlags,
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

    # ---- Traffic thermodynamics ----
    sw = traffic.shock_wave_amplification()
    if sw > 0.5:
        r.failure_modes.append(
            f"Shock-wave amplification {sw:.2f}: automation generates traffic "
            f"oscillations that REDUCE corridor throughput by "
            f"{traffic.corridor_throughput_loss_pct():.1f}%. "
            "Individual-vehicle optimization is systemically destructive."
        )
    if traffic.fairness_capacity_collapsed():
        r.failure_modes.append(
            f"Fairness-encoding collapsed: only {traffic.fairness_encoded_drivers_pct:.1f}% "
            "of drivers do load-balancing. Automation cannot replace what's already gone."
        )

    # ---- Vehicle wear thermodynamics ----
    annual_wear_penalty = wear.maintenance_cost_differential()
    if annual_wear_penalty > 5000:
        r.notes.append(
            f"Aggressive driving style adds ${annual_wear_penalty:,.0f}/yr in "
            f"maintenance + fuel cost per vehicle. Lifespan reduction "
            f"{wear.lifespan_reduction_pct():.1f}%. Erases claimed time savings."
        )

    # ---- Social backlash ----
    backlash_cost = backlash.annual_backlash_cost()
    if backlash_cost > 0:
        r.notes.append(
            f"Social backlash cost ${backlash_cost:,.0f}/yr from induced-collision "
            f"attempts. Amplified by automation perception="
            f"{backlash.backlash_amplifies_with_automation()}."
        )

    # ---- Infrastructure long-duration ----
    detonation = longdur.cascade_detonation_year()
    eff_life = longdur.effective_concrete_life_yrs()
    cumulative_10yr = longdur.cumulative_repair_cost(10)
    if detonation < 7:
        r.failure_modes.append(
            f"Infrastructure cascade detonation in year {detonation:.1f}. "
            f"Concrete effective life reduced to {eff_life:.1f} yrs. "
            f"10-yr cumulative repair cost: ${cumulative_10yr:,.0f}."
        )

    # ---- False accounting ----
    if not accounting.is_efficiency_claim_credible():
        r.deployable = False
        r.failure_modes.append(
            f"Efficiency claims rest on {accounting.false_comparison_count()} "
            "false comparisons (regulation-imposed constraints, externalized "
            "infrastructure cost, hidden maintenance/claims/fuel). "
            "Deployment justification is accounting fiction."
        )

    # True cost multiplier including new layers
    base_failure_cost = cost.true_cost_per_failure() * cost.failure_events_per_month * 12
    r.estimated_true_cost_multiplier = 1.0 + (
        (1 - skill_debt.current_competence()) * 2.5
        + sw * 0.6
        + (annual_wear_penalty / 50000)
        + (backlash_cost / 100000)
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
    traffic = TrafficThermodynamics(
        corridor_id="tomah_superior",
        fairness_encoded_drivers_pct=8.0,           # old-timers gone
        aggressive_driver_pct=42.0,
        automation_following_distance_ft=15.0,      # rigid following
        automation_optimizes_individual_only=True,
        avg_merge_density_per_mile=1.8,
        bottleneck_zones_per_corridor=12,
    )
    wear = VehicleWearThermodynamics(
        annual_brake_replacements_aggressive=3.5,
        annual_brake_replacements_smooth=1.0,
        suspension_stress_cycles_aggressive=180000,
        suspension_stress_cycles_smooth=70000,
        sensor_recalibration_freq_aggressive_per_mo=4.0,
        sensor_recalibration_freq_smooth_per_mo=1.0,
        fuel_economy_mpg_aggressive=5.6,
        fuel_economy_mpg_smooth=7.2,
        annual_miles=130000,
    )
    backlash = SocialBacklash(
        corridor_id="tomah_superior",
        induced_collision_attempts_per_yr_aggressive=4.5,
        induced_collision_attempts_per_yr_smooth=0.4,
        avg_claim_per_incident=38000.0,
        automation_perceived_as_aggressive=True,
        public_anti_automation_sentiment=0.55,
    )
    longdur = InfrastructureLongDuration(
        corridor_id="tomah_superior",
        concrete_fatigue_baseline_yrs=25.0,
        shock_wave_acceleration_factor=1.7,         # tight following amplifies wear
        pavement_thermal_stress_amplifier=1.3,
        annual_repair_budget_baseline=2_400_000.0,
        construction_zone_growth_rate_yoy=0.12,     # 12%/yr more zones
    )
    accounting = FalseAccountingFlags(
        automation_break_constraint_imposed=False,  # auto runs nonstop, driver doesn't
        infrastructure_cost_externalized=True,
        accident_claims_in_separate_ledger=True,
        maintenance_cost_in_separate_ledger=True,
        fuel_cost_normalized_per_unit=False,
        measures_corridor_throughput_not_just_individual=False,
    )

    result = cascade_audit(
        gps, infra, vehicle, labor, skill_debt, edge, cost,
        traffic, wear, backlash, longdur, accounting,
    )
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
