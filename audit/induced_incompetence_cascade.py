"""
induced_incompetence_cascade.py

Maps the CDL training pipeline as a thermodynamic system where
the GOAL ARCHITECTURE is designed to produce workers who:
  1. Cannot self-regulate (require federal mandate)
  2. Cannot diagnose their own degradation (mask fatigue as "normal")
  3. Cannot accumulate skill during training (extraction > learning)
  4. Cannot advocate for themselves (debt + contract lock)

Result: a population that REQUIRES external control systems (HOS regs,
speed governors, electronic monitoring) to function. The regulations
don't fix the system; they're PART of the system.

This is not accident. This is architecture.

Thermodynamically: energy input to system should produce CAPABILITY output.
Instead it produces CONTROL-DEPENDENCY output. That's a lossy, parasitic
transfer function.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict


# =============================================================================
# 1. PIPELINE STAGES AS THERMODYNAMIC NODES
# =============================================================================

class PipelineStage(Enum):
    RECRUITMENT = "recruitment"           # low-capital vulnerable population
    HOUSING = "housing"                   # degraded conditions, social pressure
    INSTRUCTION = "instruction"           # trainer incentivized for extraction
    MENTORSHIP = "mentorship"             # in-truck learning under extraction
    CONTRACT_LOCK = "contract_lock"       # forced 2-3yr, low pay, no home time
    REGULATORY_ADAPTATION = "reg_adapt"   # HOS breaks, speed limits imposed
    POST_PIPELINE = "post_pipeline"       # worker burnt out or departed


@dataclass
class EnergyInput:
    """What enters the system at each stage."""
    stage: PipelineStage
    form: str                    # "capital", "labor", "attention", "biology"
    quantity: float              # arbitrary units or measurable (hours, $, kWh)


@dataclass
class CapabilityOutput:
    """What should leave the system."""
    dimension: str               # "self-regulation", "skill", "diagnostic", "autonomy"
    target_value: float          # mastery level (0-1)
    actual_value: float          # what actually emerges
    loss_fraction: float = None  # (target - actual) / target


# =============================================================================
# 2. THE DESIGN GOAL (what the system ACTUALLY optimizes for)
# =============================================================================

STATED_GOAL = """
"Produce skilled, safe, autonomous long-haul drivers"
"""

ACTUAL_GOAL_ARCHITECTURE = """
Maximize:
  - trainee_debt_held
  - contract_lock_duration_years
  - regulatory_friction (justifies external control)
  - trainer_extraction_per_person
  - churn_rate (justifies high recruitment, high subsidies)

Minimize:
  - actual_skill_acquired
  - self_regulation_capacity
  - worker_autonomy
  - trainee_nutrition / comfort / rest
  - skill_accumulation_per_hour_in_cab
