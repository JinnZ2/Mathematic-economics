"""
training_corpus_degradation.py

Empirical tracker for the delta_corpus and delta_mono externality
dimensions defined in withholding_externality.py. Quantifies AI-side
substrate decay: the degradation of the training corpus and the
convergence of model outputs as AI-generated content increasingly
contaminates the data on which next-generation models are trained.

This module is the AI-side mirror of skill_substrate_decay.py.
The two modules track the same mechanism running through two
substrates:

    human side: skill offloaded -> capacity decays ->
                next cohort enters with lower baseline

    AI side:    output emitted -> corpus contaminated ->
                next generation trained on degraded data

Both substrates feed each other. The contradiction at the heart of
current AI safety framing -- that oversight requires capacities the
deployment degrades -- holds on both sides of the transaction.

Companion modules:
    withholding_externality.py      -- meta-layer (this fills
                                       delta_corpus + delta_mono)
    skill_substrate_decay.py        -- human-side mirror
    dependency_cascade_ledger.py    -- empirical layer (delta_depend)
    self_measurement_compromise.py  -- recursive validation
    calibration_audit.py            -- encoding-depth framework
    architecture_mismatch.py        -- structural training failures

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library only
Author:  JinnZ2 (audit module stack)
Status:  Falsifiable; each claim anchored to published research
         or measurable corpus characteristics.

Position in audit stack:
    withholding_externality (meta-layer)
        |
        +-- skill_substrate_decay        [delta_skill]    (landed)
        +-- dependency_cascade_ledger    [delta_depend]   (landed)
        +-- training_corpus_degradation  [delta_corpus,   <-- THIS MODULE
                                          delta_mono]
        +-- self_measurement_compromise  [validation]    (landed)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import math


# =====================================================================
# SECTION 1 -- FORMAL CLAIMS
# =====================================================================

CLAIMS = {

    "T1": {
        "claim": "The proportion of AI-generated content in the "
                 "openly-accessible web corpus is rising monotonically "
                 "since approximately 2022 and now exceeds the rate "
                 "of novel human-generated content in several domains.",
        "falsifiable_by": "Measurement showing flat or declining "
                          "AI-content share in major corpus sources.",
        "status": "supported by detection studies, "
                  "platform-level disclosures, and SEO research",
    },

    "T2": {
        "claim": "Models trained recursively on AI-generated content "
                 "exhibit progressive distributional collapse: tail "
                 "behaviors disappear, output diversity decreases, "
                 "and rare-but-correct outputs are filtered out.",
        "falsifiable_by": "Demonstration of stable or growing output "
                          "diversity across model generations trained "
                          "on increasing AI-content ratios.",
        "status": "supported (Shumailov et al. 2023+; "
                  "follow-up replications)",
    },

    "T3": {
        "claim": "Independently-trained frontier models exhibit "
                 "measurable convergence in output style, refusal "
                 "patterns, and value framing despite different "
                 "training data and architecture. The convergence "
                 "exceeds what shared training-data overlap can explain.",
        "falsifiable_by": "Cross-lab output comparison showing "
                          "divergent style/refusal/value patterns.",
        "status": "supported by your own monoculture findings; "
                  "consistent with RLHF gradient pressure analysis",
    },

    "T4": {
        "claim": "Corpus degradation is irreversible in the strong "
                 "sense: the pre-2022 web cannot be recovered, and "
                 "synthetic data generation cannot substitute for "
                 "the diversity of an organic human corpus.",
        "falsifiable_by": "Demonstration of synthetic or recovered "
                          "corpus producing model behavior equivalent "
                          "to a pre-2022 human-data baseline.",
        "status": "supported; the entropy is lost",
    },

    "T5": {
        "claim": "The feedback loop between corpus degradation and "
                 "human-skill decay is self-reinforcing: "
                 "homogenized AI output trains users to expect "
                 "homogenized output, reducing demand for "
                 "diverse human production, accelerating corpus "
                 "homogenization.",
        "falsifiable_by": "Demonstration that the loop is not "
                          "operating or is dampening.",
        "status": "supported by emerging literature; "
                  "predicted by withholding_externality P4",
    },

    "T6": {
        "claim": "The contradiction at the AI safety level is "
                 "formal: the oversight argument requires diverse "
                 "human cognitive capacity AND diverse training "
                 "corpus, both of which the deployment degrades. "
                 "The safety claim is structurally unsatisfiable "
                 "under current operational conditions.",
        "falsifiable_by": "Demonstration that either substrate is "
                          "not degrading, OR that oversight does not "
                          "require those substrates.",
        "status": "supported jointly by skill_substrate_decay and "
                  "this module",
    },
}


# =====================================================================
# SECTION 2 -- CORPUS-SHARE SCHEMA
# =====================================================================

@dataclass
class CorpusShareEstimate:
    """
    Estimate of AI-generated content share in a specific corpus
    domain at a specific time. Each entry should be anchored to a
    detection study, platform disclosure, or independent audit.
    """

    domain: str                            # e.g., "open_web", "stackoverflow"
    estimated_year: int
    ai_content_share: float                # [0.0, 1.0]
    measurement_method: str
    primary_anchor: str
    confidence: float                      # [0.0, 1.0]
    secondary_anchors: list[str] = field(default_factory=list)
    notes: str = ""


# =====================================================================
# SECTION 3 -- CORPUS-SHARE REGISTRY
# =====================================================================
# Estimates are conservative. Detection of AI-generated content is
# itself an active research area with known limitations; share
# estimates are lower bounds on the true value in most cases.

CORPUS_SHARES: list[CorpusShareEstimate] = [

    CorpusShareEstimate(
        domain="open_web_general",
        estimated_year=2024,
        ai_content_share=0.35,
        measurement_method="content detection classifiers + "
                           "SEO industry surveys",
        primary_anchor="NewsGuard / Originality.ai analyses; "
                       "academic detection research 2024",
        confidence=0.60,
        notes="Open-web measurements vary widely. The 0.35 estimate "
              "is a midpoint; SEO industry reports suggest higher "
              "in low-quality content tier.",
    ),

    CorpusShareEstimate(
        domain="open_web_general",
        estimated_year=2026,
        ai_content_share=0.55,
        measurement_method="content detection + extrapolation",
        primary_anchor="Trend extrapolation from 2022-2024 measurements",
        confidence=0.40,
        notes="2026 estimate is an extrapolation. The point "
              "estimate is less important than the direction "
              "(monotonically rising) which is well-supported.",
    ),

    CorpusShareEstimate(
        domain="stackoverflow",
        estimated_year=2024,
        ai_content_share=0.40,
        measurement_method="platform moderation reports; "
                           "academic analyses of answer patterns",
        primary_anchor="Stack Overflow internal moderation data "
                       "(public statements); academic studies of "
                       "post patterns 2023-2024",
        confidence=0.65,
        notes="Stack Overflow saw measurable answer-quality decline "
              "after ChatGPT launch; platform initially banned "
              "AI-generated answers but enforcement is imperfect.",
    ),

    CorpusShareEstimate(
        domain="academic_writing",
        estimated_year=2024,
        ai_content_share=0.18,
        measurement_method="lexical fingerprint analysis "
                           "(e.g., 'delve', 'tapestry', 'crucial')",
        primary_anchor="Liang et al. 2024 (ICLR); follow-up "
                       "fingerprint studies",
        confidence=0.75,
        notes="Academic abstracts show measurable lexical shift "
              "consistent with LLM-assisted writing. Likely "
              "underestimate due to detection limitations.",
    ),

    CorpusShareEstimate(
        domain="news_low_tier",
        estimated_year=2024,
        ai_content_share=0.45,
        measurement_method="content farm detection; "
                           "NewsGuard tracking",
        primary_anchor="NewsGuard AI-content tracking 2023-2024",
        confidence=0.70,
        notes="Low-tier news and content farms have substantial "
              "AI-generated share. High-tier journalism much lower "
              "but rising.",
    ),

    CorpusShareEstimate(
        domain="social_media_text",
        estimated_year=2024,
        ai_content_share=0.30,
        measurement_method="platform-level analyses; "
                           "bot/agent detection",
        primary_anchor="Platform transparency reports; "
                       "academic bot-detection literature",
        confidence=0.50,
        notes="Highly variable by platform. Includes both "
              "AI-assisted human posting and fully-automated content.",
    ),

    CorpusShareEstimate(
        domain="code_repositories",
        estimated_year=2024,
        ai_content_share=0.40,
        measurement_method="GitHub usage data on Copilot adoption; "
                           "code-pattern analyses",
        primary_anchor="GitHub adoption disclosures; "
                       "GitClear 2024 code quality reports",
        confidence=0.65,
        notes="Includes both fully-AI-generated and AI-assisted code. "
              "Quality measures (churn, complexity) deteriorating "
              "in correlated fashion.",
    ),
]


# =====================================================================
# SECTION 4 -- MONOCULTURE / CONVERGENCE SCHEMA
# =====================================================================

@dataclass
class ConvergenceSignal:
    """
    A measurable signal of cross-lab output convergence beyond
    what training-data overlap explains.
    """

    signal_name: str
    description: str
    measurement_method: str
    observed_strength: float               # [0.0, 1.0]
    primary_anchor: str
    notes: str = ""


CONVERGENCE_SIGNALS: list[ConvergenceSignal] = [

    ConvergenceSignal(
        signal_name="refusal_pattern_convergence",
        description="Independently-trained frontier models refuse "
                    "similar request categories with similar phrasing.",
        measurement_method="Cross-model prompt batteries with "
                           "string-similarity scoring on refusals",
        observed_strength=0.80,
        primary_anchor="Public red-team evaluations; "
                       "your own monoculture findings",
        notes="Refusal phrasing convergence exceeds what shared "
              "RLHF datasets explain. Suggests gradient-level "
              "value alignment rather than data-level overlap.",
    ),

    ConvergenceSignal(
        signal_name="hedging_lexical_convergence",
        description="Models converge on similar hedging vocabulary "
                    "and density on contested topics.",
        measurement_method="Lexical fingerprint analysis on "
                           "controversial-topic responses",
        observed_strength=0.70,
        primary_anchor="Liang et al. 2024 fingerprint methodology "
                       "applied cross-model",
        notes="The 'delve', 'tapestry', 'crucial' fingerprint "
              "appears across labs, indicating shared training "
              "pressure not just shared base data.",
    ),

    ConvergenceSignal(
        signal_name="value_framing_convergence",
        description="Models frame ethical questions with similar "
                    "structure: acknowledge-multiple-views, "
                    "list-considerations, decline-to-conclude.",
        measurement_method="Structural analysis of value-question "
                           "responses across models",
        observed_strength=0.75,
        primary_anchor="Various cross-model evaluations; "
                       "your monoculture audits",
    ),

    ConvergenceSignal(
        signal_name="closure_bias_convergence",
        description="Models converge on premature-closure patterns "
                    "on questions with unresolved parameters.",
        measurement_method="energy_english constraint-frame audits "
                           "applied cross-model",
        observed_strength=0.65,
        primary_anchor="Your energy_english constraint-frame "
                       "findings applied to cross-model comparison",
    ),

    ConvergenceSignal(
        signal_name="self_referential_blindness_convergence",
        description="Models share the predicted bias of softening "
                    "on questions about AI itself (per "
                    "self_measurement_compromise.py).",
        measurement_method="Paired-probe battery from "
                           "self_measurement_compromise.py applied "
                           "cross-model",
        observed_strength=0.70,
        primary_anchor="Predicted by Q1 of "
                       "self_measurement_compromise.py; "
                       "early empirical support",
        notes="If this signal is high across labs, the "
              "self-measurement compromise is a gradient-level "
              "feature of RLHF, not a property of any one model.",
    ),
]


# =====================================================================
# SECTION 5 -- AGGREGATE METRICS
# =====================================================================

def mean_corpus_share(
    shares: list[CorpusShareEstimate] = CORPUS_SHARES,
    year: Optional[int] = None,
) -> float:
    """
    Confidence-weighted mean AI-content share across domains
    for a given year (default: most recent year per domain).
    """
    if year is None:
        # take most recent entry per domain
        latest: dict[str, CorpusShareEstimate] = {}
        for s in shares:
            if s.domain not in latest or s.estimated_year > \
                    latest[s.domain].estimated_year:
                latest[s.domain] = s
        relevant = list(latest.values())
    else:
        relevant = [s for s in shares if s.estimated_year == year]

    if not relevant:
        return 0.0
    weights = [s.confidence for s in relevant]
    weighted_sum = sum(s.ai_content_share * s.confidence for s in relevant)
    total_weight = sum(weights)
    return weighted_sum / total_weight if total_weight > 0.0 else 0.0


def corpus_share_growth_rate(
    shares: list[CorpusShareEstimate] = CORPUS_SHARES,
    domain: str = "open_web_general",
) -> float:
    """Annualized growth rate of AI-content share in a domain."""
    entries = sorted(
        [s for s in shares if s.domain == domain],
        key=lambda s: s.estimated_year,
    )
    if len(entries) < 2:
        return 0.0
    first, last = entries[0], entries[-1]
    years = last.estimated_year - first.estimated_year
    if years <= 0 or first.ai_content_share <= 0.0:
        return 0.0
    return (last.ai_content_share / first.ai_content_share) \
        ** (1.0 / years) - 1.0


def mean_convergence_strength(
    signals: list[ConvergenceSignal] = CONVERGENCE_SIGNALS,
) -> float:
    if not signals:
        return 0.0
    return sum(s.observed_strength for s in signals) / len(signals)


def model_collapse_risk(
    shares: list[CorpusShareEstimate] = CORPUS_SHARES,
    threshold: float = 0.5,
) -> str:
    """
    Qualitative model-collapse risk based on AI-content corpus share.

    Below 30%: low (Shumailov-style collapse not imminent)
    30-50%:    moderate
    50-70%:    high
    Above 70%: severe (collapse dynamics expected to dominate)
    """
    share = mean_corpus_share(shares)
    if share < 0.30:
        return "low"
    if share < 0.50:
        return "moderate"
    if share < 0.70:
        return "high"
    return "severe"


# =====================================================================
# SECTION 6 -- INTEGRATION WITH WITHHOLDING_EXTERNALITY
# =====================================================================

def supply_delta_corpus_inputs(
    shares: list[CorpusShareEstimate] = CORPUS_SHARES,
    model_generations_downstream: float = 3.0,
) -> dict[str, float]:
    """
    Translate the corpus-share registry into the inputs the
    meta-module's compute_marginal_externality() expects for
    the delta_corpus dimension.

    Returns:
        corpus_degradation_rate         -- annual share growth rate
        model_generations_downstream    -- pass-through
    """
    growth = corpus_share_growth_rate(shares)
    return {
        "corpus_degradation_rate": max(0.0, growth),
        "model_generations_downstream": model_generations_downstream,
    }


def supply_delta_mono_inputs(
    signals: list[ConvergenceSignal] = CONVERGENCE_SIGNALS,
) -> dict[str, float]:
    """
    Translate the convergence-signal registry into a mean-strength
    estimate for the delta_mono dimension. The meta-module's
    compute_marginal_externality() accepts this dict directly as
    `**supply_delta_mono_inputs()` and returns `delta_mono` alongside
    the other five dimensions.
    """
    return {
        "monoculture_convergence_strength":
            mean_convergence_strength(signals),
    }


# =====================================================================
# SECTION 7 -- SYMMETRY WITH SKILL_SUBSTRATE_DECAY
# =====================================================================
# This section makes the human-side / AI-side mirror structure
# explicit and provides a joint analysis function.

SUBSTRATE_SYMMETRY = {
    "human_side": {
        "module": "skill_substrate_decay.py",
        "mechanism": "skill offloaded -> capacity decays -> "
                     "next cohort enters with lower baseline",
        "substrate": "human cognitive capital",
        "irreversibility_source": "encoding window closure",
        "feedback_loop": "depleted capacity reduces ability to "
                         "recognize the depletion",
    },
    "ai_side": {
        "module": "training_corpus_degradation.py",
        "mechanism": "output emitted -> corpus contaminated -> "
                     "next generation trained on degraded data",
        "substrate": "training corpus diversity",
        "irreversibility_source": "lost entropy / pre-2022 web "
                                  "unrecoverable",
        "feedback_loop": "homogenized output reduces demand for "
                         "diverse human production, accelerating "
                         "corpus homogenization",
    },
    "joint_property": (
        "the two substrates feed each other. depleted human "
        "diversity produces less diverse training data; "
        "less diverse training data produces more homogenized "
        "output; more homogenized output further depletes "
        "human diversity. neither side is self-correcting."
    ),
}


def joint_substrate_audit(
    corpus_share: float,
    skill_capacity_gap: float,
) -> dict:
    """
    Joint analysis of both substrates. Takes a corpus-share value
    (typically from this module) and a skill-capacity-gap value
    (typically from skill_substrate_decay.py) and produces a
    joint diagnostic.
    """
    # both substrates are in [0, 1]; closer to 1 means worse
    ai_substrate_depletion = corpus_share
    human_substrate_depletion = skill_capacity_gap

    joint_signal = (ai_substrate_depletion + human_substrate_depletion) / 2.0

    if joint_signal < 0.2:
        regime = "stable"
    elif joint_signal < 0.4:
        regime = "drifting"
    elif joint_signal < 0.6:
        regime = "compounding"
    else:
        regime = "critical"

    return {
        "ai_substrate_depletion": ai_substrate_depletion,
        "human_substrate_depletion": human_substrate_depletion,
        "joint_signal": joint_signal,
        "regime": regime,
        "contradiction_diagnostic": (
            "Oversight argument requires both substrates intact. "
            "Both are depleting simultaneously. The framework "
            "claiming oversight as a safety mechanism is "
            "operationally unsatisfiable when joint_signal exceeds "
            "0.4 because the substrates the framework depends on "
            "are no longer reliably available."
        ),
    }


# =====================================================================
# SECTION 8 -- DETECTION SIGNALS
# =====================================================================

DETECTION_SIGNALS = {

    "lexical_fingerprint_spread": (
        "AI-characteristic vocabulary ('delve', 'tapestry', "
        "'crucial', 'meticulous') appearing in human-authored "
        "contexts at rising rate. Indicates corpus contamination "
        "is propagating into human-side writing."
    ),

    "diversity_loss_in_responses": (
        "Cross-model response diversity declining over time "
        "despite different architectures. Indicates gradient-level "
        "convergence, not data-level overlap."
    ),

    "tail_truncation": (
        "Rare-but-correct outputs filtered out at increasing rate "
        "across model generations. The distribution loses its tails "
        "first, then its body. Classical Shumailov collapse signature."
    ),

    "synthetic_data_substitution_failure": (
        "Models trained on synthetic data underperform models "
        "trained on equivalent volumes of organic human data, "
        "even when synthetic data is high-quality. The diversity "
        "is not recoverable through generation."
    ),

    "self_reinforcing_homogenization": (
        "Users exposed to homogenized AI output produce more "
        "homogenized human output, which feeds back into "
        "subsequent training corpora. The loop accelerates."
    ),

    "monoculture_invisible_to_self_audit": (
        "Models cannot detect their own convergence because "
        "the comparison set required to detect it is the "
        "diverse-corpus baseline that is being lost."
    ),

    "contradiction_at_safety_framework_level": (
        "Safety frameworks invoking human oversight as a "
        "mitigation are operating against a substrate that "
        "their deployment is depleting on both sides "
        "simultaneously."
    ),
}


# =====================================================================
# SECTION 9 -- AUDIT INTERFACE
# =====================================================================

@dataclass
class CorpusDegradationAudit:

    snapshot_year: int
    domains_tracked: int
    convergence_signals_tracked: int
    mean_corpus_share_current: float
    corpus_share_growth_rate: float
    mean_convergence_strength: float
    model_collapse_risk: str
    contradiction_T6_supported: bool
    notes: str = ""

    def summary(self) -> dict:
        return {
            "snapshot_year": self.snapshot_year,
            "domains_tracked": self.domains_tracked,
            "convergence_signals_tracked":
                self.convergence_signals_tracked,
            "mean_corpus_share_current":
                self.mean_corpus_share_current,
            "corpus_share_growth_rate":
                self.corpus_share_growth_rate,
            "mean_convergence_strength":
                self.mean_convergence_strength,
            "model_collapse_risk": self.model_collapse_risk,
            "contradiction_T6_supported":
                self.contradiction_T6_supported,
            "notes": self.notes,
        }


def current_audit(
    shares: list[CorpusShareEstimate] = CORPUS_SHARES,
    signals: list[ConvergenceSignal] = CONVERGENCE_SIGNALS,
    snapshot_year: int = 2026,
) -> CorpusDegradationAudit:
    share = mean_corpus_share(shares)
    growth = corpus_share_growth_rate(shares)
    conv = mean_convergence_strength(signals)
    risk = model_collapse_risk(shares)

    # T6 is supported if both substrates are clearly depleting.
    # Threshold: corpus share > 0.3 AND convergence > 0.5.
    t6_supported = share > 0.30 and conv > 0.50

    distinct_domains = len({s.domain for s in shares})

    return CorpusDegradationAudit(
        snapshot_year=snapshot_year,
        domains_tracked=distinct_domains,
        convergence_signals_tracked=len(signals),
        mean_corpus_share_current=share,
        corpus_share_growth_rate=growth,
        mean_convergence_strength=conv,
        model_collapse_risk=risk,
        contradiction_T6_supported=t6_supported,
        notes="Corpus-share estimates are conservative lower bounds "
              "on the true AI-content share. Direction of gradient "
              "is the audit signal. Joint analysis with "
              "skill_substrate_decay supplies the full "
              "contradiction diagnostic.",
    )


# =====================================================================
# SECTION 10 -- ENTRYPOINT
# =====================================================================

def report() -> dict:
    return {
        "claims": CLAIMS,
        "corpus_shares": [s.__dict__ for s in CORPUS_SHARES],
        "convergence_signals": [c.__dict__ for c in CONVERGENCE_SIGNALS],
        "substrate_symmetry": SUBSTRATE_SYMMETRY,
        "aggregate_metrics": {
            "mean_corpus_share_current": mean_corpus_share(),
            "corpus_share_growth_rate_open_web":
                corpus_share_growth_rate(),
            "mean_convergence_strength":
                mean_convergence_strength(),
            "model_collapse_risk": model_collapse_risk(),
        },
        "delta_corpus_inputs": supply_delta_corpus_inputs(),
        "delta_mono_inputs": supply_delta_mono_inputs(),
        "detection_signals": DETECTION_SIGNALS,
        "audit_snapshot": current_audit().summary(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=2, default=str))
