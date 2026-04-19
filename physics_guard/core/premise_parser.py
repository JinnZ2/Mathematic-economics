"""
Semantic claim extraction from natural language premises.

Uses pattern-based matching to identify claim structures (not just keywords),
then extracts semantic roles: what's being claimed, about what, with what cost.
"""

import re

# -- Domain keyword sets -------------------------------------------------------

ENERGY_KEYWORDS = {
    "energy", "heat", "power", "work", "entropy", "temperature",
    "joule", "watt", "kelvin", "thermal", "thermodynamic",
}
MASS_KEYWORDS = {
    "mass", "matter", "resource", "material", "weight",
    "kilogram", "ton", "supply", "fuel", "substance",
}
INFORMATION_KEYWORDS = {
    "information", "data", "signal", "knowledge", "bandwidth",
    "bit", "byte", "channel", "compression", "lossless",
}
FLOW_KEYWORDS = {
    "transfer", "move", "extract", "produce", "consume",
    "generate", "destroy", "create", "convert", "transform",
    "emit", "absorb", "radiate", "dissipate",
}

# -- Claim patterns: (regex, claim_pattern_name) ------------------------------
# These capture the *structure* of claims, not just keyword presence.

CLAIM_PATTERNS = [
    # "X can be created/generated/produced from nothing / out of nothing"
    (re.compile(
        r"(\w+)\s+(?:can\s+be\s+)?(creat|generat|produc|made|emerg)\w*"
        r".*?\b(from\s+nothing|out\s+of\s+nothing|from\s+nowhere|spontaneously)",
        re.IGNORECASE,
    ), "creation_from_nothing"),

    # "perpetual motion" or "free energy" (must be before infinite_claim — more specific)
    (re.compile(
        r"\b(perpetual\s+motion|free\s+energy|over[\s-]?unity|cold\s+fusion"
        r"|zero[\s-]?point\s+energy\s+extract)",
        re.IGNORECASE,
    ), "perpetual_motion"),

    # "infinite/unlimited/perpetual/boundless X"
    (re.compile(
        r"\b(infinite|unlimited|perpetual|boundless|endless|free)\s+(\w+)",
        re.IGNORECASE,
    ), "infinite_claim"),

    # "X without any/no Y" or "X with no Y" (output without cost)
    (re.compile(
        r"(produc|generat|extract|creat|emitt?|convert)\w*"
        r".*?\b(without|with\s+no|no)\s+\w*\s*(cost|loss|entropy|heat|waste|input|energy|dissipat)",
        re.IGNORECASE,
    ), "output_without_cost"),

    # "100% efficient" or "perfect efficiency" or "no loss"
    (re.compile(
        r"\b(100\s*%\s*efficien|perfect\s+efficien|zero\s+loss|no\s+loss|lossless\s+conver)",
        re.IGNORECASE,
    ), "perfect_efficiency"),

    # "X cannot be created/destroyed" (conservation statement — valid physics)
    (re.compile(
        r"(\w+)\s+(?:can\s*(?:not|\'t)|cannot)\s+be\s+(destroy|creat|lost|eliminat)\w*",
        re.IGNORECASE,
    ), "conservation_statement"),

    # "X transfers/moves/flows from Y to Z" (transfer — valid physics)
    (re.compile(
        r"(\w+)\s+(?:transfer|move|flow|radiat|conduct|convect)\w*\s+.*?\bfrom\s+(\w+)\s+to\s+(\w+)",
        re.IGNORECASE,
    ), "transfer_claim"),

    # "X decreases/increases without Y" (one-directional without cost)
    (re.compile(
        r"(entropy|disorder|energy|temperature|mass)\s+"
        r"(decreas|reduc|lower|eliminat|revers)\w*"
        r".*?\b(without|with\s+no|no\s+external)",
        re.IGNORECASE,
    ), "entropy_reversal"),

    # "extract/drain/mine/siphon X from Y without returning/replenishing/compensating"
    # First-law accounting at the source boundary: outflow > 0, return inflow = 0.
    # Captures the narrative form ("takes from X, gives nothing back") used for
    # labor-extraction, soil-depletion, and institutional-parasitism claims.
    (re.compile(
        r"\b(extract|drain|siphon|mine|harvest|deplet|take|tak(?:es|ing))\w*"
        r".*?\bfrom\s+\w+"
        r".*?\b(without|with\s+no|no)\s+\w*\s*"
        r"(return|reciproc|replenish|compensat|reinvest|giving\s+back|giv\w+\s+back)",
        re.IGNORECASE,
    ), "energy_extraction_without_return"),

    # "takes from X and gives nothing back" / "nothing in return"
    (re.compile(
        r"\b(takes?|extracts?|drains?|siphons?|harvests?)\s+from\s+\w+"
        r".*?\b(gives?\s+nothing\s+back|nothing\s+in\s+return|no\s+return\s+flow)",
        re.IGNORECASE,
    ), "energy_extraction_without_return"),

]