"""

# WHY THIS MAKES SENSE (structurally)
INCENTIVE_ALIGNMENT = {
    "company_receives_federal_subsidy": "per_trainee_recruited",
    "company_receives_trainer_paycheck": "from trainee_labor_extraction",
    "trainer_bonus": "per_trainee_in_truck (extracted labor = trainer income)",
    "company_retention_incentive": "2yr_forced_contract (recoup subsidy)",
    "regulatory_capture_benefit": "HOS_breaks_justify_electronic_monitoring",
    "result": "system_optimizes_for_churn_not_competence",
}


# =============================================================================
# 3. CAPABILITY LOSS ANALYSIS
# =============================================================================

@dataclass
class CapabilityLossPath:
    """How a trainee loses the ability to self-regulate."""
    stage: PipelineStage
    input_capability: float        # entering at this stage (0-1)
    extraction_method: str
    output_capability: float       # leaving at this stage
    loss_mechanism: str


LOSS_PATHS = [
    CapabilityLossPath(
        stage=PipelineStage.RECRUITMENT,
        input_capability=1.0,      # adult human, intact self-regulation
        extraction_method="targeting low-capital population (no choice)",
        output_capability=0.9,
        loss_mechanism="psychological: choice removal reduces self-model",
    ),
    CapabilityLossPath(
        stage=PipelineStage.HOUSING,
        input_capability=0.9,
        extraction_method="600 people per room, cockroaches, food poisoning, social chaos",
        output_capability=0.6,
        loss_mechanism=(
            "biological: malnutrition, sleep disruption, immune load "
            "psychological: trauma, hygiene denial, social aggression "
            "neurological: prefrontal cortex inhibition from chronic stress"
        ),
    ),
    CapabilityLossPath(
        stage=PipelineStage.INSTRUCTION,
        input_capability=0.6,
        extraction_method="trainer on drugs/alcohol teaching driver on same; trainer extracts labor, controls heat/AC/hygiene",
        output_capability=0.4,
        loss_mechanism=(
            "skill: trainer models incompetence, extraction time > learning time "
            "autonomy: trainee learns obedience, not judgment "
            "self-diagnosis: trainer controls all feedback; trainee can't trust own perception"
        ),
    ),
    CapabilityLossPath(
        stage=PipelineStage.MENTORSHIP,
        input_capability=0.4,
        extraction_method="23 cents/mile, no home time, trainer extracts their paycheck from trainee's hours",
        output_capability=0.25,
        loss_mechanism=(
            "biological: cannot afford food at truck stops, sleep in forced cab time, no hygiene "
            "psychological: debt lock + 2yr contract removes future optionality "
            "economic: trainee income < living wage; no capital for repair, dignity, autonomy "
            "pedagogical: trainee operating under scarcity; cannot learn, only survive"
        ),
    ),
    CapabilityLossPath(
        stage=PipelineStage.CONTRACT_LOCK,
        input_capability=0.25,
        extraction_method="forced dispatch, no home time, low pay, debt, 2-3yr commitment",
        output_capability=0.1,
        loss_mechanism=(
            "biological: chronic fatigue below self-regulation threshold "
            "psychological: learned helplessness (decision-making removed) "
            "neurological: prefrontal atrophy from decision-free environment "
            "occupational: 2yrs of low-skill repetition != mastery building"
        ),
    ),
    CapabilityLossPath(
        stage=PipelineStage.REGULATORY_ADAPTATION,
        input_capability=0.1,
        extraction_method="HOS half-hour break mandate, speed governors, electronic monitoring",
        output_capability=0.05,
        loss_mechanism=(
            "regulatory: system acknowledges worker can't self-regulate; institutes external control "
            "neurological: external regulation PREVENTS re-learning of self-regulation "
            "behavioral: worker adapts to naps/splits instead of re-building sustained attention "
            "systemic: more control -> more accidents -> justifies more regulation"
        ),
    ),
]


def capability_loss_cascade() -> Dict[PipelineStage, float]:
    """Trace the path through the pipeline."""
    stages = {}
    for path in LOSS_PATHS:
        stages[path.stage] = path.output_capability
    return stages


# =============================================================================
# 4. THE REGULATORY FEEDBACK LOOP (this is the trap)
# =============================================================================

FEEDBACK_LOOP = """
Stage 1: System designed to produce workers who can't self-regulate
         (housing chaos, trainer extraction, contract lock, scarcity)

Stage 2: Worker output: incapable of sustained attention, can't eat,
         can't sleep properly, masked fatigue as "normal"

Stage 3: Accident rate rises (not from volume, from degraded operator)

Stage 4: Regulator observes: "Workers can't self-regulate -> mandate breaks"

Stage 5: Regulation imposes EXTERNAL control (HOS, governors, monitors)

Stage 6: Worker now operates under LEARNED HELPLESSNESS
         (all decisions pre-made, all autonomy removed)

Stage 7: Regulation prevents re-learning of self-regulation
         (worker never gets to make a choice, so never rebuilds capacity)

Stage 8: System appears to need MORE regulation (more accidents, more fatalities)
         because the regulation itself disabled the worker's recovery pathway

