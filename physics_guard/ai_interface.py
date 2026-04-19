"""
PhysicsGuard — Safe unified AI entry point.

One function, `audit()`, that any AI client can call without needing to
know which internal module handles which claim type. Auto-routes based
on input shape, catches all exceptions at the boundary, and returns a
single normalized JSON schema regardless of which pipeline ran.

## Usage

    from ai_interface import audit

    audit("Energy can be created from nothing")
    audit(["doc 1", "doc 2", "doc 3"])                    # monoculture
    audit({"domain": "organizational", ...})              # org claim
    audit({"domain": "information", ...})                 # info claim
    audit({"domain": "thermodynamic", ...})               # TAF claim
    audit(x, mode="premise")                              # force a mode

## Output schema (always the same shape)

    {
        "mode":           "premise" | "batch" | "corpus" |
                          "organizational" | "information" |
                          "thermodynamic" | "error",
        "verdict":        "CLEAN" | "SUSPECT" | "CORRUPTED" | "ERROR",
        "native_verdict": original module-specific verdict string,
        "score":          float in [0, 1] (higher = worse),
        "flags":          list of flag strings,
        "summary":        single-sentence human-readable summary,
        "details":        full module-specific output (for introspection),
        "error":          None, or error message string if mode == "error",
    }

## Verdict normalization

Different modules return different native verdicts. `verdict` normalizes
them into one vocabulary so callers don't have to branch:

    CLEAN     <- CLEAN  (core/domains)    <- GREEN  (monoculture)
    SUSPECT   <- SUSPECT                  <- YELLOW
    CORRUPTED <- CORRUPTED                <- RED
    ERROR                                                 (boundary failure)

CC0 — github.com/JinnZ2/physicsguard
"""

from __future__ import annotations

from typing import Any

from main import check, check_batch

_NATIVE_TO_NORMAL = {
    "CLEAN":     "CLEAN",
    "SUSPECT":   "SUSPECT",
    "CORRUPTED": "CORRUPTED",
    "GREEN":     "CLEAN",
    "YELLOW":    "SUSPECT",
    "RED":       "CORRUPTED",
}

_VALID_MODES = {
    "auto", "premise", "batch", "corpus",
    "organizational", "information", "thermodynamic",
}


def audit(input: Any, mode: str = "auto") -> dict:
    """Single safe entry point for AI clients. Never raises."""
    try:
        if mode not in _VALID_MODES:
            return _error(f"unknown mode {mode!r}; valid: {sorted(_VALID_MODES)}")

        if mode == "auto":
            mode = _detect_mode(input)

        if mode == "premise":        return _audit_premise(input)
        if mode == "batch":          return _audit_batch(input)
        if mode == "corpus":         return _audit_corpus(input)
        if mode == "organizational": return _audit_organizational(input)
        if mode == "information":    return _audit_information(input)
        if mode == "thermodynamic":  return _audit_thermodynamic(input)

        return _error(f"no handler for mode {mode!r}")
    except Exception as e:  # last-resort boundary catch
        return _error(f"{type(e).__name__}: {e}")


# -- Auto-detection ------------------------------------------------------------

def _detect_mode(input: Any) -> str:
    if isinstance(input, str):
        return "premise"
    if isinstance(input, list):
        if not input:
            return "corpus"
        if all(isinstance(x, str) for x in input):
            return "corpus" if len(input) > 1 else "premise"
        raise TypeError("list inputs must contain strings")
    if isinstance(input, dict):
        domain = input.get("domain", "").lower()
        if domain in {"organizational", "information", "thermodynamic"}:
            return domain
        raise TypeError(
            "dict inputs must include 'domain': "
            "'organizational', 'information', or 'thermodynamic'"
        )
    raise TypeError(f"unsupported input type: {type(input).__name__}")


# -- Mode handlers -------------------------------------------------------------

def _audit_premise(input: Any) -> dict:
    if isinstance(input, list) and len(input) == 1:
        input = input[0]
    if not isinstance(input, str):
        return _error("premise mode requires a string input")
    result = check(input)
    return _envelope(
        mode="premise",
        native_verdict=result["verdict"],
        score=result["score"],
        flags=result["flags"],
        summary=result.get("reason", ""),
        details=result,
    )


def _audit_batch(input: Any) -> dict:
    if not isinstance(input, list) or not all(isinstance(x, str) for x in input):
        return _error("batch mode requires a list of strings")
    results = check_batch(input)
    worst = _worst_verdict([r["verdict"] for r in results])
    score = max((r["score"] for r in results), default=0.0)
    flags = sorted({f for r in results for f in r["flags"]})
    return _envelope(
        mode="batch",
        native_verdict=worst,
        score=score,
        flags=flags,
        summary=f"{len(results)} premises checked; worst verdict {worst}.",
        details={"results": results},
    )


