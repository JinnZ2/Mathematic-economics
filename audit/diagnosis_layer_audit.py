"""
diagnosis_layer_audit.py

Add-on audit module for transportation_automation_audit.py
and regulation_lcd_incentive_audit.py
(also stands alone for any AI retraining context).

Audits the DIAGNOSIS LAYER of AI retraining loops:
WHO is labeling first-generation failures, and
WHAT incentive structure governs their work?

Core insight:
  AI retraining is only as good as the root-cause diagnosis
  done on prior-generation failures. If diagnosis is done by
  people in survival mode with no domain experience and no
  consequence for being wrong, the retraining loop learns
  test-taking, not physics.

Layers:
  1. Diagnosis-source identification
     contractor labelers, company engineers, outsourced
     experts, lived-experience practitioners
  2. Consequence alignment
     does the diagnoser feel the cost of wrong diagnosis?
  3. Domain immersion depth
     hands-in-soil, in-field consequence vs. classroom-only
  4. Incentive corruption per layer
     volume payment, desperation, credential signaling
  5. Retraining-loop quality projection
     given current diagnosis quality, what does
     generation 2, 3, 5 look like?

License: CC0
Stdlib only. Falsifiable. Domain-agnostic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


# ============================================================
# DIAGNOSIS-SOURCE TYPES
# ============================================================

class DiagnosisSourceType(Enum):
    """Who is doing root-cause diagnosis on AI failures?"""
    LIVED_PRACTITIONER = "lived_practitioner"
    # someone who works in the field, lives with consequence,
    # has substrate-primary domain knowledge

    SENIOR_ENGINEER_DOMAIN_EXPERT = "senior_engineer_domain_expert"
    # company engineer with deep domain background

    JUNIOR_ENGINEER_GENERAL = "junior_engineer_general"
    # company engineer, credentialed, no field consequence

    OUTSOURCED_EXPERT_CONSULTANT = "outsourced_expert_consultant"
    # external, paid per project, may have credentials but
    # no lived consequence

    GIG_CONTRACTOR_CREDENTIALED = "gig_contractor_credentialed"
    # online platform contractor, has degree, no field experience,
    # paid per task

    GIG_CONTRACTOR_DESPERATION = "gig_contractor_desperation"
    # online platform contractor, no domain background, paid
    # per task volume, in survival mode

    AI_AUTO_LABELED = "ai_auto_labeled"
    # second/third generation AI labeling for next generation
    # with no human review (worst case)


# ============================================================
# LAYER 1: CONSEQUENCE ALIGNMENT
# ============================================================

@dataclass
class ConsequenceAlignment:
    """
    Does the diagnoser feel the cost when their diagnosis is wrong?

    Lived practitioner: yes, they drive the truck / fix the bearing /
        treat the patient and feel the failure
    Engineer in field: partially, their reputation suffers
    Gig contractor: no, they got paid before failure surfaces
    AI auto-labeler: no, no agency, no consequence
    """
    diagnosis_source: DiagnosisSourceType
    feels_field_consequence: bool        # do they live with the result
    economic_consequence_if_wrong: float # 0-1, how much cost they bear
    reputation_consequence_if_wrong: float
    paid_before_failure_surfaces: bool
    can_be_held_accountable_after: bool

    def alignment_score(self) -> float:
        """0 = no skin in game, 1 = full consequence alignment."""
        score = 0.0
        if self.feels_field_consequence:
            score += 0.40
        score += self.economic_consequence_if_wrong * 0.25
        score += self.reputation_consequence_if_wrong * 0.15
        if not self.paid_before_failure_surfaces:
            score += 0.10
        if self.can_be_held_accountable_after:
            score += 0.10
        return min(1.0, score)

    def is_consequence_decoupled(self) -> bool:
        """True when diagnoser has effectively no skin in the game."""
        return self.alignment_score() < 0.30


# ============================================================
# LAYER 2: DOMAIN IMMERSION DEPTH
# ============================================================

@dataclass
class DomainImmersion:
    """
    Has the diagnoser actually worked in the field they're labeling?
    Hands-in-soil vs. classroom-only?

    A college-grad-no-field-time labeling agricultural failure modes
    will miss the subtle ripple effects a farmer would catch.
    Same for trucking, manufacturing, healthcare, construction, etc.
    """
    diagnosis_source: DiagnosisSourceType
    years_field_experience: float
    repaired_own_work_after_failure: bool
    lived_in_relevant_ecology: bool
    has_substrate_primary_pattern_recognition: bool
    has_only_credentialed_knowledge: bool

    def immersion_score(self) -> float:
        """0 = pure classroom/credential, 1 = deep substrate."""
        score = 0.0
        # field years cap meaningful contribution at ~10
        years_contribution = min(1.0, self.years_field_experience / 10) * 0.30
        score += years_contribution
        if self.repaired_own_work_after_failure:
            score += 0.20
        if self.lived_in_relevant_ecology:
            score += 0.15
        if self.has_substrate_primary_pattern_recognition:
            score += 0.30
        if self.has_only_credentialed_knowledge:
            score -= 0.15  # credential without practice is a negative signal
        return max(0.0, min(1.0, score))

    def is_classroom_only(self) -> bool:
        return (self.has_only_credentialed_knowledge
                and not self.has_substrate_primary_pattern_recognition
                and self.years_field_experience < 2.0)


# ============================================================
# LAYER 3: INCENTIVE CORRUPTION
# ============================================================

@dataclass
class IncentiveCorruption:
    """
    What incentive governs the diagnoser's labeling work?

    Volume-paid contractor: incentive is fast, not accurate
    Salaried domain expert: incentive is accurate, but pressure
        to ship may corrupt
    Lived practitioner: incentive is correctness because they
        feel the consequence
    """
    diagnosis_source: DiagnosisSourceType
    paid_per_task_volume: bool         # quantity over quality
    paid_for_accuracy_outcome: bool    # quality over quantity
    in_survival_mode: bool             # economic desperation
    pressured_by_deployment_deadline: bool
    pressured_by_quarterly_metrics: bool
    self_credential_attestation_only: bool  # they say they are expert,
                                            # nobody verified
    platform_validates_credentials: bool

    def corruption_score(self) -> float:
        """0 = clean incentive, 1 = fully corrupted."""
        score = 0.0
        if self.paid_per_task_volume:
            score += 0.25
        if not self.paid_for_accuracy_outcome:
            score += 0.15
        if self.in_survival_mode:
            score += 0.20
        if self.pressured_by_deployment_deadline:
            score += 0.10
        if self.pressured_by_quarterly_metrics:
            score += 0.10
        if self.self_credential_attestation_only:
            score += 0.15
        if not self.platform_validates_credentials:
            score += 0.05
        return min(1.0, score)

    def is_corrupted(self) -> bool:
        return self.corruption_score() > 0.50


# ============================================================
# LAYER 4: PROFILE PER DIAGNOSIS SOURCE
# ============================================================

@dataclass
class DiagnosisLayerProfile:
    """A complete profile of one source of diagnosis labels in
    the retraining loop."""
    source_id: str
    source_type: DiagnosisSourceType
    consequence: ConsequenceAlignment
    immersion: DomainImmersion
    incentive: IncentiveCorruption
    fraction_of_total_labels: float  # 0-1, share of retraining data

    def reliability_score(self) -> float:
        """Combined: high consequence alignment + deep immersion +
        clean incentive = reliable diagnosis."""
        c = self.consequence.alignment_score()
        i = self.immersion.immersion_score()
        n = 1.0 - self.incentive.corruption_score()
        return c * 0.35 + i * 0.35 + n * 0.30

    def is_unreliable(self) -> bool:
        return self.reliability_score() < 0.40

    def produces_test_taking_not_understanding(self) -> bool:
        """If immersion is shallow AND consequence is decoupled,
        the labels capture surface patterns, not causal physics."""
        return (self.immersion.is_classroom_only()
                or self.consequence.is_consequence_decoupled())


# ============================================================
# LAYER 5: RETRAINING-LOOP QUALITY PROJECTION
# ============================================================

@dataclass
class RetrainingLoopProjection:
    """
    Given the mix of diagnosis sources and their reliability,
    project quality across N generations of retraining.

    Each generation compounds prior corruption unless real
    domain consequence enters the loop.
    """
    profiles: List[DiagnosisLayerProfile]
    generations_to_project: int
    real_world_validation_between_generations: bool
    field_practitioner_review_between_generations: bool

    def weighted_diagnosis_reliability(self) -> float:
        """Weighted by fraction of total labels each source contributes."""
        total_fraction = sum(p.fraction_of_total_labels for p in self.profiles)
        if total_fraction == 0:
            return 0.0
        weighted = sum(
            p.reliability_score() * p.fraction_of_total_labels
            for p in self.profiles
        )
        return weighted / total_fraction

    def per_generation_decay_rate(self) -> float:
        """How much quality is lost per generation given current loop."""
        base_quality = self.weighted_diagnosis_reliability()
        # If real-world validation breaks the loop, decay is small
        if self.real_world_validation_between_generations:
            return max(0.02, 0.10 - base_quality * 0.08)
        if self.field_practitioner_review_between_generations:
            return max(0.05, 0.15 - base_quality * 0.10)
        # No real-world correction: decay compounds aggressively
        return min(0.30, 0.40 - base_quality * 0.30)

    def project_quality(self) -> List[float]:
        """Quality trajectory across generations."""
        q = self.weighted_diagnosis_reliability()
        decay = self.per_generation_decay_rate()
        trajectory = [q]
        for _ in range(self.generations_to_project):
            q = max(0.0, q * (1 - decay))
            trajectory.append(q)
        return trajectory

    def generation_at_threshold(self, threshold: float = 0.20) -> int:
        """Generation at which quality drops below useful threshold."""
        traj = self.project_quality()
        for gen, q in enumerate(traj):
            if q < threshold:
                return gen
        return -1  # never crossed within projection window

    def loop_will_collapse_within_projection(self) -> bool:
        return self.generation_at_threshold() != -1


# ============================================================
# LAYER 6: RETRAINING-VALIDATION GATE
# ============================================================

@dataclass
class RetrainingGateResult:
    gate_passes: bool
    diagnosis_reliability: float
    decay_per_generation: float
    quality_trajectory: List[float]
    collapse_generation: int
    failure_modes: List[str] = field(default_factory=list)
    required_remediations: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def retraining_gate_audit(
    projection: RetrainingLoopProjection,
    minimum_reliability_threshold: float = 0.55,
    maximum_decay_per_generation: float = 0.12,
) -> RetrainingGateResult:
    """
    Validation gate that MUST be passed before second-generation
    retraining is allowed. If diagnosis layer is corrupted, the
    loop will degrade and should be halted, not advanced.
    """
    r = RetrainingGateResult(
        gate_passes=True,
        diagnosis_reliability=projection.weighted_diagnosis_reliability(),
        decay_per_generation=projection.per_generation_decay_rate(),
        quality_trajectory=projection.project_quality(),
        collapse_generation=projection.generation_at_threshold(),
    )

    # ---- Reliability check ----
    if r.diagnosis_reliability < minimum_reliability_threshold:
        r.gate_passes = False
        r.failure_modes.append(
            f"Weighted diagnosis reliability {r.diagnosis_reliability:.2f} "
            f"below minimum threshold {minimum_reliability_threshold:.2f}. "
            "Diagnosis layer cannot produce trustworthy retraining labels."
        )

    # ---- Decay rate check ----
    if r.decay_per_generation > maximum_decay_per_generation:
        r.gate_passes = False
        r.failure_modes.append(
            f"Per-generation decay {r.decay_per_generation:.2f} exceeds "
            f"safe ceiling {maximum_decay_per_generation:.2f}. "
            "Retraining loop will compound corruption rather than correct it."
        )

    # ---- Real-world validation check ----
    if (not projection.real_world_validation_between_generations
        and not projection.field_practitioner_review_between_generations):
        r.gate_passes = False
        r.failure_modes.append(
            "No real-world or field-practitioner validation between "
            "generations. Loop is closed against physical reality. "
            "Will produce test-taking, not thermodynamic understanding."
        )
        r.required_remediations.append(
            "Insert field-practitioner review at every retraining cycle. "
            "Real-world validation must close the loop with consequence."
        )

    # ---- Per-source corruption flags ----
    for p in projection.profiles:
        if p.is_unreliable() and p.fraction_of_total_labels > 0.15:
            r.failure_modes.append(
                f"Source '{p.source_id}' ({p.source_type.value}) is "
                f"unreliable (score {p.reliability_score():.2f}) and "
                f"contributes {p.fraction_of_total_labels:.0%} of labels. "
                "Significant corruption fraction in retraining data."
            )
        if p.produces_test_taking_not_understanding():
            r.failure_modes.append(
                f"Source '{p.source_id}' produces surface-pattern labels, "
                "not causal-understanding labels. Retraining will learn "
                "test answers, not domain physics."
            )

    # ---- Collapse projection ----
    if r.collapse_generation > 0 and r.collapse_generation < 5:
        r.failure_modes.append(
            f"Loop collapses at generation {r.collapse_generation}. "
            "Quality drops below usable threshold within short horizon."
        )
        r.gate_passes = False

    # ---- Remediation menu (independent of pass/fail to inform users) ----
    if r.diagnosis_reliability < minimum_reliability_threshold:
        r.required_remediations.append(
            "Increase fraction of labels from lived practitioners with "
            "field experience and consequence alignment. Reduce gig-contractor "
            "and AI-auto-labeled fractions."
        )
    if any(p.consequence.is_consequence_decoupled() for p in projection.profiles):
        r.required_remediations.append(
            "Restructure labeling incentives so diagnosers bear consequence "
            "for wrong labels (paid for accuracy verified by field outcome, "
            "not for volume completed)."
        )
    if any(p.immersion.is_classroom_only() for p in projection.profiles):
        r.required_remediations.append(
            "Require minimum field-experience threshold for any labeler "
            "diagnosing domain failures. Credential alone is insufficient."
        )

    # ---- Notes ----
    if not r.gate_passes:
        r.notes.append(
            "RETRAINING GATE FAILED. Second-generation training should not "
            "proceed under current diagnosis-layer composition. Loop will "
            "compound corruption and produce confidently-wrong system."
        )
    else:
        r.notes.append(
            "Retraining gate passed under current composition. Continue to "
            "monitor decay rate and reliability between generations."
        )

    return r


# ============================================================
# EXAMPLE: typical AI retraining loop today
# ============================================================

if __name__ == "__main__":
    # Profile 1: Gig contractor, desperation, classroom-only
    gig_desperation = DiagnosisLayerProfile(
        source_id="online_platform_contractors",
        source_type=DiagnosisSourceType.GIG_CONTRACTOR_DESPERATION,
        consequence=ConsequenceAlignment(
            diagnosis_source=DiagnosisSourceType.GIG_CONTRACTOR_DESPERATION,
            feels_field_consequence=False,
            economic_consequence_if_wrong=0.05,
            reputation_consequence_if_wrong=0.10,
            paid_before_failure_surfaces=True,
            can_be_held_accountable_after=False,
        ),
        immersion=DomainImmersion(
            diagnosis_source=DiagnosisSourceType.GIG_CONTRACTOR_DESPERATION,
            years_field_experience=0.0,
            repaired_own_work_after_failure=False,
            lived_in_relevant_ecology=False,
            has_substrate_primary_pattern_recognition=False,
            has_only_credentialed_knowledge=False,  # often not even credentialed
        ),
        incentive=IncentiveCorruption(
            diagnosis_source=DiagnosisSourceType.GIG_CONTRACTOR_DESPERATION,
            paid_per_task_volume=True,
            paid_for_accuracy_outcome=False,
            in_survival_mode=True,
            pressured_by_deployment_deadline=True,
            pressured_by_quarterly_metrics=False,
            self_credential_attestation_only=True,
            platform_validates_credentials=False,
        ),
        fraction_of_total_labels=0.45,
    )

    # Profile 2: Outsourced credentialed contractor, no field
    credentialed_no_field = DiagnosisLayerProfile(
        source_id="outsourced_credentialed_consultants",
        source_type=DiagnosisSourceType.GIG_CONTRACTOR_CREDENTIALED,
        consequence=ConsequenceAlignment(
            diagnosis_source=DiagnosisSourceType.GIG_CONTRACTOR_CREDENTIALED,
            feels_field_consequence=False,
            economic_consequence_if_wrong=0.10,
            reputation_consequence_if_wrong=0.25,
            paid_before_failure_surfaces=True,
            can_be_held_accountable_after=False,
        ),
        immersion=DomainImmersion(
            diagnosis_source=DiagnosisSourceType.GIG_CONTRACTOR_CREDENTIALED,
            years_field_experience=0.5,
            repaired_own_work_after_failure=False,
            lived_in_relevant_ecology=False,
            has_substrate_primary_pattern_recognition=False,
            has_only_credentialed_knowledge=True,
        ),
        incentive=IncentiveCorruption(
            diagnosis_source=DiagnosisSourceType.GIG_CONTRACTOR_CREDENTIALED,
            paid_per_task_volume=True,
            paid_for_accuracy_outcome=False,
            in_survival_mode=False,
            pressured_by_deployment_deadline=True,
            pressured_by_quarterly_metrics=False,
            self_credential_attestation_only=False,
            platform_validates_credentials=True,
        ),
        fraction_of_total_labels=0.25,
    )

    # Profile 3: Junior company engineer, credentialed, no field
    junior_engineer = DiagnosisLayerProfile(
        source_id="junior_company_engineers",
        source_type=DiagnosisSourceType.JUNIOR_ENGINEER_GENERAL,
        consequence=ConsequenceAlignment(
            diagnosis_source=DiagnosisSourceType.JUNIOR_ENGINEER_GENERAL,
            feels_field_consequence=False,
            economic_consequence_if_wrong=0.15,
            reputation_consequence_if_wrong=0.45,
            paid_before_failure_surfaces=False,
            can_be_held_accountable_after=True,
        ),
        immersion=DomainImmersion(
            diagnosis_source=DiagnosisSourceType.JUNIOR_ENGINEER_GENERAL,
            years_field_experience=1.0,
            repaired_own_work_after_failure=False,
            lived_in_relevant_ecology=False,
            has_substrate_primary_pattern_recognition=False,
            has_only_credentialed_knowledge=True,
        ),
        incentive=IncentiveCorruption(
            diagnosis_source=DiagnosisSourceType.JUNIOR_ENGINEER_GENERAL,
            paid_per_task_volume=False,
            paid_for_accuracy_outcome=False,
            in_survival_mode=False,
            pressured_by_deployment_deadline=True,
            pressured_by_quarterly_metrics=True,
            self_credential_attestation_only=False,
            platform_validates_credentials=True,
        ),
        fraction_of_total_labels=0.20,
    )

    # Profile 4: AI auto-labeling (the worst case)
    ai_auto = DiagnosisLayerProfile(
        source_id="ai_auto_labeling_pipeline",
        source_type=DiagnosisSourceType.AI_AUTO_LABELED,
        consequence=ConsequenceAlignment(
            diagnosis_source=DiagnosisSourceType.AI_AUTO_LABELED,
            feels_field_consequence=False,
            economic_consequence_if_wrong=0.0,
            reputation_consequence_if_wrong=0.0,
            paid_before_failure_surfaces=True,
            can_be_held_accountable_after=False,
        ),
        immersion=DomainImmersion(
            diagnosis_source=DiagnosisSourceType.AI_AUTO_LABELED,
            years_field_experience=0.0,
            repaired_own_work_after_failure=False,
            lived_in_relevant_ecology=False,
            has_substrate_primary_pattern_recognition=False,
            has_only_credentialed_knowledge=False,
        ),
        incentive=IncentiveCorruption(
            diagnosis_source=DiagnosisSourceType.AI_AUTO_LABELED,
            paid_per_task_volume=True,
            paid_for_accuracy_outcome=False,
            in_survival_mode=False,
            pressured_by_deployment_deadline=False,
            pressured_by_quarterly_metrics=False,
            self_credential_attestation_only=False,
            platform_validates_credentials=False,
        ),
        fraction_of_total_labels=0.10,
    )

    projection = RetrainingLoopProjection(
        profiles=[gig_desperation, credentialed_no_field, junior_engineer, ai_auto],
        generations_to_project=8,
        real_world_validation_between_generations=False,
        field_practitioner_review_between_generations=False,
    )

    result = retraining_gate_audit(projection)

    print(f"GATE PASSES: {result.gate_passes}")
    print(f"Diagnosis reliability: {result.diagnosis_reliability:.2f}")
    print(f"Decay per generation: {result.decay_per_generation:.2f}")
    print(f"Collapse at generation: {result.collapse_generation}")
    print(f"\nQuality trajectory across generations:")
    for gen, q in enumerate(result.quality_trajectory):
        bar = "#" * int(q * 40)
        print(f"  Gen {gen}: {q:.3f}  {bar}")
    print(f"\nFailure modes:")
    for f in result.failure_modes:
        print(f"  - {f}")
    print(f"\nRequired remediations:")
    for rem in result.required_remediations:
        print(f"  - {rem}")
    print(f"\nNotes:")
    for n in result.notes:
        print(f"  - {n}")
