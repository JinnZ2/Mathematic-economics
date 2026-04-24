# compute_paradigm.py
# Alternative-computing scaffolding for Math-Econ.
#
# Two pieces:
#   1. Ternary encoding for Math-Econ's naturally 3-valued state
#      (ThresholdStatus, Coupling, Regime, ScopeStatus, calibration Band,
#      metabolic verdict band). Each encodes to balanced ternary {-1, 0, +1}.
#      The fourth absorbing/unknown state in each enum (UNKNOWN, EXTINCT,
#      BLACK, SCOPE_UNDECLARED) encodes to None.
#
#   2. A compute-paradigm registry so Math-Econ primitives can declare which
#      alternative paradigms they natively support (ternary, stochastic,
#      approximate, etc.). Mirrors the public-API shape of the registry
#      pattern used in the surrounding JinnZ2 ecosystem (SOMS, GtBCB).
#
# Deliberately stdlib-only. No external substrate imports — this module
# describes WHICH primitives could run on WHICH paradigms. Actual
# substrate dispatch (e.g. running annealing on Mandala-Computing or
# octahedral encoding via SOMS) is a separate fieldlink, not wired here.
#
# License: CC0 1.0 Universal

from enum import Enum
from typing import Any, Dict, List, Optional


class ComputeParadigm(Enum):
    """Computational paradigms a Math-Econ primitive can support.

    BINARY is the default everything already supports (standard Python
    floats / ints). The others describe alternative substrates where
    the primitive has a defined, non-trivial encoding.
    """
    BINARY = "binary"              # standard floating-point / int
    TERNARY = "ternary"            # balanced ternary {-1, 0, +1}
    STOCHASTIC = "stochastic"      # Monte Carlo / probabilistic
    APPROXIMATE = "approximate"    # scope-bounded, bounded-error
    OCTAHEDRAL = "octahedral"      # 8-state cell (Mandala-Computing, SOMS)
    ANNEALING = "annealing"        # simulated / quantum annealing
    RESERVOIR = "reservoir"        # reservoir computing (dynamic systems)
    QUANTUM = "quantum"            # superposition-based


# ---------------------------------------------------------------------------
# TIER 1: TERNARY ENCODING
# ---------------------------------------------------------------------------
# Convention: +1 means "most favorable / most certain / above threshold",
# -1 means "least favorable / most extrapolated / below threshold",
# 0 means "balanced / within range / moderate". The fourth absorbing or
# unknown state per enum (UNKNOWN, EXTINCT, BLACK, SCOPE_UNDECLARED)
# encodes to None — ternary arithmetic must skip or special-case these.
# ---------------------------------------------------------------------------

# Keyed by Enum name + member name so this module has no import-time
# dependency on AI/equation_bridge.py, audit/study_scope_audit.py,
# calibration/schema.py, or metabolic_bridge.py. Callers can pass
# either the enum member or its .name string.
_TERNARY_BY_NAME: Dict[str, Dict[str, Optional[int]]] = {
    # AI/equation_bridge.py: ThresholdStatus
    "ThresholdStatus": {
        "ABOVE": +1,    # above threshold = more intense (OSDI direction)
        "WITHIN": 0,
        "BELOW": -1,
        "UNKNOWN": None,
    },
    # audit/study_scope_audit.py: Coupling, Regime, ScopeStatus
    "Coupling": {
        "TIGHT": +1,    # scope-bound / high certainty
        "MODERATE": 0,
        "LOOSE": -1,    # extrapolated / high risk
        "UNKNOWN": None,
    },
    "Regime": {
        "STATIONARY": +1,
        "DRIFTING": 0,
        "NON_STATIONARY": -1,
        "UNKNOWN": None,
    },
    "ScopeStatus": {
        "IN_SCOPE": +1,
        "EDGE_OF_SCOPE": 0,
        "OUT_OF_SCOPE": -1,
        "SCOPE_UNDECLARED": None,
    },
    # calibration/schema.py: Band
    "Band": {
        "GREEN": +1,
        "YELLOW": 0,
        "RED": -1,
        "EXTINCT": None,   # absorbing: memorialized, not on the ternary axis
    },
    # metabolic_bridge.py: sustainable_yield_signal string values
    "VerdictBand": {
        "GREEN": +1,
        "AMBER": 0,
        "RED": -1,
        "BLACK": None,     # absorbing: irreversibility, not "very RED"
    },
}