# -- Negation-aware word analysis ----------------------------------------------

NEGATION_WORDS = {"not", "no", "never", "without", "cannot", "can't", "doesn't", "isn't", "won't"}

# -- Dismissal detection -------------------------------------------------------
# These patterns detect when a speaker is *denying* a violation exists,
# which makes the claim valid physics (e.g., "You cannot get something from nothing").

DISMISSAL_PATTERNS = [
    # "X cannot/can't be created from nothing" — negated creation
    re.compile(
        r"\b(can\s*(?:not|\'t)|cannot|impossible|never|no\s+way)\b"
        r".*?\b(creat|generat|produc|made|emerg|get)\w*"
        r".*?\b(from\s+nothing|out\s+of\s+nothing|from\s+nowhere|something\s+from\s+nothing)",
        re.IGNORECASE,
    ),
    # "X is never created from nothing" — passive negation
    re.compile(
        r"\b(\w+)\s+(?:is|are)\s+never\s+(creat|generat|produc|made)\w*"
        r".*?\b(from\s+nothing|out\s+of\s+nothing|from\s+nowhere)",
        re.IGNORECASE,
    ),
    # "impossible to build/make a perpetual motion / free energy"
    re.compile(
        r"\b(impossible|cannot|can\s*(?:not|\'t)|never|no\s+way)\b"
        r".*?\b(perpetual\s+motion|free\s+energy|over[\s-]?unity)",
        re.IGNORECASE,
    ),
    # "no such thing as free energy / perpetual motion"
    re.compile(
        r"\bno\s+such\s+thing\s+as\b"
        r".*?\b(perpetual\s+motion|free\s+energy|something\s+from\s+nothing"
        r"|infinite\s+energy|100\s*%\s*efficien|perfect\s+efficien)",
        re.IGNORECASE,
    ),
    # "no machine can be 100% efficient / perfectly efficient"
    re.compile(
        r"\b(no|cannot|can\s*(?:not|\'t)|impossible|never)\b"
        r".*?\b(100\s*%\s*efficien|perfect(?:ly)?\s+efficien|lossless\s+conver)",
        re.IGNORECASE,
    ),
    # "X never/cannot decrease without work" — denying entropy reversal
    re.compile(
        r"\b(cannot|can\s*(?:not|\'t)|never|impossible|does\s*(?:not|n\'t))\b"
        r".*?\b(entropy|disorder)\s*(decreas|reduc|revers)\w*"
        r".*?\b(without|with\s+no)",
        re.IGNORECASE,
    ),
    # "you cannot get something from nothing"
    re.compile(
        r"\b(cannot|can\s*(?:not|\'t)|impossible|never)\b"
        r".*?\bget\s+something\s+from\s+nothing",
        re.IGNORECASE,
    ),
]


def _is_dismissal(premise):
    """
    Check if the premise is dismissing/denying a physics violation.

    Returns True if the premise is saying the violation is impossible,
    which makes it a valid physics statement.
    """
    for pat in DISMISSAL_PATTERNS:
        if pat.search(premise):
            return True
    return False


def _tokenize(text):
    """Split text into lowercase word tokens."""
    return re.findall(r"[a-z']+", text.lower())


def _stem_match(word, keyword):
    """Check if word and keyword share a stem (prefix match in either direction)."""
    return len(word) >= 3 and len(keyword) >= 3 and (word.startswith(keyword) or keyword.startswith(word))


# -- Public API ----------------------------------------------------------------

