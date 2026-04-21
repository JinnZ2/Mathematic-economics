# investment_signal_bridge.py
# Defensive bridge: Math-Econ -> JinnZ2/metabolic-accounting /investment_signal/ (CC0).
#
# Companion to audit/money_signal_bridge.py. Shares the same discovery
# logic: probe a few conventional locations for a metabolic-accounting
# checkout, set _HAS_INVESTMENT_SIGNAL = False if it can't be found.
# Every helper returns None in the False case so consumers can wire the
# call in unconditionally.
#
# To make the bridge active, place a checkout adjacent to this repo:
#   <parent>/metabolic-accounting/    (default git clone name)
# or vendor a snapshot inside this repo:
#   <repo_root>/metabolic_accounting/
#
# History note: at earlier upstream commits investment_signal had no
# __init__.py and used relative parent-package imports, so it was not
# importable without a shim. At the pinned commit below, upstream uses
# absolute imports (`from money_signal.coupling import ...`) and has a
# normal __init__.py, so the bridge pattern is identical to the other
# flat-import bridges (no shim needed).
#
# Pinned upstream version:
#   repo:   https://github.com/JinnZ2/metabolic-accounting
#   commit: 437e8551634ed33a613cdb41c41f28a51136eec7
#   date:   2026-04-21
# To upgrade, fetch the new HEAD, re-run `python tests/test_bridges.py`
# with that checkout in place, and bump UPSTREAM_PINNED_COMMIT below.

import os
import sys
from typing import Any, Dict, Optional

UPSTREAM_PINNED_COMMIT = "437e8551634ed33a613cdb41c41f28a51136eec7"
UPSTREAM_PINNED_DATE = "2026-04-21"

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_CANDIDATES = (
    os.path.join(_REPO_ROOT, "metabolic_accounting"),
    os.path.abspath(os.path.join(_REPO_ROOT, "..", "metabolic-accounting")),
    os.path.abspath(os.path.join(_REPO_ROOT, "..", "metabolic_accounting")),
)
for _p in _CANDIDATES:
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
        break

try:
    from money_signal.dimensions import (  # type: ignore
        AttributedValue,
        CulturalScope,
        DimensionalContext,
        ObserverPosition,
        StateRegime,
        Substrate,
        TemporalScope,
    )
    from investment_signal.dimensions import (  # type: ignore
        DerivativeDistance,
        InvestmentAttribution,
        InvestmentContext,
        InvestmentSubstrate,
        TimeBinding,
    )
    from investment_signal.substrate_vectors import SubstrateVector  # type: ignore
    from investment_signal.coupling import (  # type: ignore
        assemble_investment_signal,
        signal_failure_count,
        signal_failure_reasons,
    )
    _HAS_INVESTMENT_SIGNAL = True
except Exception:
    _HAS_INVESTMENT_SIGNAL = False


def default_money_context() -> Optional[Any]:
    """Neutral `DimensionalContext` — modern digital-money institutional
    economy in a healthy state. Matches `money_signal_bridge.default_context`
    so both bridges see the same baseline.

    Returns None when investment_signal is not importable.
    """
    if not _HAS_INVESTMENT_SIGNAL:
        return None
    return DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_DEEP,
        substrate=Substrate.DIGITAL,
        state=StateRegime.HEALTHY,
    )


def default_investment_context(money_ctx: Optional[Any] = None) -> Optional[Any]:
    """Neutral `InvestmentContext` — direct (not derivative-layered)
    productive-capacity investment at seasonal time-binding. When
    `money_ctx` is None, uses `default_money_context()`.

    Returns None when investment_signal is not importable.
    """
    if not _HAS_INVESTMENT_SIGNAL:
        return None
    if money_ctx is None:
        money_ctx = default_money_context()
    return InvestmentContext(
        money_context=money_ctx,
        attribution=InvestmentAttribution.PRODUCTIVE_CAPACITY,
        derivative_distance=DerivativeDistance.DIRECT,
        time_binding=TimeBinding.SEASONAL,
    )


def _money_only_vector(amount: float) -> Optional[Any]:
    """Build a SubstrateVector with MONEY = amount and zeros in the other
    six substrates. The length-7 assertion in upstream's
    `validate_vector_storage` requires every substrate to appear."""
    if not _HAS_INVESTMENT_SIGNAL:
        return None
    return SubstrateVector.from_dict({
        **{s: 0.0 for s in InvestmentSubstrate},
        InvestmentSubstrate.MONEY: float(amount),
    })


def investment_signal_metrics(
    input_money: float,
    expected_output_money: float,
    ctx: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    """Run investment-signal assembly for a money-only investment and
    return the fields most useful for judgment.

    Constructs two SubstrateVectors with MONEY set to the input/output
    amounts (zeros elsewhere), assembles an InvestmentSignal via upstream,
    and returns a plain dict:

        time_binding_integrity            float   [0, 1]
        derivative_signal_reliability     float   [0, 1]
        substrate_visibility_at_distance  float   [0, 1]
        cascade_coupling_at_distance      float   [0, 1]
        reverse_causation_at_distance     float   [0, 1]
        money_minsky                      float
        money_magnitude                   float
        money_sign_flips                  bool
        money_near_collapse               bool
        is_financialized                  bool
        substrate_invisible               bool
        liquidity_illusion                bool
        infrastructure_depreciation_trap  bool
        substrate_abstraction_breakdown_any bool
        dependency_broken                 bool
        failure_count                     int
        failure_reasons                   list[str]

    Returns None when investment_signal is not importable.

    For investments with non-money substrate mixes (e.g. labor + time +
    attention → productive capacity), callers should call upstream
    `investment_signal.coupling.assemble_investment_signal` directly with
    custom SubstrateVectors — this helper only covers the common
    money-only case.
    """
    if not _HAS_INVESTMENT_SIGNAL:
        return None
    if ctx is None:
        ctx = default_investment_context()
    in_vec = _money_only_vector(input_money)
    out_vec = _money_only_vector(expected_output_money)
    sig = assemble_investment_signal(in_vec, out_vec, ctx)
    return {
        "time_binding_integrity": sig.time_binding_integrity,
        "derivative_signal_reliability": sig.derivative_signal_reliability,
        "substrate_visibility_at_distance": sig.substrate_visibility_at_distance,
        "cascade_coupling_at_distance": sig.cascade_coupling_at_distance,
        "reverse_causation_at_distance": sig.reverse_causation_at_distance,
        "money_minsky": sig.money_minsky,
        "money_magnitude": sig.money_magnitude,
        "money_sign_flips": sig.money_sign_flips,
        "money_near_collapse": sig.money_near_collapse,
        "is_financialized": sig.is_financialized,
        "substrate_invisible": sig.substrate_invisible,
        "liquidity_illusion": sig.liquidity_illusion,
        "infrastructure_depreciation_trap": sig.infrastructure_depreciation_trap,
        "substrate_abstraction_breakdown_any": sig.substrate_abstraction_breakdown_any,
        "dependency_broken": sig.dependency_broken,
        "failure_count": signal_failure_count(sig),
        "failure_reasons": list(signal_failure_reasons(sig)),
    }
