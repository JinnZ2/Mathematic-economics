"""
calibration_audit.py -- 5-dimension diagnostic for environment fragility

Source: Calibration Diagnostic (2026).
License: CC0.
Dependencies: stdlib only (math is imported at the top).

The five dimensions correspond to Q1-Q5 of the diagnostic:

    Q1: bite_source           -- is feedback personal (mauling)
                                 or impersonal (calibrating)?
    Q2: skin_in_game          -- do decision-makers feel their decisions
                                 directly (0 hops) or through layers?
    Q3: witness_dependence    -- does skill only appear when observed?
    Q4: memorialization       -- praise_volume * (1 - prevalence) signals
                                 an extinct-in-the-wild capacity.
    Q5: friction_removal      -- friction smoothed away accumulates as
                                 adaptation debt.

Each scorer returns a DimensionScore. `run_calibration_audit` composes
them and emits a CalibrationReport.
"""

import math
from typing import Any
from schema import DimensionScore, CalibrationReport, Band


# --- Q1: BITE SOURCE ---------------------------------------------------------

def score_bite_source(feedback_events: list[dict[str, Any]]) -> DimensionScore:
    """
    Calibrating bite: impersonal, instructive (the old dog's snarl).
    Mauling bite:     personal, status-driven (the whisper that wounds).
    Score = personal / (personal + impersonal).
    High score -> feedback is about status, not physics. DOMESTICATED.
    """
    if not feedback_events:
        return DimensionScore(
            name="bite_source",
            score=0.5,
            band=Band.YELLOW,
            evidence=["no feedback events recorded -- cannot calibrate"],
            falsifier="provide >=10 tagged feedback events to re-score",
        )

    personal = sum(e["count"] for e in feedback_events if e["type"] == "personal")
    impersonal = sum(e["count"] for e in feedback_events if e["type"] == "impersonal")
    total = personal + impersonal
    score = personal / total if total else 0.5

    return DimensionScore(
        name="bite_source",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"personal feedback events: {personal}",
            f"impersonal feedback events: {impersonal}",
            f"ratio: {score:.2%} personal",
        ],
        falsifier=(
            "if impersonal/instructive feedback rises above 70% of total, "
            "this dimension flips to GREEN"
        ),
    )


# --- Q2: SKIN IN THE GAME ----------------------------------------------------

def score_skin_in_game(decisions: list[dict[str, Any]]) -> DimensionScore:
    """
    consequence_hops = number of downstream entities between decision and
    felt impact.
        0 hops = decision-maker feels it directly.
        3+ hops = consequence has been sheltered.
    Score normalized via: min(mean_hops / 4.0, 1.0)
    """
    if not decisions:
        return DimensionScore(
            name="skin_in_game",
            score=0.5,
            band=Band.YELLOW,
            evidence=["no decisions recorded"],
            falsifier="provide >=5 decisions with consequence_hops to re-score",
        )

    hops = [d["consequence_hops"] for d in decisions]
    mean_hops = sum(hops) / len(hops)
    score = min(mean_hops / 4.0, 1.0)
    direct = sum(1 for h in hops if h == 0)
    sheltered = sum(1 for h in hops if h >= 3)

    return DimensionScore(
        name="skin_in_game",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"decisions audited: {len(decisions)}",
            f"mean consequence distance: {mean_hops:.2f} hops",
            f"direct-consequence decisions: {direct}",
            f"sheltered decisions (>=3 hops): {sheltered}",
        ],
        falsifier=(
            "if mean consequence_hops drops below 1.2, decision-makers are "
            "feeling the physics; dimension flips to GREEN"
        ),
    )


# --- Q3: OBSERVED VS PRACTICED -----------------------------------------------

def score_witness_dependence(skills: list[dict[str, Any]]) -> DimensionScore:
    """
    Actual skill requires nothing -- practiced constantly without observation.
    Propaganda of skill requires audience -- practiced for recording.
    Score = fraction of skills that require witness to be practiced.
    """
    if not skills:
        return DimensionScore(
            name="witness_dependence",
            score=0.5,
            band=Band.YELLOW,
            evidence=["no skills inventoried"],
            falsifier="inventory >=5 skills with requires_witness flag",
        )

    witness_dependent = sum(1 for s in skills if s.get("requires_witness"))
    total = len(skills)
    score = witness_dependent / total

    return DimensionScore(
        name="witness_dependence",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"skills inventoried: {total}",
            f"skills requiring witness: {witness_dependent}",
            f"silent-skill ratio: {(1.0 - score):.1%}",
        ],
        falsifier=(
            "if more than 70% of skills are practiced silently "
            "(requires_witness=False), dimension flips to GREEN"
        ),
    )


# --- Q4: MEMORIALIZATION -----------------------------------------------------

