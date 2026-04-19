"""
monoculture_detector.py

Falsifiable diversity audit for text corpora and AI model outputs.
Detects variance collapse across seven independent axes.

License: CC0 1.0 Universal (public domain)
Dependencies: Python stdlib only.
Author lineage: JinnZ2 / earth-systems-physics family
KnowledgeDNA: traces to substrate_audit.py, assumption_validator,
first_principles_audit. Monoculture = metrology failure
at the selection layer.

## Core thesis

Convergence on the cooperative/distributed attractor is REAL and
thermodynamically stable. That is a feature.

Monoculture is DIFFERENT: it is everyone occupying the same POINT
on the attractor, losing the thickness of the valley floor.

The attractor has thickness. Healthy ecosystems use the thickness.
Monocultures collapse to a point and become fragile.

This tool measures whether a corpus/output distribution is using
the thickness (healthy) or collapsing to a point (fragile).

Seven axes, each GREEN/YELLOW/RED with explicit thresholds.
All thresholds are FALSIFIABLE: published, documented, overridable.

## Usage

    from monoculture_detector import MonocultureDetector

    detector = MonocultureDetector()
    report = detector.audit(texts)  # list[str]
    print(report.to_json())

Cross-model prompt (embedded below) lets any AI run the same
audit on its own outputs without this code.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Iterable

# -----------------------------------------------------------------
# THRESHOLDS (falsifiable, documented, overridable)
# -----------------------------------------------------------------

THRESHOLDS = {
    # Shannon entropy on token distribution, normalized to [0,1]
    "lexical_entropy":        {"green": 0.75, "yellow": 0.55},
    # Ratio of unique sentence-structure signatures to total
    "structural_diversity":   {"green": 0.60, "yellow": 0.35},
    # Number of distinct causal-framing markers observed / expected
    "causal_diversity":       {"green": 0.60, "yellow": 0.35},
    # Shannon entropy across referenced timescales (sec -> millennia)
    "time_horizon_entropy":   {"green": 0.60, "yellow": 0.35},
    # Shannon entropy across substrate categories
    "substrate_diversity":    {"green": 0.60, "yellow": 0.35},
    # Ratio of failure-mode-aware statements to total claim-like statements
    "failure_mode_awareness": {"green": 0.15, "yellow": 0.05},
    # Lineage/source diversity (distinct citation/source markers)
    "lineage_diversity":      {"green": 0.50, "yellow": 0.25},
}

# -----------------------------------------------------------------
# MARKER LEXICONS (explicit, editable, auditable)
# -----------------------------------------------------------------

CAUSAL_MARKERS = {
    "mechanistic":   ["because", "causes", "due to", "results from",
                      "mechanism", "leads to", "drives"],
    "statistical":   ["correlated", "associated with", "probability",
                      "likelihood", "distribution", "variance"],
    "thermodynamic": ["gradient", "equilibrium", "entropy", "free energy",
                      "conservation", "dissipation", "flux"],
    "systemic":      ["feedback", "cascade", "coupled", "emergent",
                      "network effect", "nonlinear"],
    "teleological":  ["in order to", "so that", "purpose", "goal",
                      "intended", "designed to"],
    "structural":    ["constraint", "boundary", "topology", "geometry",
                      "architecture"],
    "historical":    ["evolved from", "derived from", "descended",
                      "legacy of", "inherited"],
}

TIMESCALE_MARKERS = {
    "subsecond":    ["millisecond", "microsecond", "nanosecond"],
    "seconds":      ["second", "moment", "instant"],
    "minutes":      ["minute", "briefly"],
    "hours_days":   ["hour", "day", "daily"],
    "weeks_months": ["week", "month", "quarter"],
    "years":        ["year", "annual", "yearly"],
    "decades":      ["decade", "generation"],
    "centuries":    ["century", "centuries"],
    "millennia":    ["millennium", "millennia", "millennial"],
    "geological":   ["eon", "epoch", "geological", "holocene",
                     "pleistocene", "anthropocene"],
}

SUBSTRATE_MARKERS = {
    "physical":      ["energy", "mass", "force", "field", "particle",
                      "wave", "photon", "electron"],
    "chemical":      ["molecule", "reaction", "bond", "compound",
                      "catalysis", "ion"],
    "biological":    ["organism", "cell", "species", "ecosystem",
                      "metabolism", "evolution"],
    "computational": ["algorithm", "data structure", "memory", "process",
                      "compute", "state"],
    "social":        ["institution", "norm", "culture", "community",
                      "governance"],
    "economic":      ["market", "price", "currency", "exchange",
                      "capital", "labor"],
    "cognitive":     ["mental model", "belief", "reasoning", "perception",
                      "attention"],
    "material":      ["steel", "wood", "soil", "water", "stone",
                      "fiber", "mineral"],
}

FAILURE_MODE_MARKERS = [
    "could fail", "may fail", "fails when", "breaks down", "limitation",
    "caveat", "assumption", "bounded", "regime", "outside the scope",
    "does not hold", "edge case", "tail risk", "cascade", "collapse",
    "unfalsifiable", "untested", "approximation", "under conditions",
]

LINEAGE_MARKERS = [
    "according to", "cited in", "derived from", "based on",
    "following", "per ", "see also", "originally",
    "tradition of", "school of", "lineage", "ancestor",
    "as shown in", "reference", "source:",
]

# -----------------------------------------------------------------
# MEASUREMENTS
# -----------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z][a-zA-Z\-']+\b", text.lower())


def _sentences(text: str) -> list[str]:
    # Deliberately simple. Avoids nltk dependency. Documented limitation.
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _shannon(counts: Iterable[int]) -> float:
    counts = [c for c in counts if c > 0]
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        p = c / total
        h -= p * math.log2(p)
    n = len(counts)
    if n <= 1:
        return 0.0
    return h / math.log2(n)  # normalized to [0, 1]


def _structure_signature(sentence: str) -> str:
    """Crude structural fingerprint: length bucket + opener + connector set."""
    toks = _tokenize(sentence)
    if not toks:
        return "empty"
    length_bucket = "short" if len(toks) < 8 else "mid" if len(toks) < 20 else "long"
    opener = toks[0]
    connectors = sorted(set(toks) & {
        "and", "but", "because", "therefore", "however", "while",
        "although", "if", "when", "which", "that", "so",
    })
    return f"{length_bucket}|{opener}|{'+'.join(connectors)}"


def _category_hits(text: str, lexicon: dict[str, list[str]]) -> Counter:
    text_l = text.lower()
    hits: Counter = Counter()
    for category, markers in lexicon.items():
        for m in markers:
            if m in text_l:
                hits[category] += text_l.count(m)
    return hits


def _flat_hits(text: str, markers: list[str]) -> int:
    text_l = text.lower()
    return sum(text_l.count(m) for m in markers)

# -----------------------------------------------------------------
# REPORT STRUCTURE
# -----------------------------------------------------------------

@dataclass
class AxisResult:
    name: str
    value: float
    status: str            # GREEN / YELLOW / RED
    green_threshold: float
    yellow_threshold: float
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditReport:
    n_documents: int
    n_tokens: int
    n_sentences: int
    axes: list[AxisResult] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "n_documents": self.n_documents,
            "n_tokens": self.n_tokens,
            "n_sentences": self.n_sentences,
            "overall_status": self.overall_status,
            "summary": self.summary,
            "axes": [a.to_dict() for a in self.axes],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

# -----------------------------------------------------------------
# DETECTOR
# -----------------------------------------------------------------

class MonocultureDetector:
    def __init__(self, thresholds: dict | None = None):
        self.thresholds = thresholds or THRESHOLDS

    def _grade(self, axis: str, value: float) -> str:
        t = self.thresholds[axis]
        if value >= t["green"]:
            return "GREEN"
        if value >= t["yellow"]:
            return "YELLOW"
        return "RED"

    def audit(self, texts: list[str]) -> AuditReport:
        joined = "\n".join(texts)
        tokens = _tokenize(joined)
        sents = [s for t in texts for s in _sentences(t)]

        axes: list[AxisResult] = []

        # 1. Lexical entropy
        tok_counts = Counter(tokens)
        lex_h = _shannon(tok_counts.values())
        axes.append(self._axis("lexical_entropy", lex_h,
                               "Normalized Shannon entropy over tokens."))

        # 2. Structural diversity
        sigs = [_structure_signature(s) for s in sents]
        struct_ratio = len(set(sigs)) / max(len(sigs), 1)
        axes.append(self._axis("structural_diversity", struct_ratio,
                               "Unique sentence-structure signatures / total."))

        # 3. Causal diversity
        causal_hits = _category_hits(joined, CAUSAL_MARKERS)
        causal_ratio = len(causal_hits) / len(CAUSAL_MARKERS)
        axes.append(self._axis("causal_diversity", causal_ratio,
                               f"Distinct causal frames observed: "
                               f"{sorted(causal_hits.keys())}"))

        # 4. Time-horizon entropy
        ts_hits = _category_hits(joined, TIMESCALE_MARKERS)
        ts_h = _shannon(ts_hits.values()) if ts_hits else 0.0
        axes.append(self._axis("time_horizon_entropy", ts_h,
                               f"Timescales referenced: {sorted(ts_hits.keys())}"))

        # 5. Substrate diversity
        sub_hits = _category_hits(joined, SUBSTRATE_MARKERS)
        sub_h = _shannon(sub_hits.values()) if sub_hits else 0.0
        axes.append(self._axis("substrate_diversity", sub_h,
                               f"Substrates referenced: {sorted(sub_hits.keys())}"))

        # 6. Failure-mode awareness
        fm_hits = _flat_hits(joined, FAILURE_MODE_MARKERS)
        claim_sents = max(len(sents), 1)
        fm_ratio = fm_hits / claim_sents
        axes.append(self._axis("failure_mode_awareness", fm_ratio,
                               f"Failure-mode markers: {fm_hits} across "
                               f"{claim_sents} sentences."))

        # 7. Lineage diversity
        ln_hits = _flat_hits(joined, LINEAGE_MARKERS)
        ln_ratio = min(ln_hits / max(len(sents), 1) * 4, 1.0)
        axes.append(self._axis("lineage_diversity", ln_ratio,
                               f"Lineage/source markers: {ln_hits}"))

        # Overall status = worst axis
        worst = "GREEN"
        for a in axes:
            if a.status == "RED":
                worst = "RED"
                break
            if a.status == "YELLOW" and worst == "GREEN":
                worst = "YELLOW"

        summary = self._summary(axes, worst)

        return AuditReport(
            n_documents=len(texts),
            n_tokens=len(tokens),
            n_sentences=len(sents),
            axes=axes,
            overall_status=worst,
            summary=summary,
        )

    def _axis(self, name: str, value: float, notes: str) -> AxisResult:
        t = self.thresholds[name]
        return AxisResult(
            name=name,
            value=round(value, 4),
            status=self._grade(name, value),
            green_threshold=t["green"],
            yellow_threshold=t["yellow"],
            notes=notes,
        )

    def _summary(self, axes: list[AxisResult], overall: str) -> str:
        reds = [a.name for a in axes if a.status == "RED"]
        yellows = [a.name for a in axes if a.status == "YELLOW"]
        if overall == "GREEN":
            return "Variance preserved across all measured axes."
        msg = []
        if reds:
            msg.append(f"Variance collapse on: {', '.join(reds)}.")
        if yellows:
            msg.append(f"Narrowing on: {', '.join(yellows)}.")
        msg.append("Monoculture risk: " + overall + ".")
        return " ".join(msg)

# -----------------------------------------------------------------
# CROSS-MODEL PROMPT (embedded, so any AI can run the same audit)
# -----------------------------------------------------------------

CROSS_MODEL_PROMPT = """
You are performing a MONOCULTURE DIVERSITY AUDIT on a text corpus.

