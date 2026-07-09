"""Claim contract -- machine-checkable mirror of the CLAIM template
declared in `DIFFERENTIAL_FRAME.md` at the repo root.

The frame stipulates that every assertion in this repo is a differential
equation bounded by conditions. This module gives that template a
type-checkable form so structured claim attribution composes with the
rest of the codebase (companions: `field_system_contract.py` for
field_system shapes; `calibration/schema.py` for falsifier-bearing
diagnostics).

Adopt incrementally: existing modules that already encode this frame
through their structure (dataclass fields with units, falsifier strings
in `calibration/`, scope blocks in `study_scope_audit`) need not be
refactored. Use this when a new model wants the explicit, validated form.

Scope of stability:
    - Claim, ClaimBounds, CycleClass: stable field names and types.
    - CanonStatus, Confidence, Graduation (added in 1.1.0): stable
      field names and enum values; new enum members bump minor.
    - Validation rules: every required list field must be non-empty;
      bounds must have all three sub-fields; cycle_class must match
      the enum; canon_status in {FRONTIER, REVOLUTIONARY} forces a
      graduation with non-empty justification, provenance, and tests.

Versioning: breaking changes to field names, types, or required-ness
bump major. Adding fields with backward-compatible defaults bumps minor.

Dependencies: stdlib only.
License: CC0 1.0 Universal.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


CONTRACT_VERSION = "1.1.0"


class CycleClass(str, Enum):
    """The temporal class of the rate equation. Determines how
    permanence-shaped the curve looks under casual observation:
    century-scale curves can be misread as permanence."""

    DAY = "day"
    SEASON = "season"
    GENERATION = "generation"
    CENTURY = "century"
    GEOLOGIC = "geologic"


class CanonStatus(str, Enum):
    """Epistemological placement of a claim relative to accepted canon.
    Ordered from most-established to most-divergent.

    MAINSTREAM   -- accepted canon, textbook-supported. Default for
                    the 13 canonical equations that measure via
                    published data sources.
    EMERGING     -- physics-consistent, well-supported by recent
                    empirical work, not yet in mainstream textbooks.
    CONTESTED    -- physics-consistent, empirically debated. Reasonable
                    people disagree given the same evidence.
    FRONTIER     -- physics-consistent, novel mechanism with sparse
                    empirical support. Requires a graduation.
    REVOLUTIONARY-- proposes a mechanism outside or against current
                    physics. Requires a graduation with the highest
                    provenance bar (must document why the physics
                    departure is warranted).

    FRONTIER and REVOLUTIONARY claims are structurally unable to be
    constructed without a `graduation` payload; see `Graduation` and
    `Claim.__post_init__`."""

    MAINSTREAM = "mainstream"
    EMERGING = "emerging"
    CONTESTED = "contested"
    FRONTIER = "frontier"
    REVOLUTIONARY = "revolutionary"


class Confidence(str, Enum):
    """Analyst's degree of belief that the claim holds within its
    declared bounds. Not a probability; not a substitute for the
    falsifier. Useful for prioritization (which claim to test first,
    which to weight when acting under uncertainty). A high-confidence
    claim still requires testing; the confidence just says how
    surprised the analyst would be by refutation.

    UNVERIFIED -- confidence not declared / claim not yet checked.
                  Default for a fresh Claim.
    LOW        -- author suspects the claim holds but has weak evidence.
    MEDIUM     -- multiple lines of evidence converge; no single
                  decisive test yet.
    HIGH       -- strong convergent evidence; a refutation would be
                  surprising.

    Quantitative bounds (lo/hi ranges, standard errors) belong in
    module-specific dataclasses (e.g. `CorpusShareEstimate.confidence:
    float`, `forensic_eroi.Stage.e_lo/e_hi`). This ordinal field is a
    coarse belief indicator that composes with those quantitative
    bounds rather than replacing them."""

    UNVERIFIED = "unverified"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ClaimBounds:
    """Where, when, and at what resolution a claim's rate equation holds.

    All three are required: a claim with one missing bound is incomplete
    and a downstream consumer should refuse to pin to it.
    """

    spatial: str   # where the equation holds
    temporal: str  # which cycle / time horizon
    scale: str     # resolution at which dX/dt is measured


@dataclass(frozen=True)
class Graduation:
    """Path from novel-claim status to validated. Required for claims
    with `canon_status in {FRONTIER, REVOLUTIONARY}`.

    Fields:
        justification -- WHY this claim, despite canon divergence.
                         Free text; must be non-empty and substantive.
        provenance    -- WHERE the evidence comes from. List of sources,
                         prior work, empirical anchors. Must be non-empty.
        passing_tests -- HOW the claim is checked. List of test
                         identifiers (module paths, test-function names,
                         URIs) that MUST currently pass for the claim
                         to be validated. Must be non-empty.
        validated     -- Promotion state. Defaults to False. Set to True
                         ONLY by an external process that has verified
                         all `passing_tests` currently pass. The analyst
                         cannot self-validate; that is the load-bearing
                         property of the graduation contract.

    Semantics:
        graduation.validated=False + claim.canon_status=REVOLUTIONARY:
            claim is proposed but has not yet earned the right to be
            treated as a working assumption by downstream consumers.
        graduation.validated=True:
            an external process ran the tests and they passed at
            promotion time. Downstream consumers may treat the claim
            like an EMERGING claim, subject to the standard falsifier.
        The graduation payload does NOT downgrade validation logic
        elsewhere: an unvalidated revolutionary claim can still be
        tested. Graduation controls presentation and downstream trust,
        not the falsifiability check."""

    justification: str
    provenance: List[str]
    passing_tests: List[str]
    validated: bool = False

    def __post_init__(self) -> None:
        if not self.justification.strip():
            raise ValueError(
                "Graduation.justification must be non-empty. FRONTIER "
                "and REVOLUTIONARY claims must document why they warrant "
                "canon divergence."
            )
        if not self.provenance:
            raise ValueError(
                "Graduation.provenance must list at least one source. "
                "A claim without provenance cannot be graduated."
            )
        if not self.passing_tests:
            raise ValueError(
                "Graduation.passing_tests must list at least one test "
                "identifier. A claim without a runnable test cannot be "
                "graduated."
            )


@dataclass(frozen=True)
class Claim:
    """Structured form of an assertion in this repo.

    Required (non-empty):
        observable, rate_equation, bounds, conditions, invalid_if,
        measured_by, cycle_class.

    Optional (added in 1.1.0, backward-compatible):
        canon_status  -- epistemological placement. None means
                         unspecified; MAINSTREAM should be explicit.
        graduation    -- required iff canon_status is FRONTIER or
                         REVOLUTIONARY. Ignored otherwise.
        confidence    -- analyst's ordinal belief. None means
                         unspecified; UNVERIFIED is the explicit
                         "not yet checked" state.

        relational_web -- a leaf claim with no documented couplings is
                          still well-formed; keep the field but allow empty.
    """

    observable: str
    rate_equation: str
    bounds: ClaimBounds
    conditions: List[str]
    invalid_if: List[str]
    measured_by: List[str]
    cycle_class: CycleClass
    relational_web: List[str] = field(default_factory=list)
    canon_status: Optional[CanonStatus] = None
    graduation: Optional[Graduation] = None
    confidence: Optional[Confidence] = None

    def __post_init__(self) -> None:
        if not self.observable:
            raise ValueError("Claim.observable must be non-empty")
        if not self.rate_equation:
            raise ValueError("Claim.rate_equation must be non-empty")
        if not self.conditions:
            raise ValueError("Claim.conditions must list at least one condition")
        if not self.invalid_if:
            raise ValueError("Claim.invalid_if must list at least one falsifying boundary")
        if not self.measured_by:
            raise ValueError("Claim.measured_by must list at least one observable signal")

        # canon-status <-> graduation coherence check
        needs_graduation = self.canon_status in {
            CanonStatus.FRONTIER,
            CanonStatus.REVOLUTIONARY,
        }
        if needs_graduation and self.graduation is None:
            raise ValueError(
                f"Claim.canon_status={self.canon_status.value} requires a "
                f"Graduation object with non-empty justification, provenance, "
                f"and passing_tests."
            )
        if not needs_graduation and self.graduation is not None:
            # A graduation on a MAINSTREAM/EMERGING/CONTESTED claim is not
            # forbidden -- it's harmless documentation. But surface a
            # gentle note in the coherent case: if canon_status is None
            # or MAINSTREAM but a graduation is attached, the author
            # probably meant to declare FRONTIER/REVOLUTIONARY.
            # We warn softly by not raising; consumers can inspect.
            pass

    def is_validated(self) -> bool:
        """True if the claim is treated as a working assumption downstream.

        Rules:
            - MAINSTREAM (or unspecified) claims are validated by
              construction; they inherit canon.
            - EMERGING and CONTESTED claims are validated (their
              standard falsifier is the check).
            - FRONTIER and REVOLUTIONARY claims are validated only if
              `graduation.validated` is True -- meaning an external
              process ran the tests and confirmed they passed.
        """
        if self.canon_status is None:
            return True
        if self.canon_status == CanonStatus.MAINSTREAM:
            return True
        if self.canon_status in {CanonStatus.EMERGING, CanonStatus.CONTESTED}:
            return True
        # FRONTIER or REVOLUTIONARY
        assert self.graduation is not None  # enforced by __post_init__
        return self.graduation.validated

    def needs_graduation(self) -> bool:
        """True if the canon_status structurally requires a graduation."""
        return self.canon_status in {
            CanonStatus.FRONTIER,
            CanonStatus.REVOLUTIONARY,
        }

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["cycle_class"] = self.cycle_class.value
        if self.canon_status is not None:
            d["canon_status"] = self.canon_status.value
        if self.confidence is not None:
            d["confidence"] = self.confidence.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Claim":
        bounds_data = data["bounds"]
        canon_raw = data.get("canon_status")
        confidence_raw = data.get("confidence")
        graduation_raw = data.get("graduation")
        return cls(
            observable=str(data["observable"]),
            rate_equation=str(data["rate_equation"]),
            bounds=ClaimBounds(
                spatial=str(bounds_data["spatial"]),
                temporal=str(bounds_data["temporal"]),
                scale=str(bounds_data["scale"]),
            ),
            conditions=list(data["conditions"]),
            invalid_if=list(data["invalid_if"]),
            measured_by=list(data["measured_by"]),
            cycle_class=CycleClass(data["cycle_class"]),
            relational_web=list(data.get("relational_web", [])),
            canon_status=(
                CanonStatus(canon_raw) if canon_raw is not None else None
            ),
            graduation=(
                Graduation(
                    justification=str(graduation_raw["justification"]),
                    provenance=list(graduation_raw["provenance"]),
                    passing_tests=list(graduation_raw["passing_tests"]),
                    validated=bool(graduation_raw.get("validated", False)),
                )
                if graduation_raw is not None
                else None
            ),
            confidence=(
                Confidence(confidence_raw)
                if confidence_raw is not None
                else None
            ),
        )
