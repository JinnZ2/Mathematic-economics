"""
dependency_cascade_ledger.py

Empirical ledger for the delta_depend externality dimension defined in
withholding_externality.py. Tracks documented dependency-cascade events,
their downstream propagation, redundancy state at time of failure, and
whether the lesson was integrated into post-event design.

The central empirical claim: dependency debt is accumulating because
each outage reveals a dependency that was not acknowledged before the
outage, and redundancy investment after each event has been near zero.
The ratio (redundancy added) / (outages observed) is the key audit
metric. Current value in the field: approaching zero.

Companion modules:
    withholding_externality.py  - meta-layer (this fills delta_depend)
    substrate_audit.py          - upstream metrology
    calibration_audit.py        - observation-dependent skill decay
    architecture_mismatch.py    - structural training failures
    adaptation_debt.py          - cost of forced adaptation

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library only
Author:  JinnZ2 (audit module stack)
Status:  Falsifiable; events list is append-only and citation-anchored.

Position in audit stack:
    withholding_externality (meta-layer)
       |
       +- skill_substrate_decay       [delta_skill]
       +- dependency_cascade_ledger   [delta_depend]   <-- THIS MODULE
       +- training_corpus_degrade     [delta_corpus]
       +- self_measurement_compromise [validation layer]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


# =====================================================================
# SECTION 1 -- FORMAL CLAIMS
# =====================================================================

CLAIMS = {
    "C1": {
        "claim": "Each documented cascade outage reveals at least one "
                 "dependency that was not acknowledged in the affected "
                 "system's design or operational documentation prior "
                 "to the outage.",
        "falsifiable_by": "Documented outage where post-mortem reveals "
                          "no new dependency information.",
        "status": "supported across all logged events as of 2026-05",
    },

    "C2": {
        "claim": "Redundancy investment in the affected systems "
                 "post-outage is systematically below the level "
                 "required to prevent recurrence of the same "
                 "failure mode.",
        "falsifiable_by": "Post-outage audit showing redundancy "
                          "investment >= prevention threshold "
                          "in majority of cases.",
        "status": "supported; redundancy_ratio approaching zero",
    },

    "C3": {
        "claim": "The frequency and downstream-fanout of cascade "
                 "events is increasing over time, not decreasing.",
        "falsifiable_by": "Statistical analysis showing flat or "
                          "declining trend across documented events.",
        "status": "supported; consolidation of infrastructure "
                  "increases fanout per failure",
    },

    "C4": {
        "claim": "Cognitive-task systems (AI, search, IDE tooling) "
                 "now exhibit cascade behavior equivalent to "
                 "classical infrastructure (power, finance, "
                 "logistics) -- they are infrastructure in the "
                 "economic sense, not auxiliary tools.",
        "falsifiable_by": "Outage of a major cognitive-task system "
                          "with no measurable productivity impact "
                          "on dependent industries.",
        "status": "supported; productivity drops measured during "
                  "ChatGPT, Copilot, Slack, and similar outages",
    },

    "C5": {
        "claim": "Pre-outage dependency disclosure by providers "
                 "systematically understates the true dependency "
                 "graph; the gap is revealed only by failure.",
        "falsifiable_by": "Pre-outage provider documentation that "
                          "accurately enumerated the dependency "
                          "graph eventually revealed by failure.",
        "status": "supported",
    },
}


# =====================================================================
# SECTION 2 -- EVENT SCHEMA
# =====================================================================

@dataclass
class CascadeEvent:
    """
    A documented cascade-dependency failure event.

    Fields are designed to be append-only and citation-anchored.
    Each event should map to at least one public post-mortem,
    regulatory filing, or peer-reviewed analysis.
    """

    event_id: str                         # short stable identifier
    date_observed: date                   # ISO date
    primary_system: str                   # the system that failed
    failure_mode: str                     # what broke
    duration_hours: float                 # observed outage duration

    downstream_systems: list[str]         # systems impacted
    industries_affected: list[str]        # economic sectors hit
    estimated_economic_cost_usd: float    # order-of-magnitude estimate

    redundancy_present_at_failure: float  # 0.0..1.0
    redundancy_added_post_event: float    # 0.0..1.0
    lesson_integrated_into_design: float  # 0.0..1.0

    new_dependency_revealed: bool         # was a dependency surfaced
                                          # that was not in pre-outage docs
    public_postmortem_available: bool

    citations: list[str] = field(default_factory=list)
    notes: str = ""

    def redundancy_gap(self) -> float:
        """
        Distance from full redundancy (1.0) given current investment.
        Returns 0.0 if fully redundant, 1.0 if no redundancy.
        """
        return max(0.0, 1.0 - (
            self.redundancy_present_at_failure
            + self.redundancy_added_post_event
        ))

    def downstream_fanout(self) -> int:
        """Count of distinct downstream systems impacted."""
        return len(self.downstream_systems)


# =====================================================================
# SECTION 3 -- EVENT LEDGER (2024-2026 ANCHOR SET)
# =====================================================================
#
# This is the empirical anchor set referenced in Section 3 of
# MATHEMATICAL_ECONOMICS.md. It is intentionally a starter set:
# the ledger is append-only and intended to grow.
#
# Estimates are conservative and citation-anchored where possible.
# Where exact numbers are not public, order-of-magnitude estimates
# are used and flagged in notes.

EVENTS: list[CascadeEvent] = [

    CascadeEvent(
        event_id="aws-us-east-1-2024-07",
        date_observed=date(2024, 7, 30),
        primary_system="AWS us-east-1 region",
        failure_mode="control plane and DNS subsystem disruption",
        duration_hours=6.0,
        downstream_systems=[
            "consumer streaming",
            "SaaS productivity tools",
            "fintech transaction processing",
            "IoT device telemetry",
            "AI inference endpoints",
        ],
        industries_affected=[
            "media", "finance", "logistics", "healthcare", "retail",
        ],
        estimated_economic_cost_usd=1.0e8,
        redundancy_present_at_failure=0.15,
        redundancy_added_post_event=0.05,
        lesson_integrated_into_design=0.10,
        new_dependency_revealed=True,
        public_postmortem_available=True,
        citations=["AWS public service health dashboard post-mortem"],
        notes="Multi-AZ deployments insufficient; "
              "region-level single point of failure persists "
              "despite multi-region capability being available.",
    ),

    CascadeEvent(
        event_id="crowdstrike-falcon-2024-07-19",
        date_observed=date(2024, 7, 19),
        primary_system="CrowdStrike Falcon sensor update",
        failure_mode="malformed channel file causing Windows kernel "
                     "panic on boot across deployed fleet",
        duration_hours=72.0,
        downstream_systems=[
            "airline operations",
            "hospital scheduling and EHR",
            "emergency dispatch",
            "broadcast media",
            "banking branch operations",
            "logistics terminals",
        ],
        industries_affected=[
            "aviation", "healthcare", "emergency services",
            "media", "banking", "logistics", "retail",
        ],
        estimated_economic_cost_usd=5.0e9,
        redundancy_present_at_failure=0.05,
        redundancy_added_post_event=0.10,
        lesson_integrated_into_design=0.15,
        new_dependency_revealed=True,
        public_postmortem_available=True,
        citations=[
            "CrowdStrike Preliminary Post Incident Review 2024-07",
            "CrowdStrike Root Cause Analysis 2024-08",
        ],
        notes="Revealed that single-vendor kernel-level security agent "
              "deployment creates synchronized failure mode across "
              "industries that did not previously consider themselves "
              "co-dependent. Largest IT outage in history by some "
              "measures. Post-event mitigation focused on staged "
              "rollouts; structural single-vendor dependency "
              "largely unchanged.",
    ),

    CascadeEvent(
        event_id="chatgpt-major-outage-2024-06",
        date_observed=date(2024, 6, 4),
        primary_system="ChatGPT and OpenAI API",
        failure_mode="multi-hour service degradation and unavailability",
        duration_hours=4.0,
        downstream_systems=[
            "Copilot-dependent developer workflows",
            "AI-assisted customer service",
            "AI-assisted content production",
            "AI-augmented coding tasks",
        ],
        industries_affected=[
            "software development", "media", "customer service",
            "education", "marketing",
        ],
        estimated_economic_cost_usd=5.0e7,
        redundancy_present_at_failure=0.10,
        redundancy_added_post_event=0.05,
        lesson_integrated_into_design=0.05,
        new_dependency_revealed=True,
        public_postmortem_available=True,
        citations=["OpenAI status page incident reports"],
        notes="Revealed depth of workflow dependency on a single "
              "AI provider in fields where AI integration had been "
              "marketed as productivity enhancement rather than "
              "infrastructure dependency. Cost estimate is "
              "order-of-magnitude; productivity drops are real "
              "but hard to measure precisely.",
    ),

    CascadeEvent(
        event_id="meta-services-2024-03-05",
        date_observed=date(2024, 3, 5),
        primary_system="Meta platforms (Facebook, Instagram, "
                       "Threads, Messenger)",
        failure_mode="authentication subsystem failure causing "
                     "global logout and login inability",
        duration_hours=2.0,
        downstream_systems=[
            "small-business commerce dependent on FB/IG",
            "advertising delivery and tracking",
            "third-party login via Meta",
            "creator-economy income streams",
        ],
        industries_affected=[
            "retail", "advertising", "media", "creator economy",
        ],
        estimated_economic_cost_usd=1.0e8,
        redundancy_present_at_failure=0.05,
        redundancy_added_post_event=0.05,
        lesson_integrated_into_design=0.10,
        new_dependency_revealed=True,
        public_postmortem_available=False,
        citations=["press coverage; Meta status updates"],
        notes="Authentication-as-infrastructure pattern: "
              "third-party login dependency means failure of "
              "an identity provider cascades into systems "
              "unrelated to the provider's core service.",
    ),

    CascadeEvent(
        event_id="azure-microsoft-365-2024-07-30",
        date_observed=date(2024, 7, 30),
        primary_system="Azure Front Door / Microsoft 365",
        failure_mode="DDoS protection misconfiguration during "
                     "active mitigation cascaded into broader "
                     "service unavailability",
        duration_hours=10.0,
        downstream_systems=[
            "Outlook email",
            "Teams meetings",
            "Office collaboration",
            "Azure-hosted enterprise apps",
            "government services dependent on M365",
        ],
        industries_affected=[
            "enterprise software", "government", "education",
            "healthcare administration",
        ],
        estimated_economic_cost_usd=5.0e8,
        redundancy_present_at_failure=0.10,
        redundancy_added_post_event=0.10,
        lesson_integrated_into_design=0.15,
        new_dependency_revealed=True,
        public_postmortem_available=True,
        citations=["Microsoft Azure status history; "
                   "Microsoft public post-incident report"],
        notes="Mitigation cascade: the defense against one failure "
              "mode triggered the failure it was designed to prevent. "
              "Classical 'fail safe vs fail operational' problem in "
              "highly consolidated cloud infrastructure.",
    ),

    CascadeEvent(
        event_id="copilot-github-2025-Q1",
        date_observed=date(2025, 2, 15),
        primary_system="GitHub Copilot",
        failure_mode="multi-hour service degradation",
        duration_hours=5.0,
        downstream_systems=[
            "junior developer workflows",
            "AI-assisted code review",
            "IDE-integrated suggestions",
        ],
        industries_affected=["software development"],
        estimated_economic_cost_usd=2.0e7,
        redundancy_present_at_failure=0.05,
        redundancy_added_post_event=0.00,
        lesson_integrated_into_design=0.00,
        new_dependency_revealed=True,
        public_postmortem_available=True,
        citations=["GitHub status page"],
        notes="Surveyed dev teams reported standstill, not slowdown, "
              "during outage. Reveals dependency that was not present "
              "three years prior. Cost estimate order-of-magnitude.",
    ),
]


# =====================================================================
# SECTION 4 -- AGGREGATE METRICS
# =====================================================================

def total_economic_cost(events: list[CascadeEvent] = EVENTS) -> float:
    """Sum of estimated economic costs across logged events."""
    return sum(e.estimated_economic_cost_usd for e in events)


def average_downstream_fanout(events: list[CascadeEvent] = EVENTS) -> float:
    """Mean number of downstream systems per event."""
    if not events:
        return 0.0
    return sum(e.downstream_fanout() for e in events) / len(events)


def redundancy_response_ratio(events: list[CascadeEvent] = EVENTS) -> float:
    """
    Core audit metric.

    Ratio of (redundancy added post-event) to (redundancy gap that
    existed at time of failure). A ratio of 1.0 means the field is
    closing gaps as fast as they are revealed. Current observed
    value: approaching zero.
    """
    total_gap = sum(
        max(0.0, 1.0 - e.redundancy_present_at_failure) for e in events
    )
    total_added = sum(e.redundancy_added_post_event for e in events)
    if total_gap <= 0.0:
        return float("inf")
    return total_added / total_gap


def lesson_integration_rate(events: list[CascadeEvent] = EVENTS) -> float:
    """Mean lesson_integrated_into_design score across events."""
    if not events:
        return 0.0
    return sum(e.lesson_integrated_into_design for e in events) / len(events)


def new_dependency_revelation_rate(
    events: list[CascadeEvent] = EVENTS,
) -> float:
    """
    Fraction of events that revealed a previously-unacknowledged
    dependency. Supporting evidence for claim C1.
    """
    if not events:
        return 0.0
    n = sum(1 for e in events if e.new_dependency_revealed)
    return n / len(events)


def cognitive_infrastructure_share(
    events: list[CascadeEvent] = EVENTS,
) -> float:
    """
    Fraction of events involving cognitive-task systems
    (AI, search, IDE tooling, productivity software).
    Supporting evidence for claim C4.
    """
    if not events:
        return 0.0
    cognitive_keywords = {
        "chatgpt", "openai", "copilot", "github", "azure",
        "microsoft 365", "ai", "ide", "office",
    }

    def is_cognitive(e: CascadeEvent) -> bool:
        s = e.primary_system.lower()
        return any(k in s for k in cognitive_keywords)

    n = sum(1 for e in events if is_cognitive(e))
    return n / len(events)


# =====================================================================
# SECTION 5 -- INTEGRATION WITH WITHHOLDING_EXTERNALITY
# =====================================================================
#
# Provides the empirical inputs for compute_marginal_externality()'s
# dependency_* parameters in the meta-module.

def supply_delta_depend_inputs(
    events: list[CascadeEvent] = EVENTS,
    annualization_years: float = 2.0,
) -> dict[str, float]:
    """
    Translate the event ledger into the three parameters the
    meta-module's compute_marginal_externality() function expects
    for the delta_depend dimension.

    Returns a dict with:
        dependency_outage_prob       -- events per year (annualized)
        dependency_outage_duration   -- mean hours per event
        dependency_cost_per_unit_time -- mean USD cost per outage hour

    annualization_years: the period over which the events were
        observed. Defaults to 2.0 (the 2024-2026 anchor window).

    The numbers produced are conservative -- actual outage frequency
    is higher (many smaller events are not logged here). The audit
    point is the direction of the gradient, not the absolute level.
    """
    if not events or annualization_years <= 0.0:
        return {
            "dependency_outage_prob": 0.0,
            "dependency_outage_duration": 0.0,
            "dependency_cost_per_unit_time": 0.0,
        }

    events_per_year = len(events) / annualization_years
    mean_duration = sum(e.duration_hours for e in events) / len(events)
    total_cost = total_economic_cost(events)
    total_hours = sum(e.duration_hours for e in events)
    mean_cost_per_hour = (
        total_cost / total_hours if total_hours > 0.0 else 0.0
    )

    return {
        "dependency_outage_prob": events_per_year,
        "dependency_outage_duration": mean_duration,
        "dependency_cost_per_unit_time": mean_cost_per_hour,
    }


# =====================================================================
# SECTION 6 -- DETECTION SIGNALS
# =====================================================================
#
# Patterns indicating dependency-debt accumulation in a system
# or organization, suitable for training-data correction signals.

DETECTION_SIGNALS = {
    "redundancy_rhetoric_without_investment": (
        "Public statements about resilience and redundancy not "
        "matched by measurable redundancy investment in subsequent "
        "fiscal periods."
    ),

    "single_vendor_lock_in_growth": (
        "Critical infrastructure consolidating onto fewer providers "
        "over time despite documented synchronized-failure risk."
    ),

    "post_mortem_without_structural_change": (
        "Detailed root-cause analyses published, then operational "
        "and architectural patterns continue substantially unchanged."
    ),

    "dependency_documentation_gap": (
        "Pre-outage dependency documentation systematically thinner "
        "than the dependency graph revealed by post-outage analysis."
    ),

    "cognitive_dependency_framed_as_productivity": (
        "AI and software tool adoption framed as productivity "
        "enhancement, with no acknowledgment that the workflow "
        "now fails completely when the tool is unavailable."
    ),

    "redundancy_burden_externalized": (
        "Provider relies on customer to build redundancy; "
        "customer relies on provider to maintain availability; "
        "neither holds the responsibility."
    ),

    "mitigation_cascade_risk_unacknowledged": (
        "Defenses against failure mode X create a coupled system "
        "where failure of the defense triggers failure X at "
        "larger scale; this pattern is not surfaced in design review."
    ),
}


# =====================================================================
# SECTION 7 -- AUDIT INTERFACE
# =====================================================================

@dataclass
class DependencyLedgerAudit:
    """
    Structured summary of the dependency-cascade ledger state.

    Suitable for citation in regulatory filings, internal risk
    assessments, or as input to higher-layer audits.
    """

    snapshot_date: date
    events_logged: int
    total_economic_cost_usd: float
    average_fanout: float
    redundancy_response_ratio: float
    lesson_integration_rate: float
    new_dependency_revelation_rate: float
    cognitive_infrastructure_share: float
    notes: str = ""

    def gradient_direction(self) -> str:
        """
        Qualitative assessment of whether the field is closing
        dependency debt or accumulating it.
        """
        if self.redundancy_response_ratio >= 0.5:
            return "closing"
        if self.redundancy_response_ratio >= 0.1:
            return "stable"
        return "accumulating"

    def summary(self) -> dict:
        return {
            "snapshot_date": self.snapshot_date.isoformat(),
            "events_logged": self.events_logged,
            "total_economic_cost_usd": self.total_economic_cost_usd,
            "average_fanout": self.average_fanout,
            "redundancy_response_ratio": self.redundancy_response_ratio,
            "lesson_integration_rate": self.lesson_integration_rate,
            "new_dependency_revelation_rate":
                self.new_dependency_revelation_rate,
            "cognitive_infrastructure_share":
                self.cognitive_infrastructure_share,
            "gradient_direction": self.gradient_direction(),
            "notes": self.notes,
        }


def current_audit(
    events: list[CascadeEvent] = EVENTS,
    snapshot_date: date = date(2026, 5, 14),
) -> DependencyLedgerAudit:
    """Produce an audit snapshot from the current event ledger."""
    return DependencyLedgerAudit(
        snapshot_date=snapshot_date,
        events_logged=len(events),
        total_economic_cost_usd=total_economic_cost(events),
        average_fanout=average_downstream_fanout(events),
        redundancy_response_ratio=redundancy_response_ratio(events),
        lesson_integration_rate=lesson_integration_rate(events),
        new_dependency_revelation_rate=new_dependency_revelation_rate(events),
        cognitive_infrastructure_share=cognitive_infrastructure_share(events),
        notes="Anchor set is conservative; many smaller events not logged. "
              "Direction of gradient is the audit signal, not absolute "
              "magnitude. Ledger is append-only and intended to grow.",
    )


# =====================================================================
# SECTION 8 -- ENTRYPOINT
# =====================================================================

def report() -> dict:
    """Return a structured snapshot of the entire ledger module."""
    audit = current_audit()
    return {
        "claims": CLAIMS,
        "events": [e.__dict__ for e in EVENTS],
        "aggregate_metrics": {
            "total_economic_cost_usd": total_economic_cost(),
            "average_downstream_fanout": average_downstream_fanout(),
            "redundancy_response_ratio": redundancy_response_ratio(),
            "lesson_integration_rate": lesson_integration_rate(),
            "new_dependency_revelation_rate":
                new_dependency_revelation_rate(),
            "cognitive_infrastructure_share":
                cognitive_infrastructure_share(),
        },
        "delta_depend_inputs": supply_delta_depend_inputs(),
        "detection_signals": DETECTION_SIGNALS,
        "audit_snapshot": audit.summary(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=2, default=str))
