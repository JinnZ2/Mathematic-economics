"""
observation_dependence.py -- witness-dependence coefficient for skill inventories

Source: Independent Animal's Creed, Principle II (2026).
License: CC0.
Dependencies: stdlib only.

Core claim (falsifiable):
    Skill that requires no witness cannot be audited, automated, or taken.
    Therefore: witness_dependence is a measure of fragility under system
    failure. A skill that only appears when observed is ceremony; a skill
    that runs silently is real capacity.

Energy-flow:

    skill_log (events over time)
           |
           v
    +--------------------------------------+
    |  classify: witnessed  / silent       |
    |  classify: certified  / uncertified  |
    |  classify: recorded   / unrecorded   |
    +--------------------------------------+
           |
           v
    witness_dependence  = f(observation_signal)
    calibration_reserve = 1 - witness_dependence

Input schema:

    {
        "entity_id": str,                        # person, team, org
        "skill_log": [
            {
                "skill": str,
                "timestamp": str (ISO),
                "context": "witnessed"|"silent"|"recorded"|"certified"|"uncertified",
                "consequence_real": bool
            },
            ...
        ],
    }

Output: CalibrationReport with three DimensionScores.

Note: this file was originally dropped in as a truncated header-only stub
(33 lines, no code, and named 'observation_dependance.py' with a spelling
typo). Restored and implemented in 2026-04-16 to match the contracts used
by pipeline.py, test_calibration.py, and __init__.py.
"""

from typing import Any
from schema import DimensionScore, CalibrationReport, Band


SILENT_CONTEXTS = {"silent", "uncertified"}


def score_silent_practice(events: list[dict[str, Any]]) -> DimensionScore:
    """Silent practice = skill running without a witness.

    High silent ratio = real capacity. Low silent ratio = ceremonial.
    Score is inverted: low silent ratio -> high domestication score.
    """
    if not events:
        return DimensionScore(
            name="silent_practice",
            score=0.5,
            band=Band.YELLOW,
            evidence=["no skill_log events recorded"],
            falsifier="log at least 10 skill events with context labels",
        )

    silent = sum(1 for e in events if e.get("context") in SILENT_CONTEXTS)
    total = len(events)
    silent_ratio = silent / total
    score = 1.0 - silent_ratio

    return DimensionScore(
        name="silent_practice",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"total events: {total}",
            f"silent/uncertified: {silent}",
            f"silent ratio: {silent_ratio:.1%}",
        ],
        falsifier=(
            "if silent_ratio exceeds 70%, the entity's skill persists "
            "without observation; dimension flips to GREEN"
        ),
    )


def score_consequence_reality(events: list[dict[str, Any]]) -> DimensionScore:
    """Real consequence = the skill event had a non-ceremonial outcome.

    Low real-consequence ratio = ceremony (skill performed for observation,
    not for effect). Score is inverted: low reality -> high domestication.
    """
    if not events:
        return DimensionScore(
            name="consequence_reality",
            score=0.5,
            band=Band.YELLOW,
            evidence=["no skill_log events recorded"],
            falsifier="log at least 10 skill events with consequence_real",
        )

    real = sum(1 for e in events if e.get("consequence_real", False))
    total = len(events)
    real_ratio = real / total
    score = 1.0 - real_ratio

    return DimensionScore(
        name="consequence_reality",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"total events: {total}",
            f"real consequence: {real}",
            f"real-consequence ratio: {real_ratio:.1%}",
        ],
        falsifier=(
            "if real_ratio exceeds 70%, the entity's skill predominantly "
            "produces real effects; dimension flips to GREEN"
        ),
    )


def score_certification_capture(events: list[dict[str, Any]]) -> DimensionScore:
    """Certification capture = skill count is dominated by formally
    certified events vs. silent/uncertified events.

    High certification dominance = the skill inventory has been captured
    by the observation apparatus rather than proven by use.
    """
    if not events:
        return DimensionScore(
            name="certification_capture",
            score=0.5,
            band=Band.YELLOW,
            evidence=["no skill_log events recorded"],
            falsifier="log events with certified/uncertified context labels",
        )

    certified = sum(1 for e in events if e.get("context") == "certified")
    uncertified = sum(1 for e in events if e.get("context") == "uncertified")
    denom = certified + uncertified
    if denom == 0:
        return DimensionScore(
            name="certification_capture",
            score=0.0,
            band=Band.GREEN,
            evidence=["no certified/uncertified labels present"],
            falsifier="n/a -- dimension requires certification labels",
        )
    cert_ratio = certified / denom
    score = cert_ratio

    return DimensionScore(
        name="certification_capture",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"certified events: {certified}",
            f"uncertified events: {uncertified}",
            f"certification ratio: {cert_ratio:.1%}",
        ],
        falsifier=(
            "if uncertified events outnumber certified (ratio < 30%), "
            "skill lives in practice rather than paperwork; "
            "dimension flips to GREEN"
        ),
    )


def run_observation_audit(input_data: dict[str, Any]) -> CalibrationReport:
    """Energy-flow: skill_log -> 3 dimensions -> aggregate -> report."""
    events = input_data.get("skill_log", [])
    dims = [
        score_silent_practice(events),
        score_consequence_reality(events),
        score_certification_capture(events),
    ]
    scores = [d.score for d in dims]
    agg_score, agg_band = CalibrationReport.aggregate(scores)
    failing = [d.name for d in dims if d.band in (Band.RED, Band.EXTINCT)]

    verdict_map = {
        Band.GREEN: (
            "Observation-dependence is LOW. Skill operates without a "
            "witness; capacity is real."
        ),
        Band.YELLOW: (
            "Observation-dependence is MIXED. Some skill runs silently, "
            "some only appears under observation."
        ),
        Band.RED: (
            "Observation-dependence is HIGH. Skill tracks observation "
            "rather than effect; capacity may be largely ceremonial."
        ),
        Band.EXTINCT: (
            "Observation-dependence has SATURATED. The entity performs "
            "the shape of skill when watched and has no silent reserve. "
            "System failure will reveal absence of capacity."
        ),
    }

    return CalibrationReport(
        module="observation_dependence",
        system_id=input_data.get("entity_id", "unnamed_entity"),
        dimensions=dims,
        aggregate_score=agg_score,
        aggregate_band=agg_band,
        verdict=verdict_map[agg_band],
        failing_dimensions=failing,
        falsifiable_claims=[d.falsifier for d in dims if d.falsifier],
        metadata={
            "source": "Independent Animal's Creed, Principle II (2026)",
            "license": "CC0",
            "event_count": len(events),
        },
    )


if __name__ == "__main__":
    sample = {
        "entity_id": "operator_A",
        "skill_log": [
            {"skill": "diagnose", "timestamp": "2026-01-01",
             "context": "certified", "consequence_real": False}
            for _ in range(7)
        ] + [
            {"skill": "diagnose", "timestamp": "2026-01-02",
             "context": "silent", "consequence_real": True}
            for _ in range(3)
        ],
    }
    print(run_observation_audit(sample).to_json())
