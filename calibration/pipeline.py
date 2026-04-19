"""
pipeline.py -- unified calibration audit pipeline

Energy-flow:

    system_description
           |
           +--------------+--------------+
           v              v              v
     calibration_    observation_   adaptation_
       audit         dependence        debt
           |              |              |
           +--------------+--------------+
                          |
                          v
               UnifiedCalibrationReport
                          |
                          v
               JSON output (feeds downstream:
               substrate_audit, first_principles_audit)

License: CC0.
"""

import json
from typing import Any
from schema import CalibrationReport, Band, EMBEDDED_PROMPT
from calibration_audit import run_calibration_audit
from observation_dependence import run_observation_audit
from adaptation_debt import run_adaptation_debt_audit


def run_unified_audit(system_desc: dict[str, Any]) -> dict[str, Any]:
    """
    Run all three audits and produce unified report.

    Input may contain any combination of:
        - feedback_events, decisions, skills_observed,
          memorialized_skills, friction_events  (calibration_audit)
        - skill_log                             (observation_dependence)
        - friction_events                       (adaptation_debt)
    """
    reports = {}

    # Module 1: full diagnostic
    reports["calibration"] = run_calibration_audit(system_desc)

    # Module 2: observation dependence (needs skill_log)
    if "skill_log" in system_desc:
        obs_input = {
            "entity_id": system_desc.get("system_id", "unnamed"),
            "skill_log": system_desc["skill_log"],
        }
        reports["observation"] = run_observation_audit(obs_input)

    # Module 3: adaptation debt (needs friction_events with debt schema)
    if "friction_events" in system_desc:
        debt_events = []
        for e in system_desc["friction_events"]:
            if "initial_load" in e:
                debt_events.append(e)
            else:
                # Auto-translate from basic schema
                debt_events.append({
                    "name": e.get("type", "unnamed"),
                    "domain": e.get("domain", "institutional"),
                    "initial_load": e.get("initial_load", 0.5),
                    "removed": e.get("was_removed", e.get("removed", False)),
                    "years_since_removed": e.get(
                        "years_since_removal",
                        e.get("years_since_removed", 0.0)
                    ),
                })
        debt_input = {
            "system_id": system_desc.get("system_id", "unnamed"),
            "friction_events": debt_events,
            "cliff_threshold": system_desc.get("cliff_threshold", 10.0),
        }
        reports["adaptation_debt"] = run_adaptation_debt_audit(debt_input)

    # Aggregate across modules
    module_scores = [r.aggregate_score for r in reports.values()]
    agg_score = (sum(module_scores) / len(module_scores)) if module_scores else 0.0
    agg_band = Band.from_score(agg_score)

    unified = {
        "system_id": system_desc.get("system_id", "unnamed_system"),
        "unified_score": round(agg_score, 4),
        "unified_band": agg_band.value,
        "module_reports": {
            name: json.loads(r.to_json()) for name, r in reports.items()
        },
        "all_failing_dimensions": [
            f"{mod}.{dim}"
            for mod, r in reports.items()
            for dim in r.failing_dimensions
        ],
        "all_falsifiable_claims": [
            claim
            for r in reports.values()
            for claim in r.falsifiable_claims
        ],
        "embedded_prompt": EMBEDDED_PROMPT.strip(),
        "metadata": {
            "modules_run": list(reports.keys()),
            "license": "CC0",
            "schema_version": "1.0",
        },
    }
    return unified


if __name__ == "__main__":
    test_system = {
        "system_id": "composite_test_org",
        "cliff_threshold": 10.0,
        "feedback_events": [
            {"type": "personal", "count": 12},
            {"type": "impersonal", "count": 4},
        ],
        "decisions": [
            {"decision_maker": "mgmt", "consequence_hops": 3},
            {"decision_maker": "mgmt", "consequence_hops": 4},
            {"decision_maker": "mgmt", "consequence_hops": 2},
        ],
        "skills_observed": [
            {"skill": "slide_prep", "requires_witness": True},
            {"skill": "compliance", "requires_witness": True},
            {"skill": "field_repair", "requires_witness": False},
        ],
        "memorialized_skills": [
            {"skill": "decision_making", "praise_volume": 700,
             "estimated_prevalence": 0.15},
        ],
        "friction_events": [
            {"name": "postmortems", "domain": "institutional",
             "initial_load": 0.7, "removed": True,
             "years_since_removed": 6.0},
            {"name": "peer_review", "domain": "social",
             "initial_load": 0.6, "removed": True,
             "years_since_removed": 4.0},
            {"name": "maintenance", "domain": "physical",
             "initial_load": 0.5, "removed": False,
             "years_since_removed": 0.0},
        ],
        "skill_log": [
            {"skill": "presentation", "timestamp": "2026-01",
             "context": "witnessed", "consequence_real": False},
            {"skill": "presentation", "timestamp": "2026-02",
             "context": "recorded", "consequence_real": False},
            {"skill": "field_repair", "timestamp": "2026-01",
             "context": "silent", "consequence_real": True},
            {"skill": "field_repair", "timestamp": "2026-02",
             "context": "silent", "consequence_real": True},
        ],
    }
    result = run_unified_audit(test_system)
    print(json.dumps(result, indent=2))