def encode_ternary(value: Any) -> Optional[int]:
    """Encode a Math-Econ 3+1-valued state to balanced ternary.

    Accepts:
      - An Enum member whose class name is registered in _TERNARY_BY_NAME
        (ThresholdStatus, Coupling, Regime, ScopeStatus, Band).
      - A raw string matching a VerdictBand value ("GREEN", "AMBER",
        "RED", "BLACK") — this is how metabolic_bridge.py ships its
        sustainable_yield_signal.

    Returns {-1, 0, +1} for the three primary states, or None for the
    fourth absorbing/unknown state. Raises ValueError on unrecognized
    input.
    """
    if isinstance(value, Enum):
        cls_name = type(value).__name__
        table = _TERNARY_BY_NAME.get(cls_name)
        if table is None:
            raise ValueError(
                f"no ternary encoding registered for enum {cls_name}; "
                f"extend _TERNARY_BY_NAME or call register_ternary_mapping"
            )
        if value.name not in table:
            raise ValueError(
                f"enum member {cls_name}.{value.name} has no ternary mapping"
            )
        return table[value.name]

    if isinstance(value, str):
        # metabolic_bridge returns raw strings; try the VerdictBand table.
        table = _TERNARY_BY_NAME["VerdictBand"]
        if value in table:
            return table[value]
        raise ValueError(
            f"string {value!r} is not a registered ternary state "
            f"(expected one of {sorted(table.keys())})"
        )

    raise TypeError(
        f"encode_ternary expects an Enum member or a VerdictBand string, "
        f"got {type(value).__name__}"
    )


def register_ternary_mapping(enum_class_name: str,
                             mapping: Dict[str, Optional[int]]) -> None:
    """Register a ternary encoding for an additional enum class by name.

    `mapping` is keyed by Enum member `.name` (not `.value`) and values
    must be in {-1, 0, +1, None}. Callers wiring a new 3+1-valued enum
    should call this from their own module, not import _TERNARY_BY_NAME
    directly.
    """
    for member_name, ternary in mapping.items():
        if ternary not in (-1, 0, 1, None):
            raise ValueError(
                f"{enum_class_name}.{member_name} -> {ternary}: "
                f"ternary value must be -1, 0, +1, or None"
            )
    _TERNARY_BY_NAME[enum_class_name] = dict(mapping)


def weighted_ternary_score(
    entries: List[tuple],
) -> Optional[float]:
    """Aggregate ternary-encoded values with weights to a signed real score.

    `entries` is a list of (ternary_or_None, weight) pairs. Entries with
    None are skipped; their weight is removed from the normalizer so the
    score stays in [-1, +1]. Returns None if every entry is None or the
    total participating weight is zero.

    Example (ternary OSDI across measured equations):

        entries = [
            (encode_ternary(sid_status),  0.30),
            (encode_ternary(msi_status),  0.20),
            (encode_ternary(isr_status),  0.20),
            (encode_ternary(bsc_status),  0.15),
            (encode_ternary(mm_status),   0.15),
        ]
        score = weighted_ternary_score(entries)
        # +1 = all equations ABOVE threshold (max dependence)
        #  0 = balanced / WITHIN
        # -1 = all BELOW threshold
    """
    total_weight = 0.0
    weighted_sum = 0.0
    for ternary, weight in entries:
        if ternary is None:
            continue
        total_weight += weight
        weighted_sum += ternary * weight
    if total_weight == 0.0:
        return None
    return weighted_sum / total_weight


# ---------------------------------------------------------------------------
# TIER 2: PRIMITIVE -> PARADIGM REGISTRY
# ---------------------------------------------------------------------------
# Declares which Math-Econ primitives natively support which alternative
# paradigms beyond BINARY. Defaults installed in DEFAULT_REGISTRY below
# describe what's available today; new primitives register via
# `registry.register(name, [paradigms])`.
# ---------------------------------------------------------------------------


