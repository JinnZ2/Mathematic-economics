"""
structural_recurrence.py

Make "same pattern, different dress" falsifiable.

THE MOVE
--------
A pattern is not its NAME. "Company town", "HOA", "charter city",
"neofeudalism", "regenerative-credits-to-ethanol-plant" are labels. Underneath
each is a set of MECHANISMS -- verb-first relational structures describing how
value, loss, control, and information actually flow. Strip the name. Match on
the mechanisms. If the physics overlaps, it is the same pattern wearing new
clothes, and that becomes checkable instead of arguable.

WHAT IS AUTOMATED / WHAT IS NOT
-------------------------------
NOT automated: deciding which mechanisms a case instantiates. That is the
analyst's structural reading -- yours -- and it is fully refutable. Change the
tags, the match changes.
Automated: the overlap between two mechanism sets. The comparison is computed,
not asserted. That is the whole separation -- judgment stays with the human,
arithmetic moves to the tool.

The `name` and `era` fields are metadata. The matcher NEVER reads them. This is
deliberate: the entire point is to match through the relabeling.

OPEN SEAM (multiple choice, by design)
--------------------------------------
"How much overlap counts as the same pattern?" is itself a real choice.
Three similarity framings are provided; signature is (set, set) -> float in
[0,1]. Pick the one you can defend; compare across them; add your own.

CONTRACT
--------
anti-freeze   : returns every match scored, sorted -- not a thresholded verdict.
refutation    : mechanisms and case tags are data; overwrite when they misfire.
energy_english: mechanisms are verb-first flow descriptions, no moral labels.
discrimination: ships with a non-matching control. A detector that matches
                everything proves nothing.
CC0. stdlib only. phone-buildable.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Tuple

# --- mechanisms: verb-first relational structures (the physics) --------------
# Describe the flow. Do not judge it. The id is the stable key; the relation is
# for humans. Add, rename, or split these freely -- they are a refutable vocab.

MECHANISMS: Dict[str, str] = {
    "value_up":        "labor value moves from worker to holder",
    "loss_down":       "loss moves from holder onto the public ledger",
    "subsidy_in":      "public funds enter; private profit exits",
    "exit_blocked":    "dependency or lock-in blocks the counterparty's exit",
    "terms_unilateral":"holder sets terms without counterparty consent",
    "opacity":         "information access is closed to affected parties",
    "incentive_decays":"the counterparty's incentive erodes after capture",
    "additionality_absent":   "payment lands on behavior that was already occurring",
    "routed_via_intermediary":"value reaches the counterparty only through a gatekeeper",
    # --- reciprocal / mutualist vocabulary (the contrast set) ---
    "value_circulates":"value circulates among participants",
    "terms_mutual":    "terms are set by participant consent",
    "exit_open":       "exit is available without penalty",
    "transparency":    "information is open to participants",
}


# --- structures --------------------------------------------------------------

@dataclass(frozen=True)
class Case:
    """A real-world instance. name/era are METADATA -- the matcher never reads
    them. mechanisms is the only thing matched on."""
    name: str
    era: str
    mechanisms: FrozenSet[str]

    def __post_init__(self):
        unknown = set(self.mechanisms) - set(MECHANISMS)
        assert not unknown, f"unknown mechanism ids: {unknown}"


@dataclass(frozen=True)
class Signature:
    """A named reference cluster of mechanisms -- e.g. an extraction signature.
    Used to score how strongly a case expresses a known structure."""
    name: str
    mechanisms: FrozenSet[str]


@dataclass
class Match:
    a: str
    b: str
    score: float
    shared: List[str]
    only_a: List[str]
    only_b: List[str]


# --- the contested seam: how much overlap counts as "same" -------------------

def sim_jaccard(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    """Symmetric. Shared over total. Penalizes mechanisms either side lacks."""
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def sim_overlap(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    """Shared over the smaller set. Catches 'A is a subset of B' -- a stripped-
    down instance of a richer pattern still reads as the same pattern."""
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def sim_containment(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    """Asymmetric: how much of A's structure appears in B. 'Does this new case
    contain the known signature?' -> sim_containment(signature, case)."""
    if not a:
        return 0.0
    return len(a & b) / len(a)


Similarity = Callable[[FrozenSet[str], FrozenSet[str]], float]


# --- core --------------------------------------------------------------------