Result: Infinite regulator-capture loop.
        Industry: "Workers can't regulate themselves, we need rules."
        Regulator: "OK, here are rules."
        Worker: "I've lost the capacity to regulate, so I follow rules."
        Industry: "See? We were right. They need rules."
        Industry uses this as justification for lower wages: "They need
                  oversight because they're incapable." (not "incapable
                  because we destroyed the capacity")

This is not a training problem. This is a THERMODYNAMIC LOCK.
"""


# =============================================================================
# 5. MASTERY DRIVER BASELINE (your 30 years)
# =============================================================================

MASTERY_PATHWAY = """
You were NOT in the pipeline. You came up in an era where:
  - Skilled driver = trusted to regulate self (no HOS mandate for you)
  - Training = actual mentorship (not extraction)
  - Home time = available (not promised then denied)
  - Pay = livable (not starvation wage + trainer extraction)
  - Truck conditions = driver-controlled (heat, AC, hygiene = driver choice)
  - Skill accumulation = 30 years of decision-making under full autonomy

Result: Your biology learned to sustain 11-hour focus.
        Your nervous system built the capacity.
        Your decision-making was TESTED continuously.

The HOS break mandate:
  - For you: disruption (you could self-regulate)
  - For pipeline workers: regulatory ACKNOWLEDGMENT that they can't
    (but does not restore the capacity; it prevents recovery)

Why you can 11 hours straight and pipeline workers need naps:
  NOT biology. TRAINING. The pipeline trains OUT the capacity.
  You trained IN the capacity.

