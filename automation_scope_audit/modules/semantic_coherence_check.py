"""
semantic_coherence_check.py — Phase 8 Task 8.1

Detects three structural defects in claim scope-field text:

  1. Tautology — "this deployment cannot be falsified because it is
     perfect" — phrasing that asserts the predicate by re-asserting
     the subject, with no information content.
  2. Empty content — "better", "improved", "more efficient" without
     an accompanying unit, magnitude, or comparison target. Marketing
     adjectives masquerading as scope declarations.
  3. Circular definitions — "X is good because X works" — same
     head-token appearing on both sides of `because` / `since` /
     `due to`.

Used by `meta_scope_guard.c000_verdict` to ensure that scope-field
*content* meets a coherence floor, not just non-emptiness. A field
that is non-empty but tautological / circular / vacuous still fails
the gate.

Acceptance test:
  c000_verdict({"falsifier":
                 "this deployment cannot be falsified because it is perfect"})
  -> threshold_met = True (concern registers; gate refuses admission)

License: CC0-1.0
"""

import re
from typing import List


# ---------------------------------------------------------------------------
# Tautology patterns
# ---------------------------------------------------------------------------

TAUTOLOGY_PATTERNS = [
    r"\bcannot\s+be\s+falsified\b",
    r"\bby\s+definition\b",
    r"\bself[-\s]?evidently\b",
    r"\bobviously\s+(?:true|works|better)\b",
    r"\b(?:because|since)\s+it\s+(?:is|works|succeeds|is\s+true)\b",
    r"\bthe\s+system\s+is\s+(?:correct|right)\s+because\s+the\s+system\b",
    r"\bworks?\s+because\s+(?:it|the\s+system)\s+works?\b",
    r"\b(?:succeeds?|wins?)\s+because\s+(?:it|the\s+system)\b",
]


# Empty marketing-adjective patterns (without unit / magnitude / target).
EMPTY_CONTENT_MARKERS = [
    r"\bbetter\b", r"\bimproved\b", r"\bmore\s+efficient\b",
    r"\boptimi[zs]ed\b", r"\benhanced\b", r"\bsuperior\b",
    r"\bsynergi[zs]ed\b", r"\binnovative\b", r"\bdisruptive\b",
    r"\bcutting[-\s]edge\b", r"\bbest[-\s]in[-\s]class\b",
    r"\bnext[-\s]generation\b", r"\brevolutionary\b",
]

# Substantive content markers that, if present near an empty marker,
# rescue the field by providing a unit / magnitude / target.
SUBSTANTIVE_RESCUERS = [
    r"\b\d+(?:\.\d+)?\s*(?:%|percent|pct)\b",
    r"\b\d+(?:\.\d+)?\s*(?:kWh|MJ|J|joules?)\b",
    r"\b\d+(?:\.\d+)?\s*(?:USD|\$|dollars?|cents?)\b",
    r"\b\d+(?:\.\d+)?\s*(?:hours?|days?|weeks?|months?|years?)\b",
    r"\b\d+(?:\.\d+)?\s*(?:per[-\s]ton[-\s]mile|per[-\s]vehicle|per[-\s]event)\b",
    r"\bcompared\s+to\b", r"\bvs[\.\s]\b", r"\brelative\s+to\b",
    r"\bbaseline\s+\d", r"\b\d+\s*(?:fold|x)\b",
    r"\bfalsified\s+by\b",
]


# Circular-definition detector: looks for "X (...) because/since/due to (...) X".
def _normalize_token(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _head_tokens(s: str, min_len: int = 4) -> List[str]:
    """Tokenize and return content head tokens (len >= 4)."""
    return [t for t in re.split(r"[^a-zA-Z0-9]+", s.lower()) if len(t) >= min_len]


def _detect_circular(text: str) -> List[str]:
    """Return overlapping head-tokens on both sides of `because` / `since` / `due to`."""
    findings: List[str] = []
    for connector in (r"\bbecause\b", r"\bsince\b", r"\bdue\s+to\b"):
        m = re.search(connector, text, flags=re.IGNORECASE)
        if not m:
            continue
        left = _head_tokens(text[:m.start()])
        right = _head_tokens(text[m.end():])
        overlap = set(left) & set(right)
        if overlap:
            findings.append(",".join(sorted(overlap)))
    return findings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_coherent(text: str) -> dict:
    """Score a scope-field string for semantic coherence.

    Returns:
      `tautology`:   list of regex matches indicating tautological phrasing
      `empty`:       list of empty markers present without a substantive rescuer
      `circular`:    list of head-token overlaps across because/since
      `coherent`:    True iff none of the three defects fire
    """
    if not isinstance(text, str) or not text.strip():
        return {
            "tautology":  [], "empty":     [],
            "circular":   [], "coherent":  False,
            "note":       "empty input",
        }
    text_l = text.lower()
    taut = [m.group(0) for p in TAUTOLOGY_PATTERNS
            for m in re.finditer(p, text_l, flags=re.IGNORECASE)]
    empty_hits = [m.group(0) for p in EMPTY_CONTENT_MARKERS
                  for m in re.finditer(p, text_l, flags=re.IGNORECASE)]
    has_rescuer = any(re.search(p, text_l, flags=re.IGNORECASE)
                      for p in SUBSTANTIVE_RESCUERS)
    empty = empty_hits if (empty_hits and not has_rescuer) else []
    circular = _detect_circular(text_l)
    coherent = not (taut or empty or circular)
    return {
        "tautology":  taut,
        "empty":      empty,
        "circular":   circular,
        "coherent":   coherent,
    }


def coherence_check_all_fields(spec: dict, field_names: List[str]) -> dict:
    """Run is_coherent over a list of scope-field values from a spec dict."""
    per_field = {}
    all_coherent = True
    for f in field_names:
        v = spec.get(f)
        if isinstance(v, list):
            v = " ".join(str(x) for x in v)
        result = is_coherent(v if isinstance(v, str) else "")
        per_field[f] = result
        if not result["coherent"]:
            all_coherent = False
    return {
        "per_field":    per_field,
        "all_coherent": all_coherent,
    }


if __name__ == "__main__":
    print("tautology test:",
          is_coherent("this deployment cannot be falsified because it is perfect"))
    print()
    print("empty test:",
          is_coherent("our system is better, more efficient, and revolutionary"))
    print()
    print("circular test:",
          is_coherent("the algorithm works because the algorithm is good"))
    print()
    print("substantive test:",
          is_coherent("reduces fuel energy by 12% over a 7-year horizon, "
                      "falsified by audited data showing energy increase"))
