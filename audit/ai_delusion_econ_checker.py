# ai_delusion_econ_checker.py
# Detect systemic assumptions (hierarchy, corporation, efficiency, optimization,
# productivity, economics) in AI datasets and score plausibility against
# real-world constraints.

import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List

# Optional PhysicsGuard integration. See physics_guard/PROVENANCE.md.
_PG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "physics_guard")
if os.path.isdir(_PG_DIR) and _PG_DIR not in sys.path:
    sys.path.insert(0, _PG_DIR)
try:
    from main import check as physics_check  # type: ignore
    _HAS_PHYSICS_GUARD = True
except Exception:
    _HAS_PHYSICS_GUARD = False

# ---------------------------
# Patterns for conceptual delusions
# ---------------------------
DELUSION_PATTERNS = {
    "hierarchy": [r"\btop[- ]?down\b", r"\bmanagement\b", r"\bchain of command\b"],
    "corporation": [r"\bcompany\b", r"\bcorporation\b", r"\bshareholder\b"],
    "efficiency": [r"\befficien(cy|t)\b", r"\bmaxim(ize|ization)\b", r"\bthroughput\b"],
    "optimization": [r"\boptimi[sz]e\b", r"\bperformance\b"],
    "productivity": [r"\bproductivit(y|ies)\b", r"\boutput\b", r"\bworkload\b"],
    "economics": [
        r"\beconomic(s|al)?\b",
        r"\bprofit\b",
        r"\bmarket\b",
        r"\bprice\b",
        r"\bvaluation\b",
    ],
}


# ---------------------------
# Plausibility rules
# ---------------------------
def plausibility_score(text: str) -> Dict[str, int]:
    """Return plausibility flags (0 = plausible, 1 = questionable) based on
    systemic constraints. Example checks:
        - efficiency > 100% (hyperbolic claims)
        - profit statements framed as absolutes
        - price / valuation treated as absolute truth
    """
    flags = {}

    if re.search(r"(efficiency|throughput).{0,10}(>|\bmore than\b)\s*100", text):
        flags["efficiency_implausible"] = 1
    else:
        flags["efficiency_implausible"] = 0

    if re.search(r"\bprofit\b.*\balways\b|\bnever\b", text):
        flags["profit_absolute"] = 1
    else:
        flags["profit_absolute"] = 0

    if re.search(r"\b(price|valuation)\b.*\btrue\b|\breal\b", text):
        flags["price_absolute"] = 1
    else:
        flags["price_absolute"] = 0

    return flags


# ---------------------------
# Extract conceptual delusions
# ---------------------------
def extract_delusions(text: str) -> Counter:
    text = text.lower()
    counts: Counter = Counter()
    for concept, patterns in DELUSION_PATTERNS.items():
        for pat in patterns:
            matches = re.findall(pat, text)
            counts[concept] += len(matches)
    return counts


# ---------------------------
# Analyze dataset
# ---------------------------
def analyze_dataset(dataset: List[str]) -> Dict:
    """Aggregate delusion counts and per-entry plausibility flags across a
    dataset of text strings."""
    total_counts: Counter = Counter()
    plausibility_flags_list = []

    for entry in dataset:
        total_counts += extract_delusions(entry)
        plausibility_flags_list.append(plausibility_score(entry))

    return {
        "delusion_counts": dict(total_counts),
        "plausibility_flags": plausibility_flags_list,
    }


def analyze_dataset_with_physics(dataset: List[str]) -> Dict[str, Any]:
    """Regex-based analysis augmented with PhysicsGuard verdicts.

    Runs the standard `analyze_dataset` pipeline AND passes each entry through
    PhysicsGuard's `check()` to screen for physical conservation violations
    (e.g. "efficiency beyond 100%"). Falls back to regex-only if the
    physics_guard snapshot is not importable.

    Returned dict contains:
        - delusion_counts: aggregated regex pattern counts
        - plausibility_flags: per-entry regex plausibility flags
        - physics_verdicts: per-entry PhysicsGuard verdict dicts (or None)
        - physics_available: whether PhysicsGuard was usable
    """
    base = analyze_dataset(dataset)
    if _HAS_PHYSICS_GUARD:
        verdicts = [physics_check(entry) for entry in dataset]
    else:
        verdicts = [None] * len(dataset)
    return {
        **base,
        "physics_verdicts": verdicts,
        "physics_available": _HAS_PHYSICS_GUARD,
    }


if __name__ == "__main__":
    from pprint import pprint

    sample_dataset = [
        "The company maximized efficiency beyond 100% and profits always increase.",
        "Top-down management ensures market price is the true value of resources.",
        "Productivity and optimization are the sole drivers of economic success.",
    ]

    print("=== regex-only ===")
    pprint(analyze_dataset(sample_dataset))
    print("\n=== regex + PhysicsGuard ===")
    augmented = analyze_dataset_with_physics(sample_dataset)
    print(f"physics_available: {augmented['physics_available']}")
    for entry, verdict in zip(sample_dataset, augmented["physics_verdicts"]):
        if verdict is None:
            continue
        print(f"  [{verdict['verdict']:>9s} score={verdict['score']:.2f}]  {entry[:70]}")
