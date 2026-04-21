# money_signal_bridge.py
# Defensive bridge: Math-Econ -> JinnZ2/metabolic-accounting /money_signal/ (CC0).
#
# Companion to audit/metabolic_bridge.py. Shares the same discovery logic:
# probe a few conventional locations for a metabolic-accounting checkout,
# set _HAS_MONEY_SIGNAL = False if it can't be found. Every helper returns
# None in the False case so consumers can wire the call in unconditionally.
#
# To make the bridge active, place a checkout adjacent to this repo:
#   <parent>/metabolic-accounting/    (default git clone name)
# or vendor a snapshot inside this repo:
#   <repo_root>/metabolic_accounting/
#
# What this bridge does and does not import:
#   - imports:  money_signal.dimensions, money_signal.coupling (leaf modules,
#               zero sys.path mutation, no term_audit dependency).
#   - skips:    money_signal.accounting_bridge, which mutates sys.path at
#               import time and hard-imports term_audit.* (activating it
#               would silently make our imports depend on term_audit/ being
#               present, which is outside this bridge's contract).
#
# Returned metrics are the three raw primitives that feed signal_quality
# upstream (minsky_coefficient, coupling_magnitude, has_sign_flips). We do
# NOT reimplement the signal_quality formula here — downstream can call the
# upstream `accounting_bridge.signal_quality(ctx)` directly when it has
# term_audit available, or interpret the three primitives on its own terms.
#
# Pinned upstream version:
#   repo:   https://github.com/JinnZ2/metabolic-accounting
#   commit: 09382a66ce6ee63d84038c8ee35a1fbc28cda58d
#   date:   2026-04-21
# To upgrade, fetch the new HEAD, re-run `python tests/test_bridges.py` with
# that checkout in place, and bump UPSTREAM_PINNED_COMMIT below.

import os
import sys
from typing import Any, Dict, Optional

UPSTREAM_PINNED_COMMIT = "09382a66ce6ee63d84038c8ee35a1fbc28cda58d"
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
    from money_signal.coupling import (  # type: ignore
        coupling_magnitude,
        has_sign_flips,
        minsky_coefficient,
    )
    _HAS_MONEY_SIGNAL = True
except Exception:
    _HAS_MONEY_SIGNAL = False


def default_context() -> Optional[Any]:
    """Build a neutral `DimensionalContext` for callers that don't need
    to vary the six dimensions themselves. Represents a modern digital-
    money institutional economy in a healthy state — the baseline against
    which `minsky_coefficient` etc. are scaled upstream.

    Returns None when money_signal is not importable.
    """
    if not _HAS_MONEY_SIGNAL:
        return None
    return DimensionalContext(
        temporal=TemporalScope.SEASONAL,
        cultural=CulturalScope.INSTITUTIONAL,
        attribution=AttributedValue.STATE_ENFORCED,
        observer=ObserverPosition.TOKEN_HOLDER_DEEP,
        substrate=Substrate.DIGITAL,
        state=StateRegime.HEALTHY,
    )


def money_signal_metrics(ctx: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    """Return the three raw money-signal primitives for a given context.

        {"minsky": float,
         "magnitude": float,
         "has_sign_flips": bool}

    When `ctx` is None, uses `default_context()`. Returns None when
    money_signal is not importable.

    These are the same three primitives that upstream's
    `accounting_bridge.signal_quality` collapses into a [0, 1] score.
    Exposing them raw rather than collapsed avoids a dependency on
    `term_audit/` and gives callers more information than a single float.
    """
    if not _HAS_MONEY_SIGNAL:
        return None
    if ctx is None:
        ctx = default_context()
    return {
        "minsky": minsky_coefficient(ctx),
        "magnitude": coupling_magnitude(ctx),
        "has_sign_flips": has_sign_flips(ctx),
    }
