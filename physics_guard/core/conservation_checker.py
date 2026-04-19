"""
Validates conservation constraints by computing actual deltas.

With the new constraint mapper, lhs and rhs represent real physical quantities.
When they differ, the delta measures the magnitude of the violation.
"""

import math


def check_conservation(constraints: list) -> list:
    """Check each constraint for conservation violations."""
    results = []
    for c in constraints:
        lhs = c["lhs"]
        rhs = c["rhs"]

        # Handle infinite claims
        if math.isinf(rhs) or math.isinf(lhs):
            delta = float("inf")
            passed = False
        else:
            delta = abs(lhs - rhs)
            passed = delta <= c["tolerance"]

        severity = _compute_severity(lhs, rhs, delta, c["tolerance"])

        results.append({
            "law": c["law"],
            "passed": passed,
            "delta": delta,
            "severity": severity,
            "lhs": lhs,
            "rhs": rhs,
            "detail": _describe(c, passed, delta),
        })
    return results


def _compute_severity(lhs, rhs, delta, tolerance):
    """
    Compute violation severity on a 0.0-1.0 scale.

    0.0 = no violation (delta within tolerance)
    0.5 = moderate violation
    1.0 = extreme violation (infinite claim or total imbalance)
    """
    if math.isinf(delta):
        return 1.0
    if delta <= tolerance:
        return 0.0

    # Severity scales with how far delta exceeds tolerance,
    # normalized by the magnitude of the quantities involved
    magnitude = max(abs(lhs), abs(rhs), 1.0)
    ratio = delta / magnitude
    # Sigmoid-like curve: rises quickly for small violations, saturates near 1.0
    return min(ratio / (ratio + 0.5), 1.0)


def _describe(c, passed, delta):
    """Generate a human-readable description of the check result."""
    if passed:
        return f"{c['law']}: {c['reason']}"

    if math.isinf(delta):
        return f"{c['law']}: infinite imbalance — {c['reason']}"

    return (
        f"{c['law']}: imbalance delta={delta:.4f} "
        f"(input={c['lhs']:.4f}, output={c['rhs']:.4f}) — {c['reason']}"
    )
