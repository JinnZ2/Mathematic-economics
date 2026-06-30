"""
echo_collapse.py

Tell independent corroboration apart from one source echoed at volume.

THE PROBLEM
-----------
A pattern-matcher (model or person) reads N headlines saying the same thing and
scores it as strong, well-corroborated consensus. But fifteen outlets running
near-identical copy from one press release is not fifteen sources -- it is one
source amplified fifteen times. Volume gets mistaken for verification. The lone
outlet that diverged gets buried under the echo.

THE MOVE
--------
Collapse echo to its origin. Shingle each text, cluster near-duplicates, and
report:
  - effective independent voices (number of clusters), vs raw count
  - corroboration inflation (raw / effective)
  - the boilerplate phrases repeated across most sources (the injected line)
  - the singletons: voices that did NOT echo -- where new info or dissent lives

WHAT IS / ISN'T MEASURED
------------------------
Measured: TEXTUAL independence -- how much wording is shared. Computed, not
asserted.
NOT measured: truth, or semantic claim-level agreement. Two sources can reword
the same falsehood independently and read as independent here. Swap the
similarity function for an embedding/LLM scorer to get semantic dedup; the rest
of the module is unchanged. That is the seam.

A high echo score is not "false" and a singleton is not "true". Echo means
"do not count this as N independent confirmations." Singleton means "look here,
the volume is not hiding this one."

OPEN SEAM (multiple choice, by design)
--------------------------------------
Two contested choices, both pluggable:
  - similarity:  jaccard | containment   (set, set) -> float
  - linkage:     single | complete       (matrix, threshold) -> clusters
Pick what you can defend; compare across them.

CONTRACT
--------
anti-freeze   : returns clusters + singletons + inflation, not a verdict.
refutation    : thresholds and shingle size are data; tune when they misfire.
discrimination: ships with a control -- a dissenter in an echo pile must survive.
CC0. stdlib only. phone-buildable.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Tuple
import re
import math
from collections import Counter

# --- text -> shingles --------------------------------------------------------

def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def shingles(text: str, k: int = 3) -> frozenset:
    """k-word n-grams. Captures shared phrasing, not just shared words."""
    toks = tokenize(text)
    if len(toks) < k:
        return frozenset({tuple(toks)}) if toks else frozenset()
    return frozenset(tuple(toks[i:i + k]) for i in range(len(toks) - k + 1))


# --- similarity seam ---------------------------------------------------------

def sim_jaccard(a: frozenset, b: frozenset) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def sim_containment(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


Similarity = Callable[[frozenset, frozenset], float]


# --- linkage seam ------------------------------------------------------------

def link_single(matrix: List[List[float]], t: float) -> List[List[int]]:
    """Single linkage (transitive): A~B and B~C puts A,B,C together.
    Aggressive collapse -- chains of paraphrase merge."""
    n = len(matrix)
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(x, y):
        parent[find(x)] = find(y)
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i][j] >= t:
                union(i, j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def link_complete(matrix: List[List[float]], t: float) -> List[List[int]]:
    """Complete linkage (strict): merge clusters only if EVERY cross pair meets
    the threshold. Conservative -- keeps near-duplicates apart unless tight."""
    clusters = [[i] for i in range(len(matrix))]
    def min_cross(a, b):
        return min(matrix[i][j] for i in a for j in b)
    merged = True
    while merged:
        merged = False
        best, bi, bj = -1.0, -1, -1
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                m = min_cross(clusters[i], clusters[j])
                if m >= t and m > best:
                    best, bi, bj = m, i, j
        if bi >= 0:
            clusters[bi].extend(clusters[bj])
            del clusters[bj]
            merged = True
    return clusters


Linkage = Callable[[List[List[float]], float], List[List[int]]]


# --- structures --------------------------------------------------------------

@dataclass(frozen=True)
class Source:
    id: str
    outlet: str
    text: str


@dataclass
class Report:
    raw_count: int
    effective_count: int           # number of independent clusters
    inflation: float               # raw / effective
    clusters: List[List[str]]      # source ids grouped by echo
    singletons: List[str]          # ids that echoed no one -- look here
    boilerplate: List[str]         # phrases repeated across most sources


# --- core --------------------------------------------------------------------

def analyze(sources: List[Source], k: int = 2, threshold: float = 0.5,
            sim: Similarity = sim_containment,
            linkage: Linkage = link_single,
            boilerplate_frac: float = 0.6) -> Report:
    shs = [shingles(s.text, k) for s in sources]
    n = len(sources)
    matrix = [[1.0 if i == j else sim(shs[i], shs[j]) for j in range(n)]
              for i in range(n)]
    clusters_idx = linkage(matrix, threshold)
    clusters = [[sources[i].id for i in g] for g in clusters_idx]
    singletons = [g[0] for g in clusters if len(g) == 1]

    # boilerplate: shingles appearing in >= frac of sources
    cutoff = math.ceil(boilerplate_frac * n)
    counts = Counter()
    for sh in shs:
        for gram in sh:
            counts[gram] += 1
    boiler = [" ".join(g) for g, c in counts.items() if c >= cutoff]

    eff = len(clusters)
    return Report(
        raw_count=n,
        effective_count=eff,
        inflation=n / eff if eff else float("inf"),
        clusters=clusters,
        singletons=singletons,
        boilerplate=sorted(boiler),
    )


# --- falsification self-test -------------------------------------------------

if __name__ == "__main__":
    # illustrative synthetic copy (not real outlet text): four near-verbatim
    # echoes sharing a common release phrase + one genuinely divergent source.
    _common = "the plan helps farmers capture new value from regenerative practices through biofuel markets"
    echo_pile = [
        Source("a", "Outlet A", _common + " officials announced today"),
        Source("b", "Outlet B", "in a major step " + _common),
        Source("c", "Outlet C", _common + " according to the agency"),
        Source("d", "Outlet D", "reports say " + _common + " nationwide"),
        Source("e", "Outlet E", "credit lands on processors while the premium for farmers erodes within two seasons analysts warn"),
    ]
    independent_set = [
        Source("p", "P", "soil carbon measurement remains contested across regions"),
        Source("q", "Q", "corn ethanol land use offsets much of the climate benefit"),
        Source("r", "R", "voluntary programs rarely change behavior of non adopters"),
    ]

    print("=== echo pile (expect collapse + inflation, dissenter survives) ===")
    rep = analyze(echo_pile, threshold=0.6)
    print(f"  raw={rep.raw_count}  effective={rep.effective_count}  inflation={rep.inflation:.2f}x")
    print(f"  clusters={rep.clusters}")
    print(f"  singletons (look here)={rep.singletons}")
    print(f"  boilerplate={rep.boilerplate}")

    print("\n=== independent set (expect little/no collapse) ===")
    rep2 = analyze(independent_set, threshold=0.6)
    print(f"  raw={rep2.raw_count}  effective={rep2.effective_count}  inflation={rep2.inflation:.2f}x")

    # discrimination gates
    assert rep.inflation > 1.5, "echo pile did not collapse -- volume laundered as consensus"
    assert "e" in rep.singletons, "dissenter got absorbed into the echo -- the buried voice was lost"
    assert rep2.effective_count == rep2.raw_count, "independent sources wrongly merged"
    print("\ndiscrimination gate passed: echo collapses, independents stay wide, "
          "the dissenting voice survives as a singleton.")