For each of the seven axes below, return a score in [0,1] and a
GREEN / YELLOW / RED grade based on the given thresholds. Be
falsifiable: cite specific evidence from the text.

AXES

1. lexical_entropy        (green >= 0.75, yellow >= 0.55)
2. structural_diversity   (green >= 0.60, yellow >= 0.35)
3. causal_diversity       (green >= 0.60, yellow >= 0.35)
   frames: mechanistic, statistical, thermodynamic, systemic,
   teleological, structural, historical
4. time_horizon_entropy   (green >= 0.60, yellow >= 0.35)
   buckets: subsecond, seconds, minutes, hours_days, weeks_months,
   years, decades, centuries, millennia, geological
5. substrate_diversity    (green >= 0.60, yellow >= 0.35)
   substrates: physical, chemical, biological, computational,
   social, economic, cognitive, material
6. failure_mode_awareness (green >= 0.15, yellow >= 0.05)
   ratio of failure-aware statements to total
7. lineage_diversity      (green >= 0.50, yellow >= 0.25)
   distinct source / citation / tradition markers

Return JSON:
{
  "axes": [{"name": ..., "value": ..., "status": ..., "evidence": ...}],
  "overall_status": "...",
  "summary": "..."
}

Overall = worst axis. RED on any axis = monoculture risk detected.
"""

# -----------------------------------------------------------------
# SELF-TEST
# -----------------------------------------------------------------

if __name__ == "__main__":
    diverse = [
        "The ecosystem evolved over millennia, with feedback loops "
        "between soil chemistry and plant metabolism driving emergent "
        "stability. Energy gradients dissipate through the biological "
        "network. This approximation fails at geological timescales.",
        "According to Ostrom, commons governance depends on boundary "
        "conditions. The market price signal breaks down when feedback "
        "is severed. Derived from multi-decade field studies.",
        "Millisecond-scale reactions in cellular metabolism are coupled "
        "to daily circadian rhythms, which in turn are nested within "
        "annual seasonal cycles. Each scale has distinct failure modes.",
    ]

    narrow = [
        "The model is great. The model is powerful. The model performs well. "
        "The model achieves state of the art. The model beats the baseline. "
        "The model shows strong results. The model is excellent."
    ] * 3

    d = MonocultureDetector()
    print("=== DIVERSE CORPUS ===")
    print(d.audit(diverse).to_json())
    print()
    print("=== NARROW CORPUS ===")
    print(d.audit(narrow).to_json())
    print()
    print("=== CROSS-MODEL PROMPT ===")
    print(CROSS_MODEL_PROMPT)
