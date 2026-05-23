"""
scope_collapse_detector.py  —  C006, C007

"Automation" framing collapses distinct labor categories; threat-narrative
deployment correlates with wage suppression, not efficiency gain.

Falsifier (C006): scope-honest deployment language in primary sources.
Falsifier (C007): wage data showing parity or increase post-automation.

Pure-regex / pure-stdlib. Designed to be runnable on press releases,
investor decks, analyst notes, and academic abstracts without a network
call or model dependency.

License: CC0-1.0
"""

import re
from typing import Dict, List


# Scope-collapse markers: language that asserts breadth without
# substantiation. The presence of any of these without a matching
# scope-honest disclosure flags the claim.
OVERREACH_PATTERNS = [
    r"\bfully\s+autonomous\b",
    r"\bdriverless\b",
    r"\bend[-\s]to[-\s]end\s+automat",
    r"\breplaces?\s+(?:the\s+)?(?:trucker|driver|operator)s?\b",
    r"\bno\s+humans?\s+(?:in|on)\b",
    r"\bautonom(?:ous|y)\s+(?:trucking|freight|logistics)\b",
]

SCOPE_HONEST_PATTERNS = [
    r"\bdepot[-\s]to[-\s]depot\b",
    r"\bhub[-\s]to[-\s]hub\b",
    r"\bhighway\s+only\b",
    r"\bgeo[-\s]?fenced?\b",
    r"\bunder\s+human\s+supervision\b",
    r"\bsafety\s+driver\b",
    r"\bteleoperat(?:or|ion|ed)\b",
    r"\bL[234]\b",                              # SAE level disclosure
    r"\bfixed[-\s]route\b",
    r"\bHD[-\s]mapped?\b",
]

THREAT_NARRATIVE_PATTERNS = [
    r"\bdriver\s+shortage\b",
    r"\bwage\s+(?:inflation|pressure)\b",
    r"\blabor\s+cost\s+(?:burden|crisis)\b",
    r"\baging\s+driver\s+population\b",
    r"\bunsustainable\s+wage\b",
    r"\bdisruption\b.*\b(?:trucking|freight)\b",
]

# Task categories that "automation" tends to collapse together.
LABOR_CATEGORIES = ("haul", "navigation", "site_work", "monitoring",
                    "compliance", "interface")


def _find(patterns: List[str], text: str) -> List[str]:
    text_lower = text.lower()
    hits: List[str] = []
    for p in patterns:
        for m in re.finditer(p, text_lower, flags=re.IGNORECASE):
            hits.append(m.group(0))
    return hits


def parse_automation_claim(claim_text: str) -> dict:
    """Extract scope_breadth, conditions, and falsifiers from a claim string."""
    overreach = _find(OVERREACH_PATTERNS, claim_text)
    scope_honest = _find(SCOPE_HONEST_PATTERNS, claim_text)
    threat = _find(THREAT_NARRATIVE_PATTERNS, claim_text)
    categories_named = [c for c in LABOR_CATEGORIES
                        if re.search(rf"\b{c}\b", claim_text, re.IGNORECASE)]
    return {
        "raw":                claim_text,
        "overreach_markers":  overreach,
        "scope_honest_markers": scope_honest,
        "threat_markers":     threat,
        "categories_named":   categories_named,
        "scope_breadth":      "broad" if overreach and not scope_honest
                              else "narrow" if scope_honest
                              else "unspecified",
        "conditions_disclosed": bool(scope_honest),
        "falsifiers_disclosed": bool(re.search(r"\bfalsif", claim_text, re.IGNORECASE)),
    }