class ComputeParadigmRegistry:
    """Bidirectional index of Math-Econ primitives to compute paradigms."""

    _instance: Optional["ComputeParadigmRegistry"] = None

    def __init__(self) -> None:
        self._by_primitive: Dict[str, List[ComputeParadigm]] = {}

    @classmethod
    def instance(cls) -> "ComputeParadigmRegistry":
        """Return the module-level singleton, building it lazily."""
        if cls._instance is None:
            cls._instance = cls()
            _install_defaults(cls._instance)
        return cls._instance

    def register(self, primitive: str,
                 paradigms: List[ComputeParadigm]) -> None:
        """Declare that `primitive` supports `paradigms`. BINARY is always
        implicit (everything supports standard float arithmetic) and is
        added automatically if omitted."""
        seen: List[ComputeParadigm] = []
        if ComputeParadigm.BINARY not in paradigms:
            seen.append(ComputeParadigm.BINARY)
        for p in paradigms:
            if p not in seen:
                seen.append(p)
        self._by_primitive[primitive] = seen

    def paradigms_for(self, primitive: str) -> List[ComputeParadigm]:
        """Paradigms the named primitive supports. Empty list if unknown."""
        return list(self._by_primitive.get(primitive, ()))

    def primitives_for_paradigm(
        self, paradigm: ComputeParadigm
    ) -> List[str]:
        """Primitives that natively support the given paradigm."""
        return sorted(
            name for name, plist in self._by_primitive.items()
            if paradigm in plist
        )

    def primitives(self) -> List[str]:
        return sorted(self._by_primitive.keys())

    def summary(self) -> str:
        """Human-readable matrix: primitives x paradigms."""
        paradigms = list(ComputeParadigm)
        header = "primitive".ljust(32) + "".join(
            p.value.ljust(13) for p in paradigms
        )
        rows = [header, "-" * len(header)]
        for name in self.primitives():
            supported = set(self._by_primitive[name])
            row = name.ljust(32) + "".join(
                ("x" if p in supported else ".").ljust(13) for p in paradigms
            )
            rows.append(row)
        return "\n".join(rows)


def _install_defaults(reg: ComputeParadigmRegistry) -> None:
    """Seed the registry with Math-Econ's current primitives and the
    paradigms they natively support.

    Paradigms listed here are ones the repo can ACTUALLY compute in today:
      - BINARY: always (implicit)
      - TERNARY: primitives whose output is covered by encode_ternary
      - STOCHASTIC: primitives already exercised by Monte Carlo
        sensitivity analysis in data/sensitivity_analysis.py
      - APPROXIMATE: primitives whose output is scope-bounded by
        the calibration/ audit suite

    Paradigms NOT listed (OCTAHEDRAL, ANNEALING, RESERVOIR, QUANTUM) are
    left for future fieldlinks to SOMS / Mandala-Computing / GtBCB.
    """
    P = ComputeParadigm

    # The 13 structural equations (AI/equation_bridge.py).
    # Each produces an EquationResult with a ThresholdStatus → ternary.
    for eq in ("VE_VL", "SID", "RI", "DI", "LWR", "MSI", "BSC", "MM",
               "ISR", "UFR", "ER", "HHI", "SD"):
        reg.register(eq, [P.BINARY, P.TERNARY, P.STOCHASTIC])

    # Composite indices.
    reg.register("OSDI", [P.BINARY, P.TERNARY, P.STOCHASTIC, P.APPROXIMATE])

    # field_system yield / drift.
    reg.register("field_system.effective_yield",
                 [P.BINARY, P.STOCHASTIC])
    reg.register("field_system.drift", [P.BINARY, P.STOCHASTIC])

    # Audits with bounded verdicts.
    reg.register("system_audit.SixSigmaAudit",
                 [P.BINARY, P.STOCHASTIC, P.APPROXIMATE])
    reg.register("calibration.pipeline",
                 [P.BINARY, P.TERNARY, P.APPROXIMATE])

    # Bridge verdicts (ternary via encode_ternary on the band strings).
    reg.register("metabolic_bridge.metabolic_check",
                 [P.BINARY, P.TERNARY])
    reg.register("physics_guard.check",
                 [P.BINARY, P.TERNARY, P.APPROXIMATE])
    reg.register("money_signal_bridge.money_signal_metrics",
                 [P.BINARY, P.STOCHASTIC])
    reg.register("investment_signal_bridge.investment_signal_metrics",
                 [P.BINARY, P.STOCHASTIC])

    # Scope audits (study_scope_audit uses Coupling / Regime / ScopeStatus
    # enums → ternary).
    reg.register("study_scope_audit.StudyScopeAudit",
                 [P.BINARY, P.TERNARY, P.APPROXIMATE])
