"""
adaptation_debt.py — friction removal as stored fragility liability

Source: Calibration Diagnostic Q5, Independent Animal's Creed I (2026).
License: CC0.
Dependencies: stdlib only.

Core model (falsifiable):
When friction is removed from a system, the adaptation it produced stops
occurring. The absence compounds over time.
debt(t) = Σᵢ initial_load_i × (1 + rᵢ)^tᵢ

where:
    initial_load_i = severity of removed friction event
    rᵢ             = compounding rate (domain-specific)
    tᵢ             = years since removal

This mirrors infrastructure-stability-model's latent-node time constants:
maintenance debt accumulates at a rate the system does not measure until
failure.
Energy-flow:
friction_events
│
▼
┌──────────────────────────────────────┐
│ classify: removed vs preserved       │
│ compute: compounding debt per event  │
│ detect: cliff failure threshold      │
└──────────────────────────────────────┘
│
▼
total_debt → score → years_to_cliff

Input schema:
{
"system_id": str,
"friction_events": [
{
"name": str,
"domain": "institutional"|"physical"|"social"|"cognitive",
"initial_load": float,        # [0.0, 1.0] — severity of friction removed
"removed": bool,
"years_since_removed": float,
"compounding_rate": float,    # optional; defaults by domain
},
...
],
"cliff_threshold": float,         # optional; default 10.0
}
"""

import math
from typing import Any
from schema import DimensionScore, CalibrationReport, Band

# Default compounding rates by domain

# Calibrated against observed time-to-failure in analogous systems

DEFAULT_COMPOUNDING_RATE = {
"institutional": 0.08,   # ~9 year doubling (aligns with infra-stability)
"physical": 0.04,        # ~17 year doubling (slow wear accumulation)
"social": 0.12,          # ~6 year doubling (trust/skill networks)
"cognitive": 0.15,       # ~5 year doubling (individual skill atrophy)
}

def compute_event_debt(event: dict[str, Any]) -> float:
    """
    Single event debt = initial_load × (1 + r)^t
    If not removed, returns 0 (preserved friction = no debt).
    """
    if not event.get("removed", False):
        return 0.0

    load = event.get("initial_load", 0.5)
    t = event.get("years_since_removed", 0.0)
    domain = event.get("domain", "institutional")
    r = event.get("compounding_rate", DEFAULT_COMPOUNDING_RATE.get(domain, 0.08))

    return load * ((1.0 + r) ** t)
def score_total_debt(friction_events: list[dict[str, Any]],
cliff: float = 10.0) -> DimensionScore:
    """
    Total debt normalized against cliff threshold.
    Cliff = point where debt exceeds system's remaining adaptive capacity.
    """
    if not friction_events:
        return DimensionScore(
name="total_adaptation_debt",
score=0.5,
band=Band.YELLOW,
evidence=["no friction events recorded"],
falsifier="provide ≥5 friction events with removal status",
)
    debts = [(e.get("name", "unnamed"), compute_event_debt(e))
         for e in friction_events]
    total_debt = sum(d for _, d in debts)
    score = min(total_debt / cliff, 1.0)

    top_debts = sorted(debts, key=lambda x: -x[1])[:3]

    return DimensionScore(
    name="total_adaptation_debt",
    score=score,
    band=Band.from_score(score),
    evidence=[
        f"total compounded debt: {total_debt:.3f}",
        f"cliff threshold: {cliff:.2f}",
        f"debt/cliff ratio: {score:.1%}",
        f"top 3 debt sources: {', '.join(f'{n}={d:.2f}' for n, d in top_debts)}",
    ],
    falsifier=(
        f"if total_debt drops below {cliff * 0.3:.2f} via friction "
        "restoration or system reset, dimension flips to GREEN"
    ),
)
def score_friction_preservation(friction_events: list[dict[str, Any]]
) -> DimensionScore:
    """
    Fraction of friction events still preserved.
    Preserved friction = active calibration.
    """
    if not friction_events:
        return DimensionScore(
name="friction_preservation",
score=0.5,
band=Band.YELLOW,
evidence=["no friction data"],
falsifier="log friction events",
)
    preserved = sum(1 for e in friction_events if not e.get("removed", False))
    total = len(friction_events)
    preservation_ratio = preserved / total
    # Invert: low preservation = high domestication score
    score = 1.0 - preservation_ratio

    return DimensionScore(
    name="friction_preservation",
    score=score,
    band=Band.from_score(score),
    evidence=[
        f"friction events: {total}",
        f"preserved (still calibrating): {preserved}",
        f"removed (debt accumulating): {total - preserved}",
        f"preservation ratio: {preservation_ratio:.1%}",
    ],
    falsifier=(
        "if preservation ratio exceeds 70%, the system is retaining "
        "instructional pain; dimension flips to GREEN"
    ),
)
def score_cliff_proximity(friction_events: list[dict[str, Any]],
cliff: float = 10.0) -> DimensionScore:
    """
    Years-to-cliff estimate. Projects current debt trajectory forward.
    If current debt D, growth rate r_avg, cliff C:
    years_to_cliff = log(C / D) / log(1 + r_avg)

    Score = 1 - (years_to_cliff / 30)   [30y = effectively safe horizon]
    """
    removed = [e for e in friction_events if e.get("removed", False)]
    if not removed:
        return DimensionScore(
            name="cliff_proximity",
            score=0.0,
            band=Band.GREEN,
            evidence=["no removed friction -- no debt trajectory"],
            falsifier="n/a",
        )

    current_debt = sum(compute_event_debt(e) for e in removed)
    rates = [
        e.get("compounding_rate",
              DEFAULT_COMPOUNDING_RATE.get(e.get("domain", "institutional"),
                                           0.08))
        for e in removed
    ]
    r_avg = sum(rates) / len(rates)

    if current_debt >= cliff:
        years_to_cliff = 0.0
        score = 1.0
    elif current_debt <= 0 or r_avg <= 0:
        years_to_cliff = 999.0
        score = 0.0
    else:
        years_to_cliff = math.log(cliff / current_debt) / math.log(1.0 + r_avg)
        score = max(0.0, 1.0 - min(years_to_cliff / 30.0, 1.0))

    return DimensionScore(
        name="cliff_proximity",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"current debt: {current_debt:.3f}",
            f"average compounding rate: {r_avg:.3f}/yr",
            f"projected years to cliff: {years_to_cliff:.1f}",
        ],
        falsifier=(
            "if years_to_cliff extends beyond 30 (via friction restoration "
            "or rate reduction), dimension flips to GREEN"
        ),
    )
