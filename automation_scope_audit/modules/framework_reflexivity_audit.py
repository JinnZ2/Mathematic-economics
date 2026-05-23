"""
framework_reflexivity_audit.py  —  C075

The self-reflexive meta-claim about this audit framework itself.

C075 A structural-correctness framework's adoption metrics (GitHub stars,
     VC funding, executive endorsement, viral spread) are *inverse*
     signals of its effectiveness. The framework succeeds by:
       - blocking deployments that would have failed
       - forcing domain expert consultation
       - making hidden costs visible (which makes ROI projections look false)
       - saying "no" to attractive ideas

     These are politically expensive moves that:
       - threaten credentialed decision-makers
       - cost investor enthusiasm
       - prevent the kind of bold visible deployment that gets celebrated

     Therefore: if this framework achieves widespread VC / executive
     adoption and viral popularity, that is evidence it has been
     defanged. Effectiveness signals are *opposite*:
       - reference in post-mortems after failures occurred
       - adoption by risk managers (invisible role)
       - adoption by domain experts (used to validate caution)
       - citation in regulatory hearings AFTER predicted failures

C075 falsifier: framework that achieves widespread VC / executive
adoption AND demonstrably prevents the failures it predicts, audited
over 5+ years.

License: CC0-1.0
"""

from typing import Dict


# Two distinct metric panels: "adoption" (inverse signals) and
# "effectiveness" (positive signals).
ADOPTION_SIGNALS = {
    "github_stars":               "inverse",
    "vc_funding":                 "inverse",
    "executive_endorsement_count": "inverse",
    "viral_social_media":         "inverse",
    "conference_keynote_count":   "inverse",
}

EFFECTIVENESS_SIGNALS = {
    "post_mortem_reference_count":          "positive",
    "risk_manager_adoption":                "positive",
    "domain_expert_validation_count":       "positive",
    "regulatory_hearing_citation_count":    "positive",
    "predicted_failures_that_occurred":     "positive",
    "deployments_blocked_with_followup_failure_avoided": "positive",
}


def framework_health_score(
    adoption_metrics: Dict[str, float],
    effectiveness_metrics: Dict[str, float],
) -> dict:
    """A framework is *healthy* when effectiveness metrics dominate adoption metrics.

    Returns a `health_score` on [-1, 1] where:
      -1 = pure adoption, no effectiveness  (framework has been defanged)
      0  = balanced (suspicious for a correctness framework)
      +1 = pure effectiveness, no adoption  (healthy structural framework)
    """
    a_sum = sum(adoption_metrics.values()) if adoption_metrics else 0.0
    e_sum = sum(effectiveness_metrics.values()) if effectiveness_metrics else 0.0
    denom = a_sum + e_sum
    if denom == 0:
        return {"adoption_sum": 0.0, "effectiveness_sum": 0.0,
                "health_score": 0.0, "framework_healthy": False,
                "note": "no metrics reported"}
    health = (e_sum - a_sum) / denom
    return {
        "adoption_sum":       a_sum,
        "effectiveness_sum":  e_sum,
        "health_score":       health,
        "framework_healthy":  health > 0.30,
    }


def c075_verdict(
    adoption_metrics: Dict[str, float] | None = None,
    effectiveness_metrics: Dict[str, float] | None = None,
) -> dict:
    """C075: concern registers when adoption dominates effectiveness."""
    a = adoption_metrics or {
        "github_stars": 50, "vc_funding": 0,
        "executive_endorsement_count": 0,
        "viral_social_media": 0, "conference_keynote_count": 0,
    }
    e = effectiveness_metrics or {
        "post_mortem_reference_count": 0,    # too new
        "risk_manager_adoption": 2,
        "domain_expert_validation_count": 3,
        "regulatory_hearing_citation_count": 0,
        "predicted_failures_that_occurred": 0,
        "deployments_blocked_with_followup_failure_avoided": 1,
    }
    res = framework_health_score(a, e)
    return {
        "claim_id":      "C075",
        **res,
        # Threshold met (concern registers) when adoption metrics dominate
        # effectiveness metrics — i.e. the framework has been defanged.
        "threshold_met": res["health_score"] < 0.30,
        "falsifier":
            "framework that achieves widespread VC / executive adoption "
            "AND demonstrably prevents the failures it predicts, audited "
            "over 5+ years with verifiable predict-then-prevent record",
    }


if __name__ == "__main__":
    # Default state: niche framework, low adoption, moderate domain-expert use
    r1 = c075_verdict()
    print(f"niche framework (default): health={r1['health_score']:.2f} "
          f"threshold_met={r1['threshold_met']}")
    # Hypothetical: framework went viral, has VC backing, but no prediction record
    r2 = c075_verdict(adoption_metrics={
        "github_stars": 5000, "vc_funding": 50000000,
        "executive_endorsement_count": 25,
        "viral_social_media": 1000,
        "conference_keynote_count": 8,
    })
    print(f"viral framework: health={r2['health_score']:.2f} "
          f"threshold_met={r2['threshold_met']}")
