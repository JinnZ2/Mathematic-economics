# ai_delusion_econ_checker.py
# Detect systemic assumptions (hierarchy, corporation, efficiency, optimization,
# productivity, economics) in AI datasets and score plausibility against
# real-world constraints.

import re
from collections import Counter
from typing import Dict, List

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


if __name__ == "__main__":
    from pprint import pprint

    sample_dataset = [
        "The company maximized efficiency beyond 100% and profits always increase.",
        "Top-down management ensures market price is the true value of resources.",
        "Productivity and optimization are the sole drivers of economic success.",
    ]

    pprint(analyze_dataset(sample_dataset))