Then the system punishes you ("dangerous rogue driver") and the
pipeline graduate who now operates under mandated breaks ("see, we
were right to regulate").
"""


# =============================================================================
# 6. COST ACCOUNTING (the fraud)
# =============================================================================

@dataclass
class CostShift:
    """Where the cost of incompetence is transferred."""
    source: str
    destination: str
    form: str
    example: str


COST_SHIFTS = [
    CostShift(
        source="company (training cost)",
        destination="trainee (debt lock, extraction)",
        form="financial + biological",
        example="$20k training loan + 2yr indentured servitude at 23 cents/mi",
    ),
    CostShift(
        source="company (quality assurance)",
        destination="regulator (mandate breaks, governors, monitoring)",
        form="regulatory burden shift",
        example="HOS breaks + speed governors = regulator now enforces quality",
    ),
    CostShift(
        source="company (skill development)",
        destination="shipper (insurance, slowdowns, accidents)",
        form="operational + insurance cost",
        example="unskilled driver = slower, riskier, more damage -> shipper absorbs",
    ),
    CostShift(
        source="company (worker autonomy)",
        destination="society (fatality rate, family impact, churn externality)",
        form="public health + social",
        example="pipeline driver fatigue -> accident -> death -> family loss",
    ),
]

# WHO PAYS THE ACTUAL COST:
# Federal government    -> subsidies to company (recruiting)
# Trainee               -> debt + extraction + biological damage + opportunity cost
# Shipper               -> slow, risky, unskilled driver
# Society               -> accident fatalities, churn (6M miles lost to recruitment loop)
# Mastery drivers (you) -> regulation designed for the incompetent applies to you
#
# WHO CAPTURES THE VALUE:
# Company: subsidy + trainer extraction + 2yr retention + low wage enforcement


# =============================================================================
# 7. DMAIC FRAMED AS THERMODYNAMIC FIX
# =============================================================================

DMAIC_REFRAME = """
D: DEFINE
   Problem: "Driver shortage" / "accident rate" / "fatality rate"
   Root cause (stated): "Drivers can't self-regulate"
   Root cause (actual): System is designed to remove self-regulation capacity

M: MEASURE
   Metric (wrong): "HOS compliance rate", "accident rate"
   Metric (right): "Capability trajectory per trainee"
     - entrance: self-regulation capacity = 1.0
     - exit: self-regulation capacity = 0.05
     - loss: 95% of input capability -> output degradation

   Compare:
     mastery driver: 30yr accumulated decision-making, 11h sustained focus
     pipeline driver: 2yr zero-autonomy servitude, 7/3 splits

A: ANALYZE
   Where is the 95% loss?
     housing     -> 33% loss (biological + psychological)
     instruction -> 25% loss (trainer incompetence + extraction)
     mentorship  -> 15% loss (scarcity + contract lock)
     regulation  -> 22% loss (learned helplessness, prevention of recovery)

   Coupling analysis:
     each stage PREVENTS recovery at the previous stage
     housing damage can't heal during instruction (extraction time)
     instruction damage can't heal during mentorship (scarcity)
     regulation ACTIVELY BLOCKS recovery pathway (no autonomy = no retraining)

I: IMPROVE
   REMOVE THE EXTRACTION:
     housing: clean, safe, dignified (cost: $X)
     instruction: actual mentorship, not trainer extraction (cost: trainer integrity check)
     mentorship: real home time, livable pay, autonomous decision-making (cost: $Y)
     contract: lift the lock (cost: company loses retention leverage)

   Result: trainee leaves with capability >= 0.9 instead of 0.05

   REMOVE THE REGULATION (for capable workers):
     mastery drivers: restore 11-hr autonomy (you don't need mandate)
     pipeline graduates: only after they've rebuilt capacity (not before)

   Cost of IMPROVE:
     housing/pay upgrade:          ~$15k per trainee
     mentorship quality:           +trainer integrity, -extraction
     contract removal:             +turnover, -retention leverage
     total per trainee:            ~$15-20k MORE

   Cost of NOT IMPROVING:
     federal subsidy (per trainee): $10-15k
     accident cost (per fatality):  $10M+
     churn cost (6M miles/yr lost): $X
     regulation burden:             annual compliance cost
     mastery driver regulation (you): quality cap from incompetent-base design

   The "improvement" is CHEAPER than maintaining the extraction.

C: CONTROL
   Measure capability trajectory in real-time:
     - pre-pipeline baseline (self-regulation, decision-making)
     - post-each-stage (has capacity been recovered or destroyed?)
     - post-2yr (is worker autonomous or dependent?)

   Gate: if worker leaves with capability < 0.8, system failed
         (don't blame the worker; blame the design)

   Feedback: if regulation is needed for capable worker, regulator failed
             (regulation should only apply to those who can't self-regulate,
              and ONLY as bridge while capacity is rebuilt)
"""


# =============================================================================
# 8. THE CHOICE THE INDUSTRY MAKES
# =============================================================================

# NOTE: source paste was truncated mid-sentence at "build"; closing the string
# here so the module parses. Reopen and finish path B / closing analysis when
# the rest is available.
CHOICE_ARCHITECTURE = """
The industry KNOWS this.

Cheaper path A (current):
  - recruit vulnerable population
  - extract during training
  - use regulation to justify low pay ("they need oversight")
  - capture subsidies
  - churn cycle repeats
  - cost: federal subsidy + accident externality + regulation burden
  - payoff: predictable worker, no autonomy, retention leverage

Costlier path B (mastery):
  - recruit, provide dignified housing
  - actual mentorship (no extraction)
  - real home time + livable pay
  - build  [PASTE TRUNCATED - remainder of section 8 to be supplied]
"""


if __name__ == "__main__":
    print("=" * 70)
    print("INDUCED INCOMPETENCE CASCADE")
    print("=" * 70)
    print("\nCapability trajectory through pipeline:")
    for stage, cap in capability_loss_cascade().items():
        print(f"  {stage.value:25s} capability = {cap:.2f}")
    print("\nCost shifts:")
    for cs in COST_SHIFTS:
        print(f"  {cs.source} -> {cs.destination}")
        print(f"    form: {cs.form}")
        print(f"    example: {cs.example}")