def run_adaptation_debt_audit(input_data: dict[str, Any]) -> CalibrationReport:
    """
    Energy-flow:
    friction_events → 3 dimension scorers → aggregate → cliff estimate
    """
    events = input_data.get("friction_events", [])
    cliff = input_data.get("cliff_threshold", 10.0)
    dims = [
    score_total_debt(events, cliff),
    score_friction_preservation(events),
    score_cliff_proximity(events, cliff),
]

    scores = [d.score for d in dims]
    agg_score, agg_band = CalibrationReport.aggregate(scores)
    failing = [d.name for d in dims if d.band in (Band.RED, Band.EXTINCT)]

    verdict_map = {
    Band.GREEN: (
        "Adaptation debt is LOW. System retains most friction; "
        "calibration is active."
    ),
    Band.YELLOW: (
        "Adaptation debt is ACCUMULATING. Monitor compounding trajectory."
    ),
    Band.RED: (
        "Adaptation debt is HIGH. System has removed too much friction; "
        "fragility compounding faster than adaptation can recover."
    ),
    Band.EXTINCT: (
        "Adaptation debt has CROSSED the cliff. The system is now operating "
        "entirely on cached comfort with no remaining calibration capacity. "
        "Next stressor exceeds response threshold."
    ),
}

    # Extract cliff-proximity metadata for the report
    cliff_dim = dims[2]
    ytc_evidence = next((e for e in cliff_dim.evidence
                     if "years to cliff" in e), "")

    return CalibrationReport(
    module="adaptation_debt",
    system_id=input_data.get("system_id", "unnamed_system"),
    dimensions=dims,
    aggregate_score=agg_score,
    aggregate_band=agg_band,
    verdict=verdict_map[agg_band],
    failing_dimensions=failing,
    falsifiable_claims=[d.falsifier for d in dims if d.falsifier],
    metadata={
        "source": "Calibration Diagnostic Q5 + Creed I (2026)",
        "license": "CC0",
        "cliff_threshold": cliff,
        "cliff_estimate": ytc_evidence,
    },
)
if __name__ == "__main__":
                         test_input = {
                         "system_id": "test_institution",
                         "cliff_threshold": 10.0,
                         "friction_events": [
                         {"name": "failure_review", "domain": "institutional",
                         "initial_load": 0.7, "removed": True,
                         "years_since_removed": 8.0},
                         {"name": "peer_calibration", "domain": "social",
                         "initial_load": 0.8, "removed": True,
                         "years_since_removed": 5.0},
                         {"name": "manual_override", "domain": "cognitive",
                         "initial_load": 0.6, "removed": True,
                         "years_since_removed": 10.0},
                         {"name": "physical_maintenance", "domain": "physical",
                         "initial_load": 0.5, "removed": False,
                         "years_since_removed": 0.0},
                         ],
                         }
                         report = run_adaptation_debt_audit(test_input)
                         print(report.to_json())
