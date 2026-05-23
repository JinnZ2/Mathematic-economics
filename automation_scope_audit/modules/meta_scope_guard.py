"""
meta_scope_guard.py  —  C000

C000: All scaling / efficiency / automation claims must specify scope
or are unfalsifiable.

A claim like "scaling is more efficient" is REJECTED without explicit
answers to:

    1. TO WHOM           — per-vehicle? per-ton-mile? per-joule? per-profit?
    2. CONDITIONS        — stable supply? no regulatory change? no scarcity?
    3. TIME PERIOD       — 5 years? 20 years? until resource depletion?
    4. RESOURCE          — energy? capital? labor? rare earth? water?
                            regulatory bandwidth?
    5. EXTERNALIZATION   — infrastructure privatization? human atrophy?
                            institutional brittleness? cascade risk?
    6. BENEFICIARY       — shareholders? customers? society? future generations?
    7. FALSIFIER         — what evidence would prove the claim wrong?

Without explicit answers, the claim is unfalsifiable and therefore not
admissible in any physics-grounded analysis. C000 is a *meta-claim*: a
gate that every other claim a research input, marketing pitch, or
policy assertion has to pass through before structural analysis begins.

Falsifier: a primary-source claim that explicitly answers all seven
scope questions AND publishes a measurable falsifier.

License: CC0-1.0
"""

import re
from typing import Dict, List


SCOPE_DIMENSIONS = [
    "beneficiary",
    "conditions",
    "time_period",
    "resource",
    "externalization",
    "profit_distribution",
    "falsifier",
]


# Patterns that signal each scope dimension is at least *touched* in the
# claim text. The patterns are deliberately permissive — we want to
# detect any acknowledgment, not require canonical phrasing.
SCOPE_PATTERNS: Dict[str, List[str]] = {
    "beneficiary": [
        r"\bper[-\s]vehicle\b", r"\bper[-\s]ton[-\s]mile\b",
        r"\bper[-\s]joule\b", r"\bper[-\s]profit\b",
        r"\bper[-\s]capita\b", r"\befficient\s+to\b",
        r"\bfor\s+(?:operators|customers|drivers|shareholders|society)\b",
    ],
    "conditions": [
        r"\bunder\s+(?:stable|nominal|baseline|the following)\s+conditions\b",
        r"\bassuming\s+", r"\bgiven\s+that\b",
        r"\bconditions?\s*[:=]\b",
        r"\bin\s+the\s+absence\s+of\b",
        r"\b(?:no|without)\s+(?:regulatory\s+change|supply\s+chain|cascade|scarcity)\b",
    ],
    "time_period": [
        r"\b\d+\s*[-\s]?(?:year|yr|month|day|decade)s?\b",
        r"\bover\s+\d", r"\blife(?:time|span)\b",
        r"\bdepreciation\s+period\b", r"\bhorizon\b",
        r"\buntil\s+(?:resource|fuel|reserves)\b",
    ],
    "resource": [
        r"\benergy\b", r"\bcapital\b", r"\blabor\b", r"\bwater\b",
        r"\brare[-\s]earth\b", r"\brare\s+earths?\b",
        r"\bregulatory\s+bandwidth\b", r"\bcompute\b",
        r"\bbandwidth\b", r"\bfuel\b",
    ],
    "externalization": [
        r"\bexternaliz(?:e|ed|ation)\b", r"\boffload(?:ed)?\b",
        r"\b(?:infrastructure|human|institutional)\s+(?:cost|atrophy|brittleness|sprawl)\b",
        r"\bcascade\s+risk\b", r"\boff[-\s]book\b",
        r"\bunpriced\b",
    ],
    "profit_distribution": [
        r"\b(?:profits?|gains?|surplus)\s+(?:accrue|flow|go|distributed)\b",
        r"\bshareholders?\b", r"\bcustomers?\b",
        r"\bworkers?\b", r"\bcommunit(?:y|ies)\b",
        r"\bfuture\s+generations?\b",
    ],
    "falsifier": [
        r"\bfalsif", r"\bdisproven?\b", r"\brefut(?:e|ed)\b",
        r"\b(?:would\s+be|considered)\s+wrong\s+if\b",
        r"\bevidence\s+against\b",
    ],
}


def validate_scope_specification(claim_text: str) -> dict:
    """Check `claim_text` against the seven scope dimensions.

    Returns a per-dimension boolean (present / absent), the list of
    missing dimensions, and an `admissible` flag that requires *all*
    dimensions to be touched (the bar is "claim is structured for
    falsifiability", not "claim is correct").
    """
    text = claim_text.lower()
    present: Dict[str, bool] = {}
    matches: Dict[str, List[str]] = {}
    for dim in SCOPE_DIMENSIONS:
        hits = []
        for p in SCOPE_PATTERNS.get(dim, []):
            for m in re.finditer(p, text, flags=re.IGNORECASE):
                hits.append(m.group(0))
        present[dim] = bool(hits)
        matches[dim] = hits
    missing = [d for d in SCOPE_DIMENSIONS if not present[d]]
    return {
        "claim_text":           claim_text,
        "present":              present,
        "matches":              matches,
        "missing":              missing,
        "admissible":           not missing,
    }


def c000_verdict(claim_text: str) -> dict:
    """Meta-claim verdict.

    `threshold_met` for C000 is True when the claim is *inadmissible* —
    i.e., the structural concern (the claim is unfalsifiable due to
    missing scope) registers. Admissible claims have `threshold_met`
    False; downstream claims (C001-C024) then become applicable.
    """
    v = validate_scope_specification(claim_text)
    return {
        "claim_id":      "C000",
        "claim_text":    claim_text,
        "admissible":    v["admissible"],
        "present":       v["present"],
        "missing":       v["missing"],
        "matches":       v["matches"],
        "threshold_met": not v["admissible"],
        "falsifier":
            "a primary-source claim that explicitly answers all seven scope "
            "questions AND publishes a measurable falsifier",
    }


if __name__ == "__main__":
    bad  = "Autonomous trucking is more efficient at scale."
    good = ("Autonomous trucking reduces per-ton-mile energy by 12% over a "
            "7-year horizon, under stable diesel supply and no regulatory "
            "change, measured in joules, with infrastructure cost "
            "externalized to road authorities; profit accrues to fleet "
            "shareholders; falsified by audited data showing energy "
            "increase post-deployment.")
    print("bad:",  c000_verdict(bad))
    print("good:", c000_verdict(good))