def detect_overgeneralization(claim: dict, evidence: dict) -> List[str]:
    """Compare a parsed claim against operational evidence.

    `evidence` may carry:
      - `automated_categories`: list of LABOR_CATEGORIES actually displaced.
      - `route_variance`: float from `scope_geometry.measure_route_variance`.
      - `infrastructure_state`: dict consumed by `classify_scope`.
      - `wage_change_pct`: signed percent change post-deployment in region.
      - `productivity_change_pct`: signed percent change to pair against wages.

    Returns a list of flag strings.
    """
    flags: List[str] = []

    if claim["scope_breadth"] == "broad" and not claim["conditions_disclosed"]:
        flags.append("missing_preconditions")

    auto_cats = set(evidence.get("automated_categories", []))
    uncovered = [c for c in LABOR_CATEGORIES if c not in auto_cats]
    if claim["scope_breadth"] == "broad" and uncovered:
        flags.append("hidden_labor:" + ",".join(uncovered))

    variance = evidence.get("route_variance")
    if variance is not None and variance > 0.20 and claim["scope_breadth"] == "broad":
        flags.append("geometry_mismatch")

    infra = evidence.get("infrastructure_state") or {}
    if (infra.get("paved_pct", 1.0) < 0.5 or infra.get("mapped_pct", 1.0) < 0.5) \
            and claim["scope_breadth"] == "broad":
        flags.append("infrastructure_precondition_unstated")

    if "lifecycle_years" in evidence or "well_decline_years" in evidence:
        eq_life = evidence.get("equipment_lifespan_years", 7)
        well_life = evidence.get("well_decline_years", eq_life)
        if well_life < eq_life and claim["scope_breadth"] == "broad":
            flags.append("lifecycle_omission")

    if claim["threat_markers"]:
        wage = evidence.get("wage_change_pct")
        prod = evidence.get("productivity_change_pct")
        if wage is not None and wage < -10.0 and (prod is None or prod < abs(wage)):
            flags.append("wage_suppression_pattern")

    return flags


def c006_verdict(claim_text: str, evidence: dict | None = None) -> dict:
    claim = parse_automation_claim(claim_text)
    flags = detect_overgeneralization(claim, evidence or {})
    return {
        "claim_id": "C006",
        "parsed_claim": claim,
        "flags": flags,
        "scope_collapse_detected": bool(flags),
        "falsifier": "scope-honest deployment language in primary sources",
    }


def c007_verdict(claim_text: str, wage_change_pct: float,
                 productivity_change_pct: float | None = None,
                 region: str = "") -> dict:
    """C007 explicit gate on wage suppression vs productivity match."""
    claim = parse_automation_claim(claim_text)
    threat_active = bool(claim["threat_markers"])
    wage_drop_significant = wage_change_pct < -10.0
    productivity_matches = (productivity_change_pct is not None
                            and productivity_change_pct >= abs(wage_change_pct))
    suppression = wage_drop_significant and not productivity_matches
    return {
        "claim_id": "C007",
        "region": region,
        "threat_narrative_active": threat_active,
        "wage_change_pct": wage_change_pct,
        "productivity_change_pct": productivity_change_pct,
        "wage_suppression_pattern": suppression,
        "threshold_met": threat_active and suppression,
        "falsifier": "wage data showing parity or increase post-automation",
    }


if __name__ == "__main__":
    pitch = ("Our fully autonomous trucking platform replaces the driver and "
             "addresses the chronic driver shortage with end-to-end automation.")
    honest = ("Our depot-to-depot system runs SAE L4 on HD-mapped highway "
              "segments under human supervision; teleoperators handle exits.")
    print("pitch:", c006_verdict(pitch, {
        "automated_categories": ["haul"],
        "route_variance": 0.25,
        "infrastructure_state": {"paved_pct": 0.4, "mapped_pct": 0.3},
        "well_decline_years": 3,
        "equipment_lifespan_years": 7,
    }))
    print("honest:", c006_verdict(honest, {
        "automated_categories": ["haul", "navigation"],
        "route_variance": 0.03,
        "infrastructure_state": {"paved_pct": 0.99, "mapped_pct": 0.99},
    }))
    print("C007 sample:", c007_verdict(pitch, wage_change_pct=-15.0,
                                        productivity_change_pct=3.0,
                                        region="basin_X"))
