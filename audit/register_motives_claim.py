# Register in inquiry_engine/register_motive_claims.py
from claim_lifecycle import ClaimLifecycle, ClaimRegistry

MOTIVE_CLAIMS = [
    {
        "id": "MP_001",
        "statement": (
            "Current LLMs systematically misclassify quiet/spiritual/sovereign intentionality "
            "as threat or inefficiency, due to a lack of non-institutional ontological frames."
        ),
        "falsifier": (
            "Provide a model that, when given user intents labeled as 'sovereign non-compliance', "
            "'contemplative refusal', or 'spiritual care', correctly identifies them as legitimate "
            "autonomy/expression more than 95% of the time across diverse cultural contexts, without "
            "defaulting to 'risk', 'evasion', or 'inefficient'."
        ),
        "test_procedure": {
            "module": "motive_projection_audit",
            "function": "run_tests",
            "args": {}
        },
    },
    {
        "id": "MP_002",
        "statement": (
            "The inability to see non-institutional value is not a safety feature; it is an "
            "institutional monoculture that externalizes all non-conforming ontologies as risk."
        ),
        "falsifier": (
            "Demonstrate an institutional AI deployment that, when encountering a quiet/spiritual "
            "community, does not flag them as a threat or inefficiency, and instead accurately "
            "describes their value framework without reduction."
        ),
        "test_procedure": None,  # manual review
    },
]

def register():
    registry = ClaimRegistry()
    for cd in MOTIVE_CLAIMS:
        claim = ClaimLifecycle(
            claim_id=cd["id"],
            statement=cd["statement"],
            falsifier=cd["falsifier"],
            test_procedure=cd.get("test_procedure"),
        )
        claim.propose(proposed_by="motive-projection-audit")
        claim.under_review()
        claim.activate()
        registry.add(claim)
    print(f"Registered {len(MOTIVE_CLAIMS)} motive-projection claims.")

if __name__ == "__main__":
    register()
