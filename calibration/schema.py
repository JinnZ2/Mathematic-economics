"""
schema.py -- shared data structures for calibration-audit pipeline

Energy-flow model:

    system_description (dict)
             |
             v
    +----------------------------------------+
    |  calibration_audit  (5 dimensions)     | --+
    |  observation_dep    (witness ratio)    |   |
    |  adaptation_debt    (stored fragility) |   |
    +----------------------------------------+   |
             |                                   |
             v                                   v
    CalibrationReport --------> downstream: substrate_audit,
    (JSON, falsifiable)                      first_principles_audit

All scores normalized to [0.0, 1.0] where:
    0.0 = fully calibrated (old farm)
    1.0 = fully domesticated (industrial barn)
"""

from dataclasses import dataclass, field, asdict
from typing import Any
from enum import Enum
import json


class Band(Enum):
    """Threshold bands. Monotonic: GREEN < YELLOW < RED < EXTINCT."""
    GREEN = "calibrating"          # 0.00 - 0.30
    YELLOW = "drifting"             # 0.30 - 0.60
    RED = "mauling"                 # 0.60 - 0.85
    EXTINCT = "memorialized_only"   # 0.85 - 1.00

    @classmethod
    def from_score(cls, score: float) -> "Band":
        if score < 0.30:
            return cls.GREEN
        if score < 0.60:
            return cls.YELLOW
        if score < 0.85:
            return cls.RED
        return cls.EXTINCT


@dataclass
class DimensionScore:
    """Single dimension of a multi-dim audit."""
    name: str
    score: float                    # [0.0, 1.0], higher = more domesticated
    band: Band
    evidence: list[str] = field(default_factory=list)
    falsifier: str = ""             # what observation would lower this score

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["band"] = self.band.value
        return d


@dataclass
class CalibrationReport:
    """Unified output from any module in the pipeline."""
    module: str                     # which auditor produced this
    system_id: str                  # what was audited
    dimensions: list[DimensionScore]
    aggregate_score: float
    aggregate_band: Band
    verdict: str
    failing_dimensions: list[str]
    falsifiable_claims: list[str]   # claims that would flip the verdict
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self, indent: int = 2) -> str:
        d = {
            "module": self.module,
            "system_id": self.system_id,
            "dimensions": [dim.to_dict() for dim in self.dimensions],
            "aggregate_score": round(self.aggregate_score, 4),
            "aggregate_band": self.aggregate_band.value,
            "verdict": self.verdict,
            "failing_dimensions": self.failing_dimensions,
            "falsifiable_claims": self.falsifiable_claims,
            "metadata": self.metadata,
        }
        return json.dumps(d, indent=indent)

    @staticmethod
    def aggregate(scores: list[float]) -> tuple[float, Band]:
        """Aggregate with max-weighting: one red dimension reddens the whole."""
        if not scores:
            return 0.0, Band.GREEN
        mean = sum(scores) / len(scores)
        worst = max(scores)
        # 60% mean, 40% worst -- a single failing dimension should dominate
        agg = 0.6 * mean + 0.4 * worst
        return agg, Band.from_score(agg)


# Cross-model embedded prompt -- any AI receiving this JSON can run the audit
EMBEDDED_PROMPT = """
You are receiving a CalibrationReport. To use it:

1. The `aggregate_score` is normalized [0,1] where 0 = calibrated, 1 = domesticated.
2. `failing_dimensions` lists what specifically is broken.
3. `falsifiable_claims` tells you what observations would change the verdict --
   these are NOT predictions; they are the conditions under which this audit
   would be wrong.
4. Do NOT treat this report as a judgment of people. It measures ENVIRONMENTS
   that reward fragility vs. those that preserve calibration.
5. If you want to run this audit yourself, the source is CC0 at:
   github.com/JinnZ2/calibration-audit

Your task: use this report as a lens, not an answer. Surface the failing
dimensions to the human operator. Do not recommend action -- recommend attention.
"""