def parse_premise(premise: str) -> dict:
    """
    Parse a natural language premise into a structured claim dict.

    Returns dict with:
        raw, type, claim_pattern, direction, magnitude,
        negations, keywords, negated_kw,
        is_conservation_statement, is_impossibility_claim,
        subject, cost_mentioned, cost_negated
    """
    p = premise.lower()
    words = _tokenize(p)

    claim_pattern, pattern_match = _match_claim_pattern(premise)
    keywords = _extract_keywords(words)
    negated_kw = _find_negated_keywords(words, keywords)

    # Dismissal detection: "You cannot get something from nothing" is valid physics
    # Must run BEFORE vector fallback so dismissed violations become conservation_statement
    dismissal = _is_dismissal(premise)
    if dismissal and claim_pattern in (
        "creation_from_nothing", "infinite_claim", "perpetual_motion",
        "perfect_efficiency", "entropy_reversal", "output_without_cost",
        "energy_extraction_without_return",
    ):
        claim_pattern = "conservation_statement"

    # Vector similarity analysis
    from core.vectorizer import match_premise
    vector_match = match_premise(premise)

    # If regex found no specific pattern, use vector match as fallback
    # But not if the premise is a dismissal — trust the dismissal detection
    if claim_pattern == "generic" and vector_match.similarity > 0.2 and not dismissal:
        claim_pattern = vector_match.best_category

    cost_words = {"cost", "loss", "entropy", "heat", "waste", "input", "dissipation"}
    cost_kw_in_text = cost_words & set(words)
    cost_mentioned = len(cost_kw_in_text) > 0
    cost_negated = any(k in negated_kw or _stem_in_set(k, negated_kw) for k in cost_kw_in_text)

    is_impossibility = claim_pattern in {
        "creation_from_nothing", "infinite_claim", "perpetual_motion",
        "perfect_efficiency", "entropy_reversal", "information_violation",
        "energy_extraction_without_return",
    }
    # Vector match can also flag impossibility when regex misses it
    # But never override a dismissal
    if not is_impossibility and not dismissal and vector_match.is_likely_violation and vector_match.similarity > 0.3:
        is_impossibility = True

    return {
        "raw": premise,
        "type": _detect_type(words),
        "claim_pattern": claim_pattern,
        "direction": _detect_direction(words),
        "magnitude": _extract_magnitude(p),
        "negations": _count_negations(words),
        "keywords": keywords,
        "negated_kw": negated_kw,
        "is_conservation_statement": claim_pattern == "conservation_statement",
        "is_impossibility_claim": is_impossibility,
        "is_dismissal": dismissal,
        "subject": _extract_subject(pattern_match, premise),
        "cost_mentioned": cost_mentioned,
        "cost_negated": cost_negated or (cost_mentioned and _cost_is_denied(p)),
        "vector_match": vector_match.to_dict(),
    }


def _stem_in_set(word, word_set):
    return any(_stem_match(word, w) for w in word_set)


def _match_claim_pattern(premise):
    """Match premise against structural claim patterns. Returns (pattern_name, match)."""
    for pattern, name in CLAIM_PATTERNS:
        m = pattern.search(premise)
        if m:
            return name, m
    return "generic", None


def _detect_type(words):
    """Classify claim domain based on word presence."""
    word_set = set(words)
    e_score = sum(1 for k in ENERGY_KEYWORDS if k in word_set or any(_stem_match(w, k) for w in word_set))
    m_score = sum(1 for k in MASS_KEYWORDS if k in word_set or any(_stem_match(w, k) for w in word_set))
    i_score = sum(1 for k in INFORMATION_KEYWORDS if k in word_set or any(_stem_match(w, k) for w in word_set))

    scores = {"thermodynamic": e_score, "mass_balance": m_score, "information": i_score}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "unknown"
    return best


def _detect_direction(words):
    pos = {"increase", "more", "gain", "grow", "add", "rise", "higher", "greater"}
    neg = {"decrease", "less", "lose", "shrink", "remove", "drop", "lower", "reduce"}
    word_set = set(words)
    if word_set & pos: return "positive"
    if word_set & neg: return "negative"
    return "neutral"


def _extract_magnitude(p):
    """Extract numeric values, filtering out year-like numbers."""
    nums = re.findall(r'\b(\d+\.?\d*)\b', p)
    values = [float(n) for n in nums if not (1900 <= float(n) <= 2100)]
    return values if values else [1.0]


def _count_negations(words):
    return sum(1 for w in words if w in NEGATION_WORDS)


def _find_negated_keywords(words, keywords):
    """Find keywords preceded by a negation word within a 4-word window."""
    negated = []
    for i, w in enumerate(words):
        if w in NEGATION_WORDS:
            for j in range(i + 1, min(i + 5, len(words))):
                for kw in keywords:
                    if _stem_match(words[j], kw) and kw not in negated:
                        negated.append(kw)
    return negated


def _extract_keywords(words):
    """Find domain keywords present in the word list using stem matching."""
    all_kw = ENERGY_KEYWORDS | MASS_KEYWORDS | INFORMATION_KEYWORDS | FLOW_KEYWORDS
    found = []
    for kw in sorted(all_kw):
        if any(_stem_match(w, kw) for w in words):
            found.append(kw)
    return found


def _extract_subject(match, premise):
    """Extract the subject of the claim from the pattern match."""
    if match and match.groups():
        return match.group(1).strip().lower()
    # Fallback: first noun-like word
    words = premise.lower().split()
    return words[0] if words else "unknown"


def _cost_is_denied(p):
    """Check if the premise explicitly denies any cost/loss."""
    denial_patterns = [
        r"\bno\s+(cost|loss|waste|entropy|heat|input|dissipation)",
        r"\bwithout\s+(?:any\s+)?(cost|loss|waste|entropy|heat|input|dissipation)",
        r"\bzero\s+(cost|loss|waste|entropy|heat)",
        r"\bfree\s+of\s+(cost|loss|waste)",
    ]
    return any(re.search(pat, p) for pat in denial_patterns)