def score_memorialization(memorialized: list[dict[str, Any]]) -> DimensionScore:
    """
    Principle: memorialization volume is INVERSELY proportional to prevalence.
    If a basic competence is being written about extensively, it is extinct
    in the wild.
        Signal per skill: praise_volume * (1 - prevalence)
    Normalized across inventoried skills.
    """
    if not memorialized:
        return DimensionScore(
            name="memorialization_extinction",
            score=0.0,
            band=Band.GREEN,
            evidence=["no memorialized skills flagged -- no extinction signal"],
            falsifier=(
                "if a basic competence appears with high praise_volume AND "
                "low estimated_prevalence, this dimension rises"
            ),
        )

    signals = []
    for m in memorialized:
        pv = m["praise_volume"]
        prev = m["estimated_prevalence"]     # [0, 1]
        # Normalize praise_volume to [0, 1] assuming log scale, cap at 1000
        pv_norm = min(pv / 1000.0, 1.0)
        signal = pv_norm * (1.0 - prev)
        signals.append((m["skill"], signal))

    score = sum(s for _, s in signals) / len(signals)
    extinct_flags = [skill for skill, sig in signals if sig > 0.6]

    return DimensionScore(
        name="memorialization_extinction",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"skills analyzed: {len(memorialized)}",
            f"functionally extinct (high praise, low prevalence): "
            f"{len(extinct_flags)}",
            f"extinct skills: {', '.join(extinct_flags) if extinct_flags else 'none'}",
        ],
        falsifier=(
            "if a skill shows high praise_volume (>500) but ALSO high "
            "prevalence (>0.6), the extinction signal is false for that skill"
        ),
    )


# --- Q5: FRICTION / ADAPTATION DEBT ------------------------------------------

def _is_removed(e: dict[str, Any]) -> bool:
    """Accept either `was_removed` or `removed` for schema compatibility."""
    return e.get("was_removed", e.get("removed", False))


def score_friction_removal(friction_events: list[dict[str, Any]]
                           ) -> DimensionScore:
    """
    Removed friction = stored adaptation debt.
    Longer since removal = more debt compounded.
        debt = sum over removed events of log(1 + years_since_removal)
               normalized by event count.
    """
    if not friction_events:
        return DimensionScore(
            name="adaptation_debt",
            score=0.5,
            band=Band.YELLOW,
            evidence=["no friction events recorded"],
            falsifier="provide >=5 friction events with removal status",
        )

    removed = [e for e in friction_events if _is_removed(e)]
    preserved = [e for e in friction_events if not _is_removed(e)]

    debt_signal = sum(
        math.log1p(e.get("years_since_removal",
                         e.get("years_since_removed", 0.0)))
        for e in removed
    )
    max_possible = len(friction_events) * math.log1p(20.0)  # cap at 20y
    score = min(debt_signal / max_possible, 1.0) if max_possible else 0.0

    return DimensionScore(
        name="adaptation_debt",
        score=score,
        band=Band.from_score(score),
        evidence=[
            f"friction events: {len(friction_events)}",
            f"removed (debt accumulating): {len(removed)}",
            f"preserved (calibration intact): {len(preserved)}",
            f"debt signal: {debt_signal:.2f}",
        ],
        falsifier=(
            "if >60% of friction events are preserved (not smoothed away), "
            "the system retains instructional pain; dimension flips to GREEN"
        ),
    )


# --- MAIN AUDIT --------------------------------------------------------------

def run_calibration_audit(system_desc: dict[str, Any]) -> CalibrationReport:
    """
    Energy-flow:
        system_desc -> 5 dimension scorers -> aggregate -> verdict
    """
    dims = [
        score_bite_source(system_desc.get("feedback_events", [])),
        score_skin_in_game(system_desc.get("decisions", [])),
        score_witness_dependence(system_desc.get("skills_observed", [])),
        score_memorialization(system_desc.get("memorialized_skills", [])),
        score_friction_removal(system_desc.get("friction_events", [])),
    ]
    scores = [d.score for d in dims]
    agg_score, agg_band = CalibrationReport.aggregate(scores)
    failing = [d.name for d in dims if d.band in (Band.RED, Band.EXTINCT)]

    verdict_map = {
        Band.GREEN:  "System is CALIBRATING. Feedback loops intact.",
        Band.YELLOW: "System is DRIFTING. Monitor failing dimensions.",
        Band.RED:    "System is MAULING. Fragility accumulating without correction.",
        Band.EXTINCT: (
            "System has crossed into MEMORIALIZATION-ONLY state. "
            "Actual skill is near-extinct; what remains is propaganda of skill."
        ),
    }

    return CalibrationReport(
        module="calibration_audit",
        system_id=system_desc.get("system_id", "unnamed_system"),
        dimensions=dims,
        aggregate_score=agg_score,
        aggregate_band=agg_band,
        verdict=verdict_map[agg_band],
        failing_dimensions=failing,
        falsifiable_claims=[d.falsifier for d in dims if d.falsifier],
        metadata={
            "source": "Calibration Diagnostic (2026)",
            "license": "CC0",
            "dimensions_count": len(dims),
        },
    )


if __name__ == "__main__":
    test_system = {
        "system_id": "test_org",
        "feedback_events": [
            {"type": "personal", "count": 15},
            {"type": "impersonal", "count": 3},
        ],
        "decisions": [
            {"decision_maker": "exec_a", "consequence_hops": 4},
            {"decision_maker": "exec_b", "consequence_hops": 3},
            {"decision_maker": "exec_c", "consequence_hops": 5},
        ],
        "skills_observed": [
            {"skill": "presentation",    "requires_witness": True},
            {"skill": "compliance_docs", "requires_witness": True},
            {"skill": "fire_building",   "requires_witness": False},
        ],
        "memorialized_skills": [
            {"skill": "active_listening", "praise_volume": 800,
             "estimated_prevalence": 0.1},
            {"skill": "decision_making",  "praise_volume": 600,
             "estimated_prevalence": 0.2},
        ],
        "friction_events": [
            {"type": "hard_deadline",       "was_removed": True,
             "years_since_removal": 5.0},
            {"type": "peer_review",         "was_removed": True,
             "years_since_removal": 3.0},
            {"type": "performance_review",  "was_removed": False,
             "years_since_removal": 0.0},
        ],
    }
    print(run_calibration_audit(test_system).to_json())
