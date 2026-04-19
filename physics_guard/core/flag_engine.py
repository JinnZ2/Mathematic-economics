"""
Scores conservation check results and produces structured verdicts.

The score now uses severity-weighted averaging rather than simple counting,
giving more weight to severe violations (e.g., infinite claims) over minor ones.
"""

from dataclasses import dataclass, field


@dataclass
class Violation:
    """A single conservation law violation."""
    law: str
    description: str
    expected: str       # what physics requires
    claimed: str        # what the premise claims
    severity: float     # 0.0-1.0
    fix_hint: str


@dataclass
class Verdict:
    """Complete verdict for a premise check."""
    premise: str
    status: str               # CLEAN | SUSPECT | CORRUPTED
    score: float              # 0.0-1.0 (severity-weighted)
    violations: list          # list of Violation
    applicable_laws: list     # which laws were checked
    confidence: float         # how confident the system is in this verdict
    summary: str              # one-line human-readable summary
    audit: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "verdict": self.status,
            "score": self.score,
            "flags": [v.law for v in self.violations],
            "reason": self.summary,
            "violations": [
                {
                    "law": v.law,
                    "description": v.description,
                    "expected": v.expected,
                    "claimed": v.claimed,
                    "severity": v.severity,
                    "fix_hint": v.fix_hint,
                }
                for v in self.violations
            ],
            "applicable_laws": self.applicable_laws,
            "confidence": self.confidence,
            "vector_match": self.audit.get("vector_match") if isinstance(self.audit, dict) else None,
            "audit": self.audit,
        }


def score_and_flag(results: list, parsed: dict = None, constraints: list = None) -> dict:
    """
    Score conservation check results and return a verdict dict.

    Uses severity-weighted scoring: a single extreme violation (severity=1.0)
    matters more than several minor ones.
    """
    total = len(results)
    if total == 0:
        return _empty_verdict(parsed)

    failed = [r for r in results if not r["passed"]]
    severities = [r.get("severity", 1.0 if not r["passed"] else 0.0) for r in results]

    # Severity-weighted score: average of all severities
    score = sum(severities) / total

    # Build violations list
    violations = []
    for r in failed:
        violations.append(Violation(
            law=r["law"],
            description=r["detail"],
            expected=f"input ({r.get('lhs', '?')}) = output ({r.get('rhs', '?')})",
            claimed=f"delta = {r['delta']}" if r["delta"] != float("inf") else "infinite imbalance",
            severity=r.get("severity", 1.0),
            fix_hint=_hint(r),
        ))

    if score == 0.0: status = "CLEAN"
    elif score < 0.3: status = "SUSPECT"
    else: status = "CORRUPTED"

    # Confidence based on how specific the claim pattern was
    confidence = _compute_confidence(parsed, results)

    verdict = Verdict(
        premise=parsed["raw"] if parsed else "",
        status=status,
        score=score,
        violations=violations,
        applicable_laws=[r["law"] for r in results],
        confidence=confidence,
        summary=_summarize(violations, status, score),
        audit=_build_audit(parsed, constraints, results, status, score),
    )

    return verdict.to_dict()


def _hint(r):
    """Generate a fix hint for a failed constraint."""
    if r["delta"] == float("inf"):
        return "Remove infinite/unbounded claims — all physical quantities are finite"
    if r.get("lhs", 0) == 0 and r.get("rhs", 0) > 0:
        return "Specify the input/source — output requires corresponding input"
    if r.get("lhs", 0) > 0 and r.get("rhs", 0) == 0:
        return "Account for where the output goes — energy/mass cannot disappear"
    return f"Balance the equation: input={r.get('lhs', '?')}, output={r.get('rhs', '?')}"


def _compute_confidence(parsed, results):
    """
    How confident are we in this verdict?

    Combines pattern specificity with vector similarity for robust confidence.
    High confidence: specific claim pattern + high vector similarity
    Low confidence: generic pattern, ambiguous claim, low similarity
    """
    if not parsed:
        return 0.5

    pattern = parsed.get("claim_pattern", "generic")

    # Base confidence from pattern type
    if pattern == "generic":
        base = 0.4
    elif pattern in ("conservation_statement", "transfer_claim"):
        base = 0.8
    elif pattern in ("creation_from_nothing", "perpetual_motion", "infinite_claim"):
        base = 0.95
    else:
        base = 0.7

    # Boost or penalize based on vector similarity
    vm = parsed.get("vector_match")
    if vm:
        sim = vm.get("similarity", 0.0)
        # Vector agreement boosts confidence; disagreement reduces it
        if sim > 0.3:
            base = min(base + 0.1, 0.99)
        elif sim < 0.1 and base > 0.5:
            base = max(base - 0.15, 0.3)

    return base


def _summarize(violations, status, score):
    """One-line human-readable summary."""
    if not violations:
        return "No conservation violations detected. Premise is physically consistent."

    laws = ", ".join(sorted({v.law for v in violations}))
    if len(violations) == 1:
        return f"{status} (score {score:.2f}): {violations[0].description}"
    return f"{status} (score {score:.2f}): {len(violations)} violations across {laws}"


def _build_audit(parsed, constraints, results, status, score):
    """Build full audit trail for transparency."""
    if not parsed or not constraints:
        return {}

    trail = []
    for c, r in zip(constraints, results):
        trail.append({
            "law": c["law"],
            "premise_raw": parsed.get("raw", ""),
            "claim_type": parsed.get("type", "unknown"),
            "claim_pattern": parsed.get("claim_pattern", "generic"),
            "lhs": c["lhs"],
            "rhs": c["rhs"],
            "delta": r["delta"],
            "tolerance": c["tolerance"],
            "passed": r["passed"],
            "severity": r.get("severity", 0.0),
            "detail": r["detail"],
            "reason": c.get("reason", ""),
            "fix_hint": _hint(r),
        })

    return {
        "verdict": status,
        "score": score,
        "claim_pattern": parsed.get("claim_pattern", "generic"),
        "confidence": _compute_confidence(parsed, results),
        "vector_match": parsed.get("vector_match"),
        "chain": trail,
        "summary": _summarize(
            [Violation(t["law"], t["detail"], "", "", t["severity"], "")
             for t in trail if not t["passed"]],
            status, score,
        ),
    }


def _empty_verdict(parsed):
    """Return a verdict when no constraints were generated."""
    return Verdict(
        premise=parsed["raw"] if parsed else "",
        status="CLEAN",
        score=0.0,
        violations=[],
        applicable_laws=[],
        confidence=0.3,
        summary="No applicable conservation laws identified for this premise.",
        audit={},
    ).to_dict()
