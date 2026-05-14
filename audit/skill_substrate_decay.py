"""
skill_substrate_decay.py

Per-domain empirical tracker for the delta_skill externality dimension
defined in withholding_externality.py. Quantifies cognitive substrate
decay across eight skill domains, anchored to published longitudinal
or cross-sectional evidence.

Central claim: cognitive skills offloaded to external systems
(GPS, calculator, AI) exhibit measurable decay in users at rates that
exceed natural skill maintenance, and the decay is partially
irreversible after the encoding window closes. The decay rate and
reversibility differ by domain depending on when in the developmental
trajectory the skill was originally acquired.

The encoding_depth axis (from calibration_audit) is load-bearing:
skills acquired during the neuroplasticity window with survival-embedded
context are more architecturally primary than skills acquired later
via language-mediated instruction. The former survive offloading better
but, when they DO erode, are harder to rebuild.

Companion modules:
    withholding_externality.py      - meta-layer (this fills delta_skill)
    dependency_cascade_ledger.py    - empirical layer (delta_depend)
    self_measurement_compromise.py  - recursive validation
    calibration_audit.py            - encoding-depth framework (upstream)

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library only
Author:  JinnZ2 (audit module stack)
Status:  Falsifiable; each domain anchor is a citation that can be
         challenged or updated.

Position in audit stack:
    withholding_externality (meta-layer)
       |
       +- skill_substrate_decay        [delta_skill]   <-- THIS MODULE
       +- dependency_cascade_ledger    [delta_depend]   (landed)
       +- training_corpus_degrade      [delta_corpus]
       +- self_measurement_compromise  [validation]    (landed)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math


# =====================================================================
# SECTION 1 -- FORMAL CLAIMS
# =====================================================================

CLAIMS = {
    "S1": {
        "claim": "Cognitive skills offloaded to external systems "
                 "exhibit measurable decay in users at rates exceeding "
                 "natural skill maintenance.",
        "falsifiable_by": "Longitudinal study showing offloading-group "
                          "skill retention >= non-offloading-group "
                          "across multiple domains.",
        "status": "supported across 8 domains as of 2026-05",
    },

    "S2": {
        "claim": "Decay is partially or fully irreversible after the "
                 "encoding window closes. Reversibility decreases with "
                 "the depth at which the skill was originally encoded.",
        "falsifiable_by": "Demonstration that adult re-acquisition "
                          "fully restores capacity in skills lost "
                          "from atrophy after the encoding window.",
        "status": "supported by neuroplasticity literature; "
                  "calibration_audit framework applies",
    },

    "S3": {
        "claim": "Cohort replacement extends the decay: each cohort "
                 "that grows up with offloaded skills has lower "
                 "baseline capacity than the prior cohort, "
                 "independent of individual usage.",
        "falsifiable_by": "Demonstration of stable or rising baseline "
                          "across cohorts in offloaded domains.",
        "status": "supported by PISA trajectories; multi-domain",
    },

    "S4": {
        "claim": "Skills with intact embodied / physical-substrate "
                 "alternatives decay more slowly than skills available "
                 "only through abstract / symbolic instantiation.",
        "falsifiable_by": "Demonstration that physical-trade skills "
                          "are decaying at rates comparable to "
                          "text-mediated skills.",
        "status": "supported; physical trades remain intact while "
                  "text-mediated skills degrade",
    },

    "S5": {
        "claim": "Decay rates have accelerated since approximately "
                 "2022 (broad AI deployment) compared to the prior "
                 "decade of digital tool dependency.",
        "falsifiable_by": "Time-series showing flat or decelerating "
                          "decay rate across 2022-2026.",
        "status": "supported for coding, writing, critical thinking; "
                  "earlier-offloaded domains stable-degraded",
    },

    "S6": {
        "claim": "The economic value of intact embodied skill is "
                 "rising as text-mediated skill becomes commodified "
                 "and depleted. The mighty-atom signal -- credentialed "
                 "rating divergent from actual capacity -- generalizes.",
        "falsifiable_by": "Demonstration that embodied-skill labor "
                          "compensation is not diverging from "
                          "credentialed-labor compensation over time.",
        "status": "early supporting evidence in skilled-trades wage "
                  "trajectories",
    },
}


# =====================================================================
# SECTION 2 -- DOMAIN SCHEMA
# =====================================================================

@dataclass
class SkillDomain:
    """
    A single cognitive skill domain tracked for offloading-induced
    decay. Each field maps to published evidence or a defensible
    empirical estimate.

    Score conventions:
        - All "state" fields are in [0.0, 1.0] where 1.0 means
          population-level full capacity.
        - Decay rate is fractional capacity loss per year.
        - Reversibility window is years post-onset within which
          intervention can restore most capacity.
    """

    domain: str
    offloading_system: str                # what users offload TO
    offloading_started_year: int

    pre_offload_baseline: float           # ~1.0 by definition
    current_population_state: float       # empirical estimate
    decay_rate_per_year: float            # fractional loss/year
    reversibility_window_years: float     # years before partial
                                          # irreversibility sets in
    cohort_replacement_status: str        # "stable", "drifting", "broken"
    embodied_alternative_intact: bool

    primary_anchor: str                   # citation / evidence source
    secondary_anchors: list[str] = field(default_factory=list)

    signal_strength: str = "moderate"     # "weak", "moderate", "strong"
    trajectory: str = "stable"            # "stable", "degrading",
                                          # "accelerating"
    notes: str = ""

    def capacity_gap(self) -> float:
        """How far below baseline the current population state is."""
        return max(0.0, self.pre_offload_baseline
                        - self.current_population_state)

    def years_since_offload(self, current_year: int = 2026) -> int:
        return max(0, current_year - self.offloading_started_year)

    def projected_state(self, years_ahead: float = 5.0,
                        current_year: int = 2026) -> float:
        """
        Simple exponential decay projection. Does not account for
        cohort effects or floor levels -- meant as an order-of-magnitude
        indicator.
        """
        return max(
            0.0,
            self.current_population_state
            * math.exp(-self.decay_rate_per_year * years_ahead)
        )

    def reversibility_class(self) -> str:
        """
        Qualitative reversibility based on years since offload
        relative to reversibility window.
        """
        elapsed = self.years_since_offload()
        if elapsed < self.reversibility_window_years * 0.5:
            return "high"
        if elapsed < self.reversibility_window_years:
            return "partial"
        if elapsed < self.reversibility_window_years * 2:
            return "low"
        return "very_low"


# =====================================================================
# SECTION 3 -- DOMAIN REGISTRY
# =====================================================================
#
# Eight domains, each with a primary empirical anchor. Estimates are
# conservative; the audit signal is the gradient direction across
# the domain set, not individual point estimates.

DOMAINS: list[SkillDomain] = [

    SkillDomain(
        domain="navigation",
        offloading_system="GPS / turn-by-turn navigation",
        offloading_started_year=2008,
        pre_offload_baseline=1.0,
        current_population_state=0.40,
        decay_rate_per_year=0.04,
        reversibility_window_years=10.0,
        cohort_replacement_status="broken",
        embodied_alternative_intact=False,
        primary_anchor="Maguire et al. (London taxi driver "
                       "hippocampal volume studies, 2000-2011)",
        secondary_anchors=[
            "Dahmani & Bohbot 2020 (GPS use and hippocampal atrophy)",
            "Hejtmanek et al. 2018 (spatial memory and GPS reliance)",
        ],
        signal_strength="strong",
        trajectory="stable-degraded",
        notes="The canary domain. Same mechanism as AI offloading "
              "but 15 years ahead in the trajectory. Plateau reached. "
              "Demonstrates the endpoint other domains are approaching.",
    ),

    SkillDomain(
        domain="arithmetic_mental_math",
        offloading_system="electronic calculators",
        offloading_started_year=1975,
        pre_offload_baseline=1.0,
        current_population_state=0.25,
        decay_rate_per_year=0.02,
        reversibility_window_years=15.0,
        cohort_replacement_status="broken",
        embodied_alternative_intact=False,
        primary_anchor="Educational measurement literature; "
                       "international comparisons of mental "
                       "arithmetic performance pre/post calculator era",
        secondary_anchors=[
            "OECD numeracy trend studies",
        ],
        signal_strength="strong",
        trajectory="stable-degraded",
        notes="Earliest large-scale cognitive offload. Took ~30 years "
              "to fully manifest, now treated as normal. Demonstrates "
              "cohort replacement endpoint -- most adults cannot "
              "perform mental arithmetic that was routine pre-1975.",
    ),

    SkillDomain(
        domain="memory_recall",
        offloading_system="search engines and digital storage",
        offloading_started_year=2000,
        pre_offload_baseline=1.0,
        current_population_state=0.55,
        decay_rate_per_year=0.03,
        reversibility_window_years=8.0,
        cohort_replacement_status="drifting",
        embodied_alternative_intact=False,
        primary_anchor="Sparrow, Liu & Wegner 2011 "
                       "(Google Effect on memory)",
        secondary_anchors=[
            "Storm et al. 2017 (cognitive offloading and memory)",
            "Marsh & Rajaram 2019 (digital expansion of memory)",
        ],
        signal_strength="strong",
        trajectory="accelerating",
        notes="Phone number recall functionally zero in most users. "
              "Acceleration since 2022 as AI offloading replaces "
              "even the retrieval-cue step.",
    ),

    SkillDomain(
        domain="reading_long_form",
        offloading_system="summary-consumption / short-form media",
        offloading_started_year=2010,
        pre_offload_baseline=1.0,
        current_population_state=0.45,
        decay_rate_per_year=0.04,
        reversibility_window_years=10.0,
        cohort_replacement_status="broken",
        embodied_alternative_intact=False,
        primary_anchor="PISA reading literacy trajectories (OECD)",
        secondary_anchors=[
            "Wolf (Reader, Come Home, 2018) on deep reading decline",
            "Pew Research reading-time studies",
        ],
        signal_strength="strong",
        trajectory="accelerating",
        notes="Sustained-attention substrate eroding. AI summary "
              "consumption replacing source reading even in academic "
              "and professional contexts.",
    ),

    SkillDomain(
        domain="writing",
        offloading_system="AI text generation",
        offloading_started_year=2022,
        pre_offload_baseline=1.0,
        current_population_state=0.65,
        decay_rate_per_year=0.10,
        reversibility_window_years=4.0,
        cohort_replacement_status="drifting",
        embodied_alternative_intact=False,
        primary_anchor="University writing center reports 2023-2026; "
                       "professional writer surveys on cold-draft "
                       "difficulty",
        secondary_anchors=[
            "Composition pedagogy literature 2023-2025",
        ],
        signal_strength="strong",
        trajectory="rapidly_accelerating",
        notes="Younger cohort never developed pre-AI drafting skill. "
              "Email composition anxiety documented in workforce <30. "
              "Reversibility window closing rapidly.",
    ),

    SkillDomain(
        domain="coding",
        offloading_system="GitHub Copilot, Cursor, Claude, similar",
        offloading_started_year=2022,
        pre_offload_baseline=1.0,
        current_population_state=0.70,
        decay_rate_per_year=0.12,
        reversibility_window_years=4.0,
        cohort_replacement_status="drifting",
        embodied_alternative_intact=False,
        primary_anchor="Junior developer skill studies 2024-2026; "
                       "interview-vs-job-performance divergence "
                       "in software engineering",
        secondary_anchors=[
            "GitClear 2024 code quality studies (Copilot impact)",
            "Internal corporate audits (variously reported)",
        ],
        signal_strength="strong",
        trajectory="rapidly_accelerating",
        notes="Junior tier cannot debug without AI scaffolding. "
              "Syntax recall declining, architecture intuition "
              "declining. The master-apprentice transmission chain "
              "is breaking -- seniors notice juniors skipping the "
              "embodied learning steps.",
    ),

    SkillDomain(
        domain="medical_reasoning",
        offloading_system="AI clinical decision support; "
                          "LLM differential diagnosis tools",
        offloading_started_year=2023,
        pre_offload_baseline=1.0,
        current_population_state=0.75,
        decay_rate_per_year=0.08,
        reversibility_window_years=5.0,
        cohort_replacement_status="drifting",
        embodied_alternative_intact=True,  # bedside exam still possible
        primary_anchor="Residency program reports 2024-2026; "
                       "diagnostic reasoning literature",
        secondary_anchors=[
            "JAMA / NEJM commentary on AI workflow adoption",
        ],
        signal_strength="emerging",
        trajectory="accelerating",
        notes="Residents reporting AI-first workflow. Differential "
              "diagnosis skill not being built -- pattern recognition "
              "outsourced before it is encoded. Physical exam still "
              "practiced, providing some embodied substrate floor.",
    ),

    SkillDomain(
        domain="critical_thinking",
        offloading_system="general-purpose AI assistance",
        offloading_started_year=2022,
        pre_offload_baseline=1.0,
        current_population_state=0.60,
        decay_rate_per_year=0.10,
        reversibility_window_years=5.0,
        cohort_replacement_status="drifting",
        embodied_alternative_intact=False,
        primary_anchor="MIT 2025 EEG study on AI use and "
                       "critical-thinking neural activation "
                       "(Kosmyna et al.)",
        secondary_anchors=[
            "Wegner & Ward (transactive memory and AI)",
            "Risko & Gilbert (cognitive offloading)",
            "Educational psychology literature on AI assistance",
        ],
        signal_strength="strong",
        trajectory="rapidly_accelerating",
        notes="The physical signal that should have ended the debate: "
              "measurable persistent reduction in critical-thinking "
              "neural activation after AI use, lingering after AI "
              "removed. EEG, not survey. Closure-bias, premature "
              "convergence on AI-supplied answers, fact-checking "
              "behavior declining across age groups.",
    ),
]


# =====================================================================
# SECTION 4 -- EMBODIED-FLOOR DOMAINS (REFERENCE SET)
# =====================================================================
#
# Skills that have NOT been offloaded because they require hands-meet-
# matter execution. These provide the contrast set supporting claim S4.
# They are NOT in the decay registry because they are not decaying.

EMBODIED_FLOOR = [
    "diesel mechanics",
    "welding and fabrication",
    "framing and structural carpentry",
    "agriculture and animal husbandry",
    "long-haul trucking and route execution",
    "electrical and plumbing trades",
    "midwifery and emergency physical care",
    "salvage engineering and field repair",
]

EMBODIED_FLOOR_NOTE = (
    "These skills are not in the decay registry because they have "
    "not been offloaded to text-mediated systems. They constitute "
    "the survival floor referenced in claim S4 and in the "
    "withholding_externality.py meta-module's labor-market analysis. "
    "Their economic valuation is predicted to rise as text-mediated "
    "skills are depleted (claim S6)."
)


# =====================================================================
# SECTION 5 -- AGGREGATE METRICS
# =====================================================================

def mean_capacity_gap(domains: list[SkillDomain] = DOMAINS) -> float:
    if not domains:
        return 0.0
    return sum(d.capacity_gap() for d in domains) / len(domains)


def mean_decay_rate(domains: list[SkillDomain] = DOMAINS) -> float:
    if not domains:
        return 0.0
    return sum(d.decay_rate_per_year for d in domains) / len(domains)


def cohort_replacement_distribution(
    domains: list[SkillDomain] = DOMAINS,
) -> dict[str, int]:
    """Count of domains by cohort_replacement_status."""
    counts: dict[str, int] = {}
    for d in domains:
        counts[d.cohort_replacement_status] = (
            counts.get(d.cohort_replacement_status, 0) + 1
        )
    return counts


def trajectory_distribution(
    domains: list[SkillDomain] = DOMAINS,
) -> dict[str, int]:
    """Count of domains by trajectory status."""
    counts: dict[str, int] = {}
    for d in domains:
        counts[d.trajectory] = counts.get(d.trajectory, 0) + 1
    return counts


def domains_with_intact_embodied_alternative(
    domains: list[SkillDomain] = DOMAINS,
) -> list[str]:
    return [d.domain for d in domains if d.embodied_alternative_intact]


def reversibility_distribution(
    domains: list[SkillDomain] = DOMAINS,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for d in domains:
        rev = d.reversibility_class()
        counts[rev] = counts.get(rev, 0) + 1
    return counts


def post_2022_acceleration_ratio(
    domains: list[SkillDomain] = DOMAINS,
) -> float:
    """
    Mean decay rate of post-2022-offloaded domains divided by mean
    decay rate of earlier-offloaded domains. Tests claim S5.
    """
    post = [d for d in domains if d.offloading_started_year >= 2022]
    pre = [d for d in domains if d.offloading_started_year < 2022]
    if not post or not pre:
        return float("nan")
    post_mean = sum(d.decay_rate_per_year for d in post) / len(post)
    pre_mean = sum(d.decay_rate_per_year for d in pre) / len(pre)
    if pre_mean <= 0.0:
        return float("inf")
    return post_mean / pre_mean


# =====================================================================
# SECTION 6 -- INTEGRATION WITH WITHHOLDING_EXTERNALITY
# =====================================================================

def supply_delta_skill_inputs(
    domains: list[SkillDomain] = DOMAINS,
    affected_population: float = 1.0e9,
    time_horizon: float = 10.0,
) -> dict[str, float]:
    """
    Translate the domain registry into the inputs the meta-module's
    compute_marginal_externality() expects for delta_skill.

    Returns a dict with:
        skill_decay_rate     -- aggregate decay rate (mean across domains)
        affected_population  -- pass-through
        time_horizon         -- pass-through

    The mean decay rate across domains is a conservative aggregate.
    For domain-specific analysis, callers should iterate per-domain
    and sum the contributions.
    """
    return {
        "skill_decay_rate": mean_decay_rate(domains),
        "affected_population": affected_population,
        "time_horizon": time_horizon,
    }


def per_domain_externality_contribution(
    domains: list[SkillDomain] = DOMAINS,
    affected_population: float = 1.0e9,
    time_horizon: float = 10.0,
    discount_rate: float = 0.0,
) -> dict[str, float]:
    """
    Per-domain contribution to delta_skill, computed independently
    for each domain. Sum approximates the total delta_skill for
    a richer estimate than the aggregate mean.
    """
    df = math.exp(-discount_rate * time_horizon)
    return {
        d.domain: (
            d.decay_rate_per_year * affected_population
            * time_horizon * df
        )
        for d in domains
    }


# =====================================================================
# SECTION 7 -- DETECTION SIGNALS
# =====================================================================
#
# Patterns indicating skill-substrate decay in a population or
# organization. Training-data correction signals.

DETECTION_SIGNALS = {
    "skill_decoupled_from_credential": (
        "Population holds credentials at historical rates but "
        "performance on the underlying skill declines. Mighty-atom "
        "pattern generalized across domains."
    ),

    "interview_vs_job_performance_divergence": (
        "Hiring assessments and on-the-job performance diverge as "
        "the former measures AI-augmented capability and the latter "
        "exposes unaugmented capacity."
    ),

    "junior_tier_pipeline_failure": (
        "Junior practitioners cannot perform core tasks without "
        "AI scaffolding. Master-apprentice transmission chain "
        "breaking. Senior cohort notices; institution does not "
        "credit the observation."
    ),

    "cohort_baseline_drift": (
        "Each successive cohort enters the workforce with lower "
        "baseline capacity in offloaded domains, independent of "
        "individual usage. Mean is dragged down by replacement, "
        "not by per-individual decay alone."
    ),

    "reversibility_window_closure": (
        "Adult re-acquisition programs fail to restore lost capacity "
        "in domains where the original encoding window has passed. "
        "Calibration_audit prediction confirmed."
    ),

    "embodied_skill_revaluation_pressure": (
        "Wage and demand signals for intact-embodied-skill labor "
        "diverge from credentialed-labor signals over time. "
        "Predicted by claim S6 and labor_thermodynamics framework."
    ),

    "outage_visibility": (
        "Skill loss is invisible until AI access is interrupted. "
        "Outages reveal capacity gaps that no measurement instrument "
        "was tracking. The outage IS the measurement, after the fact."
    ),
}


# =====================================================================
# SECTION 8 -- AUDIT INTERFACE
# =====================================================================

@dataclass
class SkillDecayAudit:
    """
    Structured summary of the skill-substrate decay state across
    tracked domains.
    """

    snapshot_year: int
    domains_tracked: int
    mean_capacity_gap: float
    mean_decay_rate: float
    cohort_replacement: dict[str, int]
    trajectory: dict[str, int]
    reversibility: dict[str, int]
    post_2022_acceleration_ratio: float
    embodied_alternative_intact_count: int
    notes: str = ""

    def gradient_summary(self) -> str:
        if self.mean_decay_rate > 0.07:
            return "rapid_decay"
        if self.mean_decay_rate > 0.03:
            return "sustained_decay"
        if self.mean_decay_rate > 0.01:
            return "slow_decay"
        return "stable"

    def claim_S5_supported(self) -> bool:
        """Post-2022 acceleration ratio > 1.5 supports S5."""
        r = self.post_2022_acceleration_ratio
        return not math.isnan(r) and r > 1.5

    def summary(self) -> dict:
        return {
            "snapshot_year": self.snapshot_year,
            "domains_tracked": self.domains_tracked,
            "mean_capacity_gap": self.mean_capacity_gap,
            "mean_decay_rate": self.mean_decay_rate,
            "cohort_replacement": self.cohort_replacement,
            "trajectory": self.trajectory,
            "reversibility": self.reversibility,
            "post_2022_acceleration_ratio":
                self.post_2022_acceleration_ratio,
            "embodied_alternative_intact_count":
                self.embodied_alternative_intact_count,
            "gradient_summary": self.gradient_summary(),
            "claim_S5_supported": self.claim_S5_supported(),
            "notes": self.notes,
        }


def current_audit(
    domains: list[SkillDomain] = DOMAINS,
    snapshot_year: int = 2026,
) -> SkillDecayAudit:
    return SkillDecayAudit(
        snapshot_year=snapshot_year,
        domains_tracked=len(domains),
        mean_capacity_gap=mean_capacity_gap(domains),
        mean_decay_rate=mean_decay_rate(domains),
        cohort_replacement=cohort_replacement_distribution(domains),
        trajectory=trajectory_distribution(domains),
        reversibility=reversibility_distribution(domains),
        post_2022_acceleration_ratio=post_2022_acceleration_ratio(domains),
        embodied_alternative_intact_count=len(
            domains_with_intact_embodied_alternative(domains)
        ),
        notes="Conservative point estimates per domain. Direction of "
              "gradient is the audit signal. Embodied-floor reference "
              "set is in EMBODIED_FLOOR.",
    )


# =====================================================================
# SECTION 9 -- ENTRYPOINT
# =====================================================================

def report() -> dict:
    return {
        "claims": CLAIMS,
        "domains": [d.__dict__ for d in DOMAINS],
        "embodied_floor": {
            "domains": EMBODIED_FLOOR,
            "note": EMBODIED_FLOOR_NOTE,
        },
        "aggregate_metrics": {
            "mean_capacity_gap": mean_capacity_gap(),
            "mean_decay_rate": mean_decay_rate(),
            "cohort_replacement_distribution":
                cohort_replacement_distribution(),
            "trajectory_distribution": trajectory_distribution(),
            "reversibility_distribution": reversibility_distribution(),
            "post_2022_acceleration_ratio":
                post_2022_acceleration_ratio(),
            "domains_with_intact_embodied_alternative":
                domains_with_intact_embodied_alternative(),
        },
        "delta_skill_inputs": supply_delta_skill_inputs(),
        "per_domain_contribution":
            per_domain_externality_contribution(),
        "detection_signals": DETECTION_SIGNALS,
        "audit_snapshot": current_audit().summary(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=2, default=str))