def match(a: Case, b: Case, sim: Similarity = sim_jaccard) -> Match:
    shared = sorted(a.mechanisms & b.mechanisms)
    return Match(
        a=a.name, b=b.name,
        score=sim(a.mechanisms, b.mechanisms),
        shared=shared,
        only_a=sorted(a.mechanisms - b.mechanisms),
        only_b=sorted(b.mechanisms - a.mechanisms),
    )


def match_library(target: Case, library: List[Case],
                  sim: Similarity = sim_jaccard) -> List[Match]:
    """Score target against every case. Returns all of them sorted high->low.
    No threshold, no verdict -- read the trajectory yourself (anti-freeze)."""
    out = [match(target, c, sim) for c in library if c.name != target.name]
    return sorted(out, key=lambda m: m.score, reverse=True)


def score_signature(case: Case, sig: Signature) -> float:
    """How much of a known signature this case expresses. Containment of the
    signature within the case."""
    return sim_containment(sig.mechanisms, case.mechanisms)


# --- seed library (your structural readings -- all refutable) ----------------

EXTRACTION = Signature("extraction", frozenset({
    "value_up", "loss_down", "subsidy_in", "exit_blocked",
    "terms_unilateral", "opacity",
}))

COMPANY_TOWN = Case("company town", "1880-1930", frozenset({
    "value_up", "exit_blocked", "terms_unilateral", "opacity", "subsidy_in",
}))
HOA_TOWN = Case("private HOA town", "1990-", frozenset({
    "value_up", "exit_blocked", "terms_unilateral", "opacity",
}))
CHARTER_CITY = Case("charter city / ZEDE", "2010-", frozenset({
    "value_up", "subsidy_in", "terms_unilateral", "opacity", "loss_down",
}))
ETHANOL_CREDITS = Case("regen-credits -> ethanol plant", "2020-", frozenset({
    "subsidy_in", "value_up", "incentive_decays", "terms_unilateral",
}))
# the control: a reciprocal structure that must NOT read as extraction
COMMONS_COOP = Case("worker / commons co-op", "various", frozenset({
    "value_circulates", "terms_mutual", "exit_open", "transparency",
}))

LIBRARY = [COMPANY_TOWN, HOA_TOWN, CHARTER_CITY, ETHANOL_CREDITS, COMMONS_COOP]


# --- falsification self-test -------------------------------------------------

if __name__ == "__main__":
    print("=== identity & disjoint sanity ===")
    assert abs(match(COMPANY_TOWN, COMPANY_TOWN).score - 1.0) < 1e-9, "self != 1"
    assert match(COMPANY_TOWN, COMMONS_COOP).score == 0.0, "extraction vs co-op should be 0"
    print("  self-match = 1.0 ; extraction vs co-op = 0.0  ok")

    print("\n=== match the relabelings against the company town (name hidden) ===")
    for m in match_library(COMPANY_TOWN, LIBRARY, sim_overlap):
        tag = "SAME STRUCTURE" if m.score >= 0.6 else "diverges"
        print(f"  {m.b:32s} score={m.score:.2f}  [{tag}]  shared={m.shared}")

    print("\n=== each case vs the extraction signature (containment) ===")
    scores = {}
    for c in LIBRARY:
        s = score_signature(c, EXTRACTION)
        scores[c.name] = s
        print(f"  {c.name:32s} expresses {s*100:4.0f}% of the extraction signature")

    print("\n=== same comparison across all three similarity framings ===")
    pairs: List[Tuple[str, Case]] = [("company<->charter", CHARTER_CITY)]
    for label, other in pairs:
        for nm, fn in [("jaccard", sim_jaccard), ("overlap", sim_overlap),
                       ("containment", sim_containment)]:
            print(f"  {label} [{nm:11s}] = {fn(COMPANY_TOWN.mechanisms, other.mechanisms):.2f}")

    # discrimination gate: the detector must separate extraction from reciprocity
    extraction_cases = [c for c in LIBRARY if c.name != "worker / commons co-op"]
    assert all(scores[c.name] >= 0.5 for c in extraction_cases), \
        "an extraction case failed to express the signature -- under-matching"
    assert scores["worker / commons co-op"] == 0.0, \
        "the co-op control matched extraction -- the detector matches everything"
    print("\ndiscrimination gate passed: relabeled extraction reads as one structure; "
          "the reciprocal control reads as zero.")