def _audit_corpus(input: Any) -> dict:
    if not isinstance(input, list) or not all(isinstance(x, str) for x in input):
        return _error("corpus mode requires a list of strings")
    from monoculture_detector import MonocultureDetector
    report = MonocultureDetector().audit(input)
    red = [a.name for a in report.axes if a.status == "RED"]
    yellow = [a.name for a in report.axes if a.status == "YELLOW"]
    score = _corpus_score(report.overall_status)
    return _envelope(
        mode="corpus",
        native_verdict=report.overall_status,
        score=score,
        flags=red + yellow,
        summary=report.summary,
        details=report.to_dict(),
    )


def _audit_organizational(input: Any) -> dict:
    from domains.organizational import OrgClaim, check_organization
    claim = _build_claim(input, OrgClaim, required={"raw"})
    result = check_organization(claim)
    return _envelope(
        mode="organizational",
        native_verdict=result.verdict,
        score=len(result.flags) / max(len(result.audit), 1),
        flags=result.flags,
        summary=_summarize_domain(result.verdict, result.flags),
        details={
            "verdict": result.verdict,
            "flags": result.flags,
            "resilience_score": result.resilience_score,
            "enforcement_waste": result.enforcement_waste,
            "cascade_risk": result.cascade_risk,
            "audit": result.audit,
        },
    )


def _audit_information(input: Any) -> dict:
    from domains.information import InfoClaim, check_information
    claim = _build_claim(input, InfoClaim, required={"raw", "claim_type"})
    result = check_information(claim)
    return _envelope(
        mode="information",
        native_verdict=result.verdict,
        score=len(result.flags) / max(len(result.audit), 1),
        flags=result.flags,
        summary=_summarize_domain(result.verdict, result.flags),
        details={
            "verdict": result.verdict,
            "flags": result.flags,
            "audit": result.audit,
        },
    )


def _audit_thermodynamic(input: Any) -> dict:
    from domains.thermodynamic_accountability import (
        TAFClaim,
        check_thermodynamic_accountability,
    )
    claim = _build_claim(input, TAFClaim, required={"raw"})
    result = check_thermodynamic_accountability(claim)
    return _envelope(
        mode="thermodynamic",
        native_verdict=result.verdict,
        score=len(result.flags) / max(len(result.audit), 1),
        flags=result.flags,
        summary=_summarize_domain(result.verdict, result.flags),
        details={
            "verdict": result.verdict,
            "flags": result.flags,
            "net_yield": result.net_yield,
            "friction_ratio": result.friction_ratio,
            "load_factor": result.load_factor,
            "distance_to_collapse": result.distance_to_collapse,
            "energy_debt": result.energy_debt,
            "audit": result.audit,
        },
    )


# -- Helpers -------------------------------------------------------------------

def _build_claim(input: dict, cls, required: set):
    """Instantiate a dataclass from a dict, ignoring the 'domain' key and
    any unknown fields; raise if required fields are missing."""
    if not isinstance(input, dict):
        raise TypeError(f"{cls.__name__} input must be a dict")
    missing = required - input.keys()
    if missing:
        raise ValueError(f"{cls.__name__} missing required fields: {sorted(missing)}")
    allowed = {f for f in cls.__dataclass_fields__}
    kwargs = {k: v for k, v in input.items() if k in allowed}
    return cls(**kwargs)


def _envelope(mode, native_verdict, score, flags, summary, details) -> dict:
    return {
        "mode":           mode,
        "verdict":        _NATIVE_TO_NORMAL.get(native_verdict, "ERROR"),
        "native_verdict": native_verdict,
        "score":          float(min(max(score, 0.0), 1.0)),
        "flags":          list(flags),
        "summary":        summary,
        "details":        details,
        "error":          None,
    }


def _error(msg: str) -> dict:
    return {
        "mode":           "error",
        "verdict":        "ERROR",
        "native_verdict": "ERROR",
        "score":          0.0,
        "flags":          [],
        "summary":        msg,
        "details":        {},
        "error":          msg,
    }


def _worst_verdict(verdicts: list) -> str:
    rank = {"CLEAN": 0, "GREEN": 0, "SUSPECT": 1, "YELLOW": 1, "CORRUPTED": 2, "RED": 2}
    if not verdicts:
        return "CLEAN"
    return max(verdicts, key=lambda v: rank.get(v, -1))


def _corpus_score(status: str) -> float:
    return {"GREEN": 0.0, "YELLOW": 0.5, "RED": 1.0}.get(status, 0.0)


def _summarize_domain(verdict: str, flags: list) -> str:
    if verdict == "CLEAN":
        return "No violations detected."
    if verdict == "SUSPECT":
        return f"Minor concerns: {', '.join(flags)}."
    return f"Constraint violations: {', '.join(flags)}."
