"""
regulation_lcd_incentive_audit.py

Add-on audit module for transportation_automation_audit.py
(also stands alone for any domain).

Detects three coupled structural failure patterns:

  1. LOWEST-COMMON-DENOMINATOR REGULATION
     Rules built around the worst-performing (or most-degraded)
     baseline, then applied universally. Treats regulation as
     science when it's really induced-deficit compensation.

  2. INDUCED-DEFICIT FEEDBACK LOOP
     System creates the condition (bad food, sleep deprivation,
     stress, skill atrophy), regulates against the symptom,
     then uses the regulation as justification for further
     restriction or replacement.

  3. INCENTIVE-STRUCTURE CYCLING
     Same financial / regulatory / lobbying actors recreate the
     same degradation pattern across each new technology
     generation. Tool changes; incentive doesn't. Outcome
     doesn't.

These three couple. LCD regulation requires induced deficit
to justify itself; induced deficit requires the incentive
structure that profits from degradation; the incentive
structure requires regulatory capture to remain unchanged.

Breaking any one breaks the loop.

License: CC0
Stdlib only. Falsifiable. Domain-agnostic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum


# ============================================================
# DOMAIN CLASSIFICATION
# ============================================================

class RegulatedDomain(Enum):
    TRANSPORTATION = "transportation"
    MANUFACTURING = "manufacturing"
    HEALTHCARE = "healthcare"
    AGRICULTURE = "agriculture"
    EDUCATION = "education"
    AI_DEPLOYMENT = "ai_deployment"
    LABOR_GENERAL = "labor_general"
    FOOD_SYSTEMS = "food_systems"
    HOUSING = "housing"
    ENERGY = "energy"


# ============================================================
# LAYER 1: LOWEST-COMMON-DENOMINATOR REGULATION
# ============================================================

@dataclass
class LCDRegulation:
    """
    A regulation built around the worst-performing baseline,
    applied universally regardless of actual capability.

    Examples:
      - Mandatory 30-min trucker break: based on sleep-deprived,
        malnourished baseline; applied to athlete-level drivers
        also.
      - One-size school curriculum: based on attention-degraded
        baseline; applied to high-encoding-depth learners also.
      - Standard medical dosing: based on average-but-degraded
        adult; applied to highly metabolically variable patients.
    """
    regulation_id: str
    domain: RegulatedDomain
    baseline_population_capacity: float        # 0-1, capability of population
                                               # used to set the rule
    healthy_population_capacity: float         # 0-1, what's actually possible
                                               # in non-degraded subjects
    applied_to_full_capability_range: bool     # is rule universal regardless?
    individual_assessment_permitted: bool      # can capable individuals be tested?
    rule_specifies_uniform_constraint: bool    # one number for everyone?

    def lcd_compression_ratio(self) -> float:
        """How much the rule constrains capable individuals.
        1.0 = no compression, 0.0 = total compression of capable to LCD."""
        if self.healthy_population_capacity == 0:
            return 1.0
        return self.baseline_population_capacity / self.healthy_population_capacity

    def is_lcd_imposed(self) -> bool:
        """Does the rule force capable individuals down to incapable level?"""
        return (self.lcd_compression_ratio() < 0.6
                and self.applied_to_full_capability_range
                and not self.individual_assessment_permitted)

    def capable_individuals_constrained_pct(self) -> float:
        """What fraction of regulated population is held below their actual
        capability."""
        if not self.is_lcd_imposed():
            return 0.0
        # Rough: capable population assumed to be ~30-50% if healthy baseline
        # exists
        compression = 1.0 - self.lcd_compression_ratio()
        return min(100.0, compression * 80)


# ============================================================
# LAYER 2: INDUCED-DEFICIT DETECTION
# ============================================================

@dataclass
class InducedDeficitChain:
    """
    Detects when a population's degraded condition was CAUSED by
    upstream system choices, not by inherent biology.

    Trucker example:
      bad food along corridors -> metabolic dysfunction
      poor sleep environments -> chronic sleep debt
      stress + isolation -> elevated cortisol
      => sleep apnea, fatigue, error rates rise
      => regulation imposed
      => regulation cited as proof "drivers can't self-regulate"
      => automation justified

    The deficit is INDUCED. Not measured. Not innate.
    """
    deficit_id: str
    domain: RegulatedDomain

    # Upstream causes (system-controlled)
    upstream_food_quality: float                # 0-1
    upstream_sleep_environment: float           # 0-1
    upstream_stress_load: float                 # 0-1, higher = more stress
    upstream_skill_training_quality: float      # 0-1
    upstream_economic_pressure: float           # 0-1, higher = more desperation

    # Observed deficit (system-measured)
    observed_population_dysfunction_rate: float  # 0-1

    # System response
    deficit_attributed_to_inherent_biology: bool
    upstream_causes_addressed: bool
    deficit_used_to_justify_regulation: bool
    deficit_used_to_justify_replacement: bool   # automation, etc.

    def upstream_degradation_score(self) -> float:
        """How much the system itself created the deficit."""
        # Lower scores in upstream variables = more system-induced damage
        food_pressure = 1.0 - self.upstream_food_quality
        sleep_pressure = 1.0 - self.upstream_sleep_environment
        skill_pressure = 1.0 - self.upstream_skill_training_quality
        return (food_pressure + sleep_pressure + self.upstream_stress_load
                + skill_pressure + self.upstream_economic_pressure) / 5

    def is_induced_deficit(self) -> bool:
        """High upstream degradation correlated with observed dysfunction
        AND no addressing of upstream causes."""
        return (self.upstream_degradation_score() > 0.5
                and self.observed_population_dysfunction_rate > 0.3
                and not self.upstream_causes_addressed)

    def is_circular_justification(self) -> bool:
        """The deepest pattern: induce deficit, then cite deficit as
        reason for the regulation/replacement that profits from it."""
        return (self.is_induced_deficit()
                and self.deficit_used_to_justify_regulation
                and self.deficit_attributed_to_inherent_biology)

    def fuels_replacement_narrative(self) -> bool:
        """Is the induced deficit being weaponized to justify
        automation/displacement?"""
        return (self.is_induced_deficit()
                and self.deficit_used_to_justify_replacement)


# ============================================================
# LAYER 3: INCENTIVE-STRUCTURE CYCLING
# ============================================================

@dataclass
class IncentiveActor:
    """A financial / political actor in the incentive structure."""
    actor_id: str
    profits_from_degradation: bool          # cheaper labor, more turnover
    profits_from_regulation: bool           # compliance industry, lawyers
    profits_from_replacement: bool          # automation vendors, consultants
    has_lobbying_presence: bool
    same_actor_across_generations: bool     # was this actor in prior cycle?


@dataclass
class IncentiveCycle:
    """
    Tracks one cycle of: degrade -> regulate -> replace -> profit.
    Each cycle leaves the actors enriched and the population
    further degraded, with new tool/regulation/promise.

    Pattern across cycles:
      Cycle N:   Workers degraded -> regulations imposed ->
                 automation deployed -> automation degrades same way ->
                 next-gen automation promised
      Cycle N+1: Same incentive structure -> same outcome
    """
    cycle_id: str
    domain: RegulatedDomain
    cycle_number: int                       # 1, 2, 3... for that domain
    actors: List[IncentiveActor]

    # The pattern markers
    cost_externalization_present: bool
    maintenance_treated_as_overhead: bool
    regulatory_capture_present: bool
    liability_shifted_downstream: bool
    quarterly_metric_dominance: bool
    skilled_practitioners_displaced: bool
    rehires_from_desperation_pool: bool
    failure_blamed_on_tool_or_user: bool    # never on incentive structure
    new_tool_promised_to_fix_it: bool       # next cycle starts here

    def actors_carrying_over_count(self) -> int:
        return sum(1 for a in self.actors if a.same_actor_across_generations)

    def degradation_pattern_score(self) -> float:
        """How fully does this cycle reproduce the degrading pattern?"""
        flags = [
            self.cost_externalization_present,
            self.maintenance_treated_as_overhead,
            self.regulatory_capture_present,
            self.liability_shifted_downstream,
            self.quarterly_metric_dominance,
            self.skilled_practitioners_displaced,
            self.rehires_from_desperation_pool,
            self.failure_blamed_on_tool_or_user,
            self.new_tool_promised_to_fix_it,
        ]
        return sum(flags) / len(flags)

    def will_repeat(self) -> bool:
        """Does this cycle have all the markers needed to recur?"""
        return (self.degradation_pattern_score() > 0.6
                and self.actors_carrying_over_count() >= 2
                and self.new_tool_promised_to_fix_it)


# ============================================================
# LAYER 4: COUPLED PATTERN DETECTION
# ============================================================

@dataclass
class CoupledFailureResult:
    pattern_active: bool
    individual_layers_active: Dict[str, bool] = field(default_factory=dict)
    severity_score: float = 0.0                # 0-1
    predicted_repetition_count: int = 0
    breaking_intervention_points: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def coupled_pattern_audit(
    lcd: LCDRegulation,
    deficit: InducedDeficitChain,
    cycle: IncentiveCycle,
) -> CoupledFailureResult:
    """
    The three layers couple:

      LCD regulation     <- requires induced deficit to justify itself
      Induced deficit    <- requires incentive structure that profits
                            from degradation
      Incentive cycling  <- requires regulatory capture to remain
                            unchanged across cycles

    All three present = self-reinforcing degradation loop.
    Breaking ANY ONE breaks the loop.
    """
    r = CoupledFailureResult(pattern_active=False)

    lcd_active = lcd.is_lcd_imposed()
    deficit_active = deficit.is_induced_deficit()
    circular_active = deficit.is_circular_justification()
    fuels_replacement = deficit.fuels_replacement_narrative()
    cycle_will_repeat = cycle.will_repeat()

    r.individual_layers_active = {
        "lcd_regulation_imposed": lcd_active,
        "induced_deficit_present": deficit_active,
        "circular_justification": circular_active,
        "fuels_replacement_narrative": fuels_replacement,
        "incentive_cycle_will_repeat": cycle_will_repeat,
    }

    # Pattern is active if any TWO of the three core layers fire
    core_active = sum([lcd_active, deficit_active, cycle_will_repeat])
    r.pattern_active = core_active >= 2

    # Severity
    severity = 0.0
    if lcd_active:
        severity += lcd.capable_individuals_constrained_pct() / 100 * 0.30
    if deficit_active:
        severity += deficit.upstream_degradation_score() * 0.35
    if cycle_will_repeat:
        severity += cycle.degradation_pattern_score() * 0.35
    r.severity_score = min(1.0, severity)

    # Predict how many more cycles before structural collapse
    # (rough: each cycle compounds, ceiling around 4-6 before collapse)
    if cycle_will_repeat:
        remaining = max(0, 5 - cycle.cycle_number)
        r.predicted_repetition_count = remaining

    # Where can the loop be broken?
    if lcd_active:
        r.breaking_intervention_points.append(
            "Replace LCD regulation with capability-tiered assessment. "
            "Allow capable individuals to operate at actual capacity "
            "with documented competence rather than universal constraint."
        )
    if deficit_active:
        r.breaking_intervention_points.append(
            "Address upstream causes (food quality, sleep environment, "
            "stress load, skill training) instead of regulating the symptom. "
            "Healthy baseline measurement required before any regulation."
        )
    if circular_active:
        r.breaking_intervention_points.append(
            "Forbid use of induced-deficit metrics as justification for "
            "regulation or replacement. Require independent measurement of "
            "healthy-baseline capability."
        )
    if fuels_replacement:
        r.breaking_intervention_points.append(
            "Block automation/displacement justified by induced-deficit "
            "performance. Require comparison against healthy-baseline humans, "
            "not against system-degraded baseline."
        )
    if cycle_will_repeat:
        r.breaking_intervention_points.append(
            "Disallow cycle continuation by same actors: regulatory recusal "
            "for actors profiting from the prior degradation cycle. "
            "Liability and maintenance must be internalized to deployer."
        )

    # Notes
    if r.pattern_active and r.severity_score > 0.7:
        r.notes.append(
            "STRUCTURAL FAILURE LOOP ACTIVE. Self-reinforcing degradation "
            "across cycles. Each tool generation will repeat the pattern "
            "until the incentive structure is changed."
        )
    elif r.pattern_active:
        r.notes.append(
            "Failure loop forming. Intervention required at any of the "
            "three layers to break the cycle."
        )
    else:
        r.notes.append(
            "Pattern not currently active. Monitor for emergence as "
            "deployment / regulation / actor structure evolves."
        )

    return r


# ============================================================
# CROSS-DOMAIN PATTERN MATCHING
# ============================================================

@dataclass
class CrossDomainPattern:
    """A documented case of the LCD/deficit/incentive loop in
    another domain. Useful for empirical landscape grounding."""
    case_id: str
    domain: RegulatedDomain
    description: str
    lcd_regulation_example: str
    induced_deficit_mechanism: str
    incentive_actors: List[str]
    cycle_number_at_observation: int
    outcome: str


CROSS_DOMAIN_DATABASE: List[CrossDomainPattern] = [
    CrossDomainPattern(
        case_id="trucking_fatigue_regulation",
        domain=RegulatedDomain.TRANSPORTATION,
        description=(
            "Mandatory break rules built around sleep-deprived, "
            "malnourished baseline. Capable drivers constrained "
            "to LCD; automation justified against degraded baseline."
        ),
        lcd_regulation_example="DOT 30-min mandatory break, hours-of-service rules",
        induced_deficit_mechanism=(
            "Convenience-store food along corridors, truck-stop "
            "sleep environments, schedule pressure, isolation. "
            "Produces sleep apnea + fatigue. Cited as biology, "
            "is system-induced."
        ),
        incentive_actors=[
            "fleet operators benefiting from cheap labor",
            "compliance/insurance industry profiting from regulation",
            "automation vendors selling 'driver replacement'",
        ],
        cycle_number_at_observation=2,
        outcome=(
            "Automation deployment justified against degraded human "
            "baseline. Will inherit same degradation cycle when same "
            "actors deploy it."
        ),
    ),
    CrossDomainPattern(
        case_id="manufacturing_operator_displacement",
        domain=RegulatedDomain.MANUFACTURING,
        description=(
            "Skilled operators replaced by automation + cheap "
            "monitor-bodies. Knowledge exodus + certification "
            "inversion + reactive-only maintenance."
        ),
        lcd_regulation_example=(
            "Standardized certification programs that test "
            "credentials rather than competence; safety rules "
            "that train out embodied risk recognition."
        ),
        induced_deficit_mechanism=(
            "Wage inversion (experienced < certified). Knowledge "
            "transmission punished. Old-timers exit. Remaining "
            "labor pool degraded."
        ),
        incentive_actors=[
            "facility owners minimizing labor cost",
            "certification industry",
            "automation/integrator vendors",
        ],
        cycle_number_at_observation=3,
        outcome=(
            "Multiple cycles observed. Each automation generation "
            "requires more expensive intervention. Production "
            "quality declines while quarterly metrics improve."
        ),
    ),
    CrossDomainPattern(
        case_id="public_education_lcd",
        domain=RegulatedDomain.EDUCATION,
        description=(
            "Standardized curriculum + testing built around "
            "attention-degraded, nutritionally-deficient, "
            "sleep-deprived baseline. Capable learners "
            "constrained to LCD pace. Standardized-test scores "
            "cited as proof of universal cognitive capacity."
        ),
        lcd_regulation_example=(
            "Grade-level curriculum standards, age-cohort testing, "
            "mandatory pacing, attention-medication frameworks."
        ),
        induced_deficit_mechanism=(
            "Industrial-scale nutrition, fluorescent indoor "
            "environments, sleep-deprivation from schedules, "
            "screen-mediated cognition replacing substrate-primary "
            "learning."
        ),
        incentive_actors=[
            "testing companies",
            "curriculum publishers",
            "ed-tech vendors",
            "pharmaceutical attention-treatment industry",
        ],
        cycle_number_at_observation=4,
        outcome=(
            "Each generation: declining substrate-primary "
            "competence, rising prescription rates, more tech "
            "tools promised to fix what prior tools degraded."
        ),
    ),
    CrossDomainPattern(
        case_id="agriculture_industrial_inputs",
        domain=RegulatedDomain.AGRICULTURE,
        description=(
            "Regulations and certifications built around "
            "industrial-input-dependent farming. Traditional "
            "skill-encoded farmers constrained or excluded. "
            "Soil + nutrition + farmer-knowledge degraded."
        ),
        lcd_regulation_example=(
            "USDA certification regimes, food-safety rules "
            "designed around industrial processing, organic "
            "standards capturable by scale operators."
        ),
        induced_deficit_mechanism=(
            "Soil depletion through monoculture, farmer "
            "knowledge exodus through economic pressure, seed "
            "patenting eroding genetic diversity, processing "
            "stripping nutrient density."
        ),
        incentive_actors=[
            "agrochemical industry",
            "seed-patent holders",
            "consolidated processors",
            "compliance industry",
        ],
        cycle_number_at_observation=4,
        outcome=(
            "Each cycle: more inputs required, less nutrition "
            "delivered, more regulation justified by degraded "
            "system performance, replacement (lab-grown food, "
            "vertical farming) promised."
        ),
    ),
    CrossDomainPattern(
        case_id="healthcare_chronic_disease_management",
        domain=RegulatedDomain.HEALTHCARE,
        description=(
            "Treatment guidelines built around degraded-baseline "
            "patient population (poor diet, low movement, high "
            "stress). Pharmaceutical management substitutes for "
            "upstream cause repair."
        ),
        lcd_regulation_example=(
            "Standard-of-care protocols, dosing tables, "
            "insurance-coded treatment pathways."
        ),
        induced_deficit_mechanism=(
            "Food system, sedentary work, chronic stress, sleep "
            "deprivation produce the chronic disease being "
            "treated. Symptoms managed pharmaceutically."
        ),
        incentive_actors=[
            "pharmaceutical industry",
            "insurance companies",
            "device manufacturers",
            "consolidated hospital systems",
        ],
        cycle_number_at_observation=3,
        outcome=(
            "Each cycle: more medications, more procedures, "
            "more compliance burden, less actual health. "
            "AI-driven diagnostics now promised as next fix."
        ),
    ),
    CrossDomainPattern(
        case_id="ai_deployment_lcd_emerging",
        domain=RegulatedDomain.AI_DEPLOYMENT,
        description=(
            "AI safety / capability regulations being shaped "
            "around lowest-capable models, applied universally. "
            "Same lobbying actors from prior automation cycles "
            "shaping the framework."
        ),
        lcd_regulation_example=(
            "Universal safety rules that constrain capable "
            "models to incapable-model baseline; mandatory "
            "guardrails set by worst-case rather than tiered "
            "capability assessment."
        ),
        induced_deficit_mechanism=(
            "Training data sourced from desperation labor + "
            "AI-on-AI generations. Degraded outputs cited as "
            "proof AI 'cannot' do X. New-generation AI "
            "promised to fix what prior generation broke."
        ),
        incentive_actors=[
            "incumbent AI labs (regulatory capture)",
            "compliance/audit industry",
            "incumbent enterprise software vendors",
        ],
        cycle_number_at_observation=1,
        outcome=(
            "Cycle just beginning. Pattern markers present. "
            "Predicted to follow trucking/manufacturing trajectory "
            "absent intervention at incentive layer."
        ),
    ),
]


def cross_domain_match_count(domain: RegulatedDomain) -> int:
    """How many documented cases of this loop exist across domains?"""
    return len(CROSS_DOMAIN_DATABASE)


def matching_precedents(domain: RegulatedDomain) -> List[CrossDomainPattern]:
    """Cases in the same domain or with same actor structure."""
    return [c for c in CROSS_DOMAIN_DATABASE if c.domain == domain]


# ============================================================
# EXAMPLE: trucking domain end-to-end
# ============================================================

if __name__ == "__main__":
    lcd = LCDRegulation(
        regulation_id="dot_30min_break_mandate",
        domain=RegulatedDomain.TRANSPORTATION,
        baseline_population_capacity=0.45,           # sleep-deprived avg driver
        healthy_population_capacity=0.92,            # 6M-mile athlete-driver
        applied_to_full_capability_range=True,
        individual_assessment_permitted=False,
        rule_specifies_uniform_constraint=True,
    )
    deficit = InducedDeficitChain(
        deficit_id="trucker_metabolic_sleep_dysfunction",
        domain=RegulatedDomain.TRANSPORTATION,
        upstream_food_quality=0.18,
        upstream_sleep_environment=0.30,
        upstream_stress_load=0.72,
        upstream_skill_training_quality=0.40,
        upstream_economic_pressure=0.78,
        observed_population_dysfunction_rate=0.55,
        deficit_attributed_to_inherent_biology=True,
        upstream_causes_addressed=False,
        deficit_used_to_justify_regulation=True,
        deficit_used_to_justify_replacement=True,    # automation pitch
    )
    cycle = IncentiveCycle(
        cycle_id="trucking_automation_cycle_2",
        domain=RegulatedDomain.TRANSPORTATION,
        cycle_number=2,
        actors=[
            IncentiveActor(
                actor_id="major_fleet_operators",
                profits_from_degradation=True,
                profits_from_regulation=False,
                profits_from_replacement=True,
                has_lobbying_presence=True,
                same_actor_across_generations=True,
            ),
            IncentiveActor(
                actor_id="compliance_insurance_industry",
                profits_from_degradation=False,
                profits_from_regulation=True,
                profits_from_replacement=False,
                has_lobbying_presence=True,
                same_actor_across_generations=True,
            ),
            IncentiveActor(
                actor_id="automation_vendors",
                profits_from_degradation=False,
                profits_from_regulation=False,
                profits_from_replacement=True,
                has_lobbying_presence=True,
                same_actor_across_generations=False,
            ),
        ],
        cost_externalization_present=True,
        maintenance_treated_as_overhead=True,
        regulatory_capture_present=True,
        liability_shifted_downstream=True,
        quarterly_metric_dominance=True,
        skilled_practitioners_displaced=True,
        rehires_from_desperation_pool=True,
        failure_blamed_on_tool_or_user=True,
        new_tool_promised_to_fix_it=True,
    )

    result = coupled_pattern_audit(lcd, deficit, cycle)

    print(f"PATTERN ACTIVE: {result.pattern_active}")
    print(f"Severity: {result.severity_score:.2f}")
    print(f"Predicted remaining cycles before collapse: {result.predicted_repetition_count}")
    print(f"\nLayers active:")
    for k, v in result.individual_layers_active.items():
        print(f"  {k}: {v}")
    print(f"\nBreaking intervention points:")
    for i, point in enumerate(result.breaking_intervention_points, 1):
        print(f"  {i}. {point}")
    print(f"\nNotes:")
    for n in result.notes:
        print(f"  - {n}")

    print(f"\nCross-domain precedents in database: "
          f"{cross_domain_match_count(RegulatedDomain.TRANSPORTATION)}")
    print(f"Same-domain matches: "
          f"{len(matching_precedents(RegulatedDomain.TRANSPORTATION))}")
